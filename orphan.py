#!/usr/bin/env python3
"""orphan.py - воспроизводит сироту и показывает, кто её усыновил."""
import os
import subprocess
import sys
import time


def flush():
    sys.stdout.flush()


print(f"[main] PID={os.getpid()}")
flush()

mid = os.fork()
if mid == 0:
    # "родитель" будущей сироты
    orphan = os.fork()
    if orphan == 0:
        # сирота
        print(f"[сирота] PID={os.getpid()}, PPID до смерти родителя = {os.getppid()}")
        flush()
        time.sleep(2)  # за это время родитель умрёт
        new_ppid = os.getppid()
        print(f"[сирота] PPID после = {new_ppid}")
        print("[сирота] кто это:")
        flush()
        subprocess.run(["ps", "-o", "pid,ppid,stat,args", "-p", str(new_ppid)])
        os._exit(0)
    print(f"[родитель] PID={os.getpid()} создал сироту {orphan} и сразу завершается")
    flush()
    time.sleep(1)
    os._exit(0)

os.waitpid(mid, 0)  # main убирает "родителя", чтобы не было зомби
time.sleep(4)       # ждём сироту, чтобы вывод не потерялся и она не осталась в фоне

