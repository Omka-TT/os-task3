#!/usr/bin/env python3
"""ptree.py - дерево процессов текущего пользователя по данным /proc (без ps)."""
import os
import sys


def read_status(pid):
    """Читает /proc/<pid>/status в словарь. None, если процесс уже исчез."""
    info = {}
    try:
        with open(f"/proc/{pid}/status") as f:
            for line in f:
                key, _, value = line.partition(":")
                info[key] = value.strip()
    except (FileNotFoundError, ProcessLookupError, PermissionError):
        return None
    return info


def collect(uid):
    """Собирает процессы указанного пользователя: {pid: {...}}."""
    procs = {}
    for entry in os.listdir("/proc"):
        if not entry.isdigit():
            continue
        pid = int(entry)
        st = read_status(pid)
        if st is None or "Uid" not in st:
            continue
        if int(st["Uid"].split()[0]) != uid:  # первое число - real UID
            continue
        procs[pid] = {
            "name": st.get("Name", "?"),
            "state": st.get("State", "?")[:1],  # R, S, D, Z, T ...
            "ppid": int(st.get("PPid", 0)),
            "rss_kb": int(st.get("VmRSS", "0 kB").split()[0]),  # у зомби VmRSS нет -> 0
        }
    return procs


def main():
    procs = collect(os.getuid())

    children = {}
    for pid, p in procs.items():
        children.setdefault(p["ppid"], []).append(pid)

    # корни: те, чей родитель не принадлежит текущему пользователю
    roots = sorted(pid for pid, p in procs.items() if p["ppid"] not in procs)

    def show(pid, depth):
        p = procs[pid]
        print(f"{'  ' * depth}{p['name']}  PID={pid}  state={p['state']}  RSS={p['rss_kb']} kB")
        for child in sorted(children.get(pid, [])):
            show(child, depth + 1)

    for root in roots:
        show(root, 0)


if __name__ == "__main__":
    sys.exit(main())
