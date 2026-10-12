#!/usr/bin/env python3
"""cow.py - показывает copy-on-write после fork."""
import gc
import os
import sys

gc.disable()  # чтобы сборщик мусора не трогал страницы и не портил измерение

KEYS = ("Rss", "Pss", "Private_Dirty", "Shared_Dirty", "Shared_Clean", "Private_Clean")


def mem():
    """Метрики текущего процесса из /proc/self/smaps_rollup (в кБ)."""
    r = {}
    with open("/proc/self/smaps_rollup") as f:
        for line in f:
            parts = line.split()
            key = parts[0].rstrip(":")
            if key in KEYS:
                r[key] = int(parts[1])
    return r


def report(label):
    m = mem()
    print(
        f"{label:<34} RSS={m['Rss'] / 1024:7.1f} MB  Pss={m['Pss'] / 1024:7.1f} MB  "
        f"Private_Dirty={m['Private_Dirty'] / 1024:7.1f} MB  "
        f"Shared={(m['Shared_Dirty'] + m['Shared_Clean']) / 1024:7.1f} MB"
    )
    sys.stdout.flush()


data = list(range(3_000_000))  # большой список (~100+ МБ вместе с int-объектами)
report("[родитель] до fork")

pid = os.fork()
if pid == 0:
    report("[ребёнок] сразу после fork")
    for i in range(len(data)):  # меняем весь список -> копируются страницы
        data[i] += 1
    report("[ребёнок] после изменения списка")
    os._exit(0)

os.waitpid(pid, 0)
report("[родитель] после ребёнка")
