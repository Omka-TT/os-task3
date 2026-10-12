#!/usr/bin/env python3
"""zombie.py - воспроизводит зомби и затем убирает его."""
import os
import subprocess
import sys
import time


def ps(*pids):
    sys.stdout.flush()
    subprocess.run(["ps", "-o", "pid,ppid,stat,comm", "-p", ",".join(map(str, pids))])


child = os.fork()
if child == 0:
    print(f"[ребёнок] PID={os.getpid()} завершаюсь сразу")
    sys.stdout.flush()
    os._exit(0)

time.sleep(1)  # ребёнок уже завершился, а мы не вызвали wait
print(f"\n[родитель] PID={os.getpid()}, ребёнок {child} завершён, wait() ещё НЕ вызван:")
ps(os.getpid(), child)  # у ребёнка STAT=Z, comm=python3 <defunct>

os.waitpid(child, 0)  # родитель забирает код возврата, зомби исчезает
print("\n[родитель] после waitpid ребёнка в таблице процессов уже нет:")
ps(os.getpid(), child)

