#!/usr/bin/env python3
"""runner.py N cmd [args...] - запускает N детей через fork+exec, ждёт всех."""
import os
import sys
import time


def main():
    if len(sys.argv) < 3 or not sys.argv[1].isdigit():
        print(f"Использование: {sys.argv[0]} N команда [аргументы...]")
        return 2

    n = int(sys.argv[1])
    cmd = sys.argv[2:]
    started = {}  # pid -> (номер, время старта)

    sys.stdout.flush()  # иначе буфер продублируется в детях
    for i in range(n):
        t0 = time.monotonic()
        pid = os.fork()
        if pid == 0:
            # ветка ребёнка
            try:
                os.execvp(cmd[0], cmd)  # при успехе сюда уже не вернёмся
            except OSError as e:
                print(f"exec не удался: {cmd[0]}: {e}", file=sys.stderr)
            os._exit(127)  # ОБЯЗАТЕЛЬНО выйти, иначе ребёнок продолжит код родителя
        started[pid] = (i, t0)

    # родитель ждёт всех детей
    for _ in range(n):
        pid, status = os.wait()
        elapsed = time.monotonic() - started[pid][1]
        code = os.waitstatus_to_exitcode(status)  # >=0 код выхода, <0 номер сигнала
        print(f"ребёнок #{started[pid][0]} PID={pid} код={code} время={elapsed:.3f} c")
    return 0


if __name__ == "__main__":
    sys.exit(main())
