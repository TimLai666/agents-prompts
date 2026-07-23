#!/usr/bin/env python3
"""
sync.py — 把 AGENTS-content.md 同步到全域設定檔位置。

目標:
  ~/.codex/AGENTS.md
  ~/.claude/CLAUDE.md
  ~/.pi/agent/AGENTS.md

用法:
  python sync.py              同步檔案
  python sync.py --dry-run    預覽變更，不動檔案
  python sync.py --diff       複製前顯示差異
"""

from __future__ import annotations

import argparse
import difflib
import shutil
import sys
from datetime import datetime
from pathlib import Path

# -- ANSI colors (Windows VT100 fallback) ------------------------------------

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
CYAN = "\033[36m"


def _enable_win_vt():
    if sys.platform != "win32":
        return
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
        handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
        mode = ctypes.c_ulong()
        kernel32.GetConsoleMode(handle, ctypes.byref(mode))
        kernel32.SetConsoleMode(handle, mode.value | 0x0004)  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
    except Exception:
        pass


# -- helpers ------------------------------------------------------------------

def normalize(text: str) -> str:
    """去掉結尾空白，統一加一個 newline。"""
    return text.rstrip() + "\n"


def backup(path: Path, dest_dir: Path) -> Path | None:
    """把既有檔案複製一份到 dest_dir，檔名帶時間戳。"""
    if not path.exists():
        return None
    dest_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = dest_dir / f"{path.name}.{ts}.bak"
    shutil.copy2(path, out)
    return out


def diff_lines(src: Path, tgt: Path) -> list[str]:
    """回傳 unified diff 的行列表。"""
    s = normalize(src.read_text("utf-8")).splitlines(keepends=True)
    if not tgt.exists():
        t = []
    else:
        t = normalize(tgt.read_text("utf-8")).splitlines(keepends=True)
    return list(difflib.unified_diff(
        t, s,
        fromfile=str(tgt),
        tofile=str(src),
        lineterm="",
    ))


# -- main sync logic ----------------------------------------------------------

def sync_one(
    source: Path,
    target: Path,
    backup_dir: Path,
    *,
    dry_run: bool,
    show_diff: bool,
) -> str:
    """同步一個檔案。回傳: identical / updated / would_update。"""
    label = f"~/{target.parent.relative_to(Path.home()).as_posix()}/{target.name}"
    print(f"{BOLD}{label}{RESET}")

    src_text = normalize(source.read_text("utf-8"))

    if target.exists() and normalize(target.read_text("utf-8")) == src_text:
        print(f"  {GREEN}≡ 內容相同{RESET}")
        return "identical"

    if show_diff:
        lines = diff_lines(source, target)
        if lines:
            for line in lines:
                if line.startswith("+") and not line.startswith("+++"):
                    print(f"  {GREEN}{line}{RESET}")
                elif line.startswith("-") and not line.startswith("---"):
                    print(f"  {RED}{line}{RESET}")
                else:
                    print(f"  {DIM}{line}{RESET}")
        else:
            print(f"  {YELLOW}→ 需要更新{RESET}")

    if dry_run:
        print(f"  {YELLOW}→ 需要更新（預覽模式，未實際寫入）{RESET}")
        return "would_update"

    bak = backup(target, backup_dir)
    if bak:
        print(f"  {DIM}備份: {bak}{RESET}")

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(src_text, encoding="utf-8")
    print(f"  {GREEN}[OK] 已更新{RESET}")
    return "updated"


# -- entry point ---------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(
        description="同步 AGENTS-content.md 到全域設定檔位置",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--dry-run", action="store_true",
                     help="預覽變更，不實際修改檔案")
    ap.add_argument("--diff", action="store_true",
                     help="複製前顯示差異")
    args = ap.parse_args()

    _enable_win_vt()

    source = Path(__file__).resolve().parent / "AGENTS-content.md"
    if not source.exists():
        print(f"{RED}找不到來源: {source}{RESET}")
        sys.exit(1)

    home = Path.home()
    targets = [
        (home / ".codex" / "AGENTS.md",  home / ".codex" / "backups"),
        (home / ".claude" / "CLAUDE.md", home / ".claude" / "backups"),
        (home / ".pi" / "agent" / "AGENTS.md", home / ".pi" / "agent" / "backups"),
    ]

    print(f"{BOLD}同步 AGENTS-content.md{RESET}")
    print(f"  來源: {source}")
    print()

    results = []
    for target, backup_dir in targets:
        if not target.parent.exists():
            print(f"  {DIM}略過 {target.parent}：該工具未安裝{RESET}")
            print()
            continue
        results.append(sync_one(
            source, target, backup_dir,
            dry_run=args.dry_run,
            show_diff=args.diff,
        ))
        print()

    if args.dry_run and "would_update" in results:
        print(f"{YELLOW}以上為預覽，未實際寫入。移除 --dry-run 執行同步。{RESET}")


if __name__ == "__main__":
    main()
