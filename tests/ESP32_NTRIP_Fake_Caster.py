#!/usr/bin/env python3
import argparse
import asyncio
import base64
import os
import random
import time
from dataclasses import dataclass
from typing import List, Optional, Tuple

# ----------------------------
# Caster behavior configuration
# ----------------------------

@dataclass
class StreamPlan:
    # HTTP behavior
    status_line: str = "ICY 200 OK\r\n"
    extra_headers: List[str] = None  # e.g. ["Server: FakeCaster\r\n", "Date: ...\r\n"]
    header_delay_ms: int = 0         # delay before sending headers (simulate slow header)
    body_delay_ms: int = 0           # delay before streaming starts

    # Streaming behavior
    rtcm_path: Optional[str] = None
    loop_stream: bool = True
    inter_chunk_delay_ms: int = 0

    # Segmentation control
    # If provided, send these chunk sizes repeatedly (e.g. [1,1,2,5,13])
    chunk_sizes: Optional[List[int]] = None
    # Otherwise, random chunk sizes in [min,max]
    random_chunk_range: Tuple[int, int] = (64, 256)

    # Fault injection
    stall_after_bytes: Optional[int] = None  # stop sending but keep socket open
    drop_after_bytes: Optional[int] = None   # close socket abruptly after N bytes
    junk_prefix: bytes = b""                 # prepend junk before stream
    corrupt_every_n: Optional[int] = None    # flip a byte every N chunks (not CRC-aware)


def b64_basic(user: str, pw: str) -> str:
    return base64.b64encode(f"{user}:{pw}".encode()).decode()


