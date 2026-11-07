#!/usr/bin/env python3
"""syslog_listen.py - a tiny syslog receiver for Lab 4, Part 2, when you have no SIEM at hand.

Listens on UDP and TCP, prints every message, and appends it to received.log.
Port 514 needs admin rights, so the default is 13379:

  python3 syslog_listen.py                 (UDP and TCP 13379 on this machine only)
  python3 harness.py chat --model ... --syslog 127.0.0.1:13379 --syslog-format cef
"""
import argparse, socket, socketserver, threading, time

OUT = "received.log"
LOCK = threading.Lock()


def show(msg, src, proto):
    line = msg.decode("utf-8", "replace").strip()
    with LOCK:
        print(f"[{time.strftime('%H:%M:%S')} {proto} {src}] {line[:400]}{'...' if len(line) > 400 else ''}", flush=True)
        with open(OUT, "a", encoding="utf-8") as f:
            f.write(line + "\n")


class UDP(socketserver.BaseRequestHandler):
    def handle(self):
        show(self.request[0], self.client_address[0], "udp")


class TCP(socketserver.StreamRequestHandler):
    def handle(self):  # RFC 6587: octet counting ("123 <msg>") or one message per line
        buf = b""
        while True:
            chunk = self.request.recv(65536)
            if not chunk:
                break
            buf += chunk
            while buf:
                head, sp, rest = buf.partition(b" ")
                if sp and head.isdigit() and len(rest) >= int(head):
                    n = int(head)
                    show(rest[:n], self.client_address[0], "tcp")
                    buf = rest[n:]
                elif b"\n" in buf and not head.isdigit():
                    line, _, buf = buf.partition(b"\n")
                    show(line, self.client_address[0], "tcp")
                else:
                    break


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--host", default="127.0.0.1", help="0.0.0.0 to accept other machines (Docker on Linux)")
    ap.add_argument("--port", type=int, default=13379)
    a = ap.parse_args()
    socketserver.ThreadingUDPServer.allow_reuse_address = True
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    u = socketserver.ThreadingUDPServer((a.host, a.port), UDP)
    t = socketserver.ThreadingTCPServer((a.host, a.port), TCP)
    for srv in (u, t):
        threading.Thread(target=srv.serve_forever, daemon=True).start()
    print(f"Listening for syslog on {a.host}:{a.port} (UDP and TCP). Saving to {OUT}. Ctrl-C to stop.", flush=True)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