def load_bytes(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read()


# ----------------------------
# Core server
# ----------------------------

class FakeCaster:
    def __init__(self, plan: StreamPlan, expect_mount: Optional[str], expect_auth: Optional[str]):
        self.plan = plan
        self.expect_mount = expect_mount
        self.expect_auth = expect_auth

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        peer = writer.get_extra_info("peername")
        try:
            req = await self._read_http_request(reader)
            method, path, headers = self._parse_request(req)

            # Basic request validation / routing
            if self.expect_mount and path != f"/{self.expect_mount}":
                await self._send_response(writer, "HTTP/1.0 404 Not Found\r\n", ["\r\n"])
                writer.close()
                await writer.wait_closed()
                print(f"[{peer}] 404 mount mismatch: got path={path}")
                return

            if self.expect_auth:
                auth = headers.get("authorization", "")
                if auth.strip() != self.expect_auth.strip():
                    await self._send_response(writer, "HTTP/1.0 401 Unauthorized\r\n", ["\r\n"])
                    writer.close()
                    await writer.wait_closed()
                    print(f"[{peer}] 401 auth mismatch: got auth={auth!r}")
                    return

            # Send success / configured status + headers
            await self._send_response(writer, self.plan.status_line, self.plan.extra_headers or [])

            # Optional delay before streaming body
            if self.plan.body_delay_ms:
                await asyncio.sleep(self.plan.body_delay_ms / 1000.0)

            # Stream
            await self._stream_bytes(writer)

        except asyncio.IncompleteReadError:
            print(f"[{peer}] client disconnected early")
        except Exception as e:
            print(f"[{peer}] error: {e}")
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass

    async def _read_http_request(self, reader: asyncio.StreamReader) -> bytes:
        # Read until blank line (HTTP request headers end)
        data = b""
        while True:
            line = await reader.readline()
            if not line:
                break
            data += line
            if line in (b"\r\n", b"\n"):
                break
        return data

    def _parse_request(self, req: bytes):
        text = req.decode(errors="replace")
        lines = [ln.strip("\r") for ln in text.split("\n") if ln.strip("\r")]
        if not lines:
            raise ValueError("empty request")
        request_line = lines[0].strip()
        parts = request_line.split()
        if len(parts) < 2:
            raise ValueError(f"bad request line: {request_line}")
        method, path = parts[0], parts[1]
        headers = {}
        for ln in lines[1:]:
            if ":" in ln:
                k, v = ln.split(":", 1)
                headers[k.strip().lower()] = v.strip()
        return method, path, headers

    async def _send_response(self, writer: asyncio.StreamWriter, status_line: str, headers: List[str]):
        if self.plan.header_delay_ms:
            await asyncio.sleep(self.plan.header_delay_ms / 1000.0)

        # Ensure CRLF line endings
        if not status_line.endswith("\r\n"):
            status_line += "\r\n"
        writer.write(status_line.encode())

        for h in headers:
            if not h.endswith("\r\n"):
                h += "\r\n"
            writer.write(h.encode())

        # Header terminator
        writer.write(b"\r\n")
        await writer.drain()

    async def _stream_bytes(self, writer: asyncio.StreamWriter):
        if self.plan.rtcm_path:
            payload = load_bytes(self.plan.rtcm_path)
        else:
            payload = b""

        # Optional junk before stream (useful to test receiver robustness / your health logic)
        stream = self.plan.junk_prefix + payload

        sent = 0
        chunk_index = 0

        # When no payload, just idle
        if not stream:
            while True:
                await asyncio.sleep(1.0)

        while True:
            # Stall injection
            if self.plan.stall_after_bytes is not None and sent >= self.plan.stall_after_bytes:
                print(f"[stream] STALL after {sent} bytes (keeping socket open)")
                while True:
                    await asyncio.sleep(10.0)

            # Drop injection
            if self.plan.drop_after_bytes is not None and sent >= self.plan.drop_after_bytes:
                print(f"[stream] DROP after {sent} bytes")
                return

            # Determine next chunk
            if self.plan.chunk_sizes:
                size = self.plan.chunk_sizes[chunk_index % len(self.plan.chunk_sizes)]
            else:
                lo, hi = self.plan.random_chunk_range
                size = random.randint(lo, hi)

            # Slice chunk
            if sent >= len(stream):
                if self.plan.loop_stream:
                    sent = 0
                else:
                    return

            chunk = stream[sent:sent + size]

            # Corrupt injection (not CRC aware; useful for CRC-error behavior)
            if self.plan.corrupt_every_n and (chunk_index % self.plan.corrupt_every_n == 0) and chunk:
                b = bytearray(chunk)
                b[len(b)//2] ^= 0xFF
                chunk = bytes(b)

            writer.write(chunk)
            await writer.drain()

            sent += len(chunk)
            chunk_index += 1

            if self.plan.inter_chunk_delay_ms:
                await asyncio.sleep(self.plan.inter_chunk_delay_ms / 1000.0)


def build_plan(mode: str, rtcm_path: Optional[str]) -> StreamPlan:
    # Default: OK stream, mild segmentation
    if mode == "ok":
        return StreamPlan(
            status_line="ICY 200 OK\r\n",
            extra_headers=["Server: FakeCaster\r\n", "Content-Type: gnss/data\r\n"],
            rtcm_path=rtcm_path,
            chunk_sizes=[128, 17, 3, 64, 256],  # deterministic segmentation torture
            inter_chunk_delay_ms=0,
        )

    if mode == "ok_headers":
        # Lots of headers to validate header draining behavior
        return StreamPlan(
            status_line="HTTP/1.0 200 OK\r\n",
            extra_headers=[
                "Server: FakeCaster\r\n",
                "Date: Tue, 03 Feb 2026 09:39:54 GMT-05:00\r\n",
                "X-Debug: header-drain-test\r\n",
            ],
            rtcm_path=rtcm_path,
            chunk_sizes=[64, 64, 64],
        )

    if mode == "unauth":
        return StreamPlan(status_line="HTTP/1.0 401 Unauthorized\r\n")

    if mode == "nomount":
        return StreamPlan(status_line="HTTP/1.0 404 Not Found\r\n")

    if mode == "servererr":
        return StreamPlan(status_line="HTTP/1.0 500 Internal Server Error\r\n")

    if mode == "stall":
        return StreamPlan(
            status_line="ICY 200 OK\r\n",
            extra_headers=["Server: FakeCaster\r\n"],
            rtcm_path=rtcm_path,
            stall_after_bytes=1024,  # stall after some data
        )

    if mode == "drop":
        return StreamPlan(
            status_line="ICY 200 OK\r\n",
            extra_headers=["Server: FakeCaster\r\n"],
            rtcm_path=rtcm_path,
            drop_after_bytes=1024,  # close after some data
        )

    if mode == "junk":
        return StreamPlan(
            status_line="ICY 200 OK\r\n",
            extra_headers=["Server: FakeCaster\r\n"],
            rtcm_path=rtcm_path,
            junk_prefix=b"THIS_IS_JUNK_BEFORE_RTCM\r\n",
            chunk_sizes=[10, 10, 10, 200],
        )

    if mode == "corrupt":
        return StreamPlan(
            status_line="ICY 200 OK\r\n",
            extra_headers=["Server: FakeCaster\r\n"],
            rtcm_path=rtcm_path,
            corrupt_every_n=5,
            chunk_sizes=[200, 200, 200],
        )

    raise ValueError(f"unknown mode: {mode}")


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=2101)
    ap.add_argument("--mode", default="ok",
                    choices=["ok", "ok_headers", "unauth", "nomount", "servererr", "stall", "drop", "junk", "corrupt"])
    ap.add_argument("--mount", default=None, help="Expected mount (without leading /)")
    ap.add_argument("--user", default=None)
    ap.add_argument("--password", default=None)
    ap.add_argument("--rtcm", default=None, help="Path to binary RTCM capture to replay")

    args = ap.parse_args()

    expect_auth = None
    if args.user is not None and args.password is not None:
        expect_auth = f"Basic {b64_basic(args.user, args.password)}"

    plan = build_plan(args.mode, args.rtcm)
    caster = FakeCaster(plan, expect_mount=args.mount, expect_auth=expect_auth)

    server = await asyncio.start_server(caster.handle_client, args.host, args.port)
    addrs = ", ".join(str(sock.getsockname()) for sock in server.sockets)
    print(f"[FakeCaster] listening on {addrs} mode={args.mode}")

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())