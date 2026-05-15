# ============================================
# Local review pipeline runner (menu)
# Run from: review/70 scripts/  or review project root
# ============================================

import os
import subprocess
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)

STEPS = [
    ("1", "Query generator (WoS + Scopus)", "WoS_Scopus_query.py", True),
    ("2", "Merge & classify RIS (PRISMA)", "merge_and_classify.py", False),
    ("3", "Screening & classification", "screening_and_deep_classify.py", False),
    ("4", "Extraction templates", "extraction_templ.py", False),
    ("5", "Zotero → Excel sync (keys + notes)", "zotero_sync.py", True),
    ("6", "Install / check dependencies", None, False),
]

FOLDERS = [
    ("00 search", "Search queries"),
    ("10 data_raw", "Raw RIS exports"),
    ("20 data_clean", "Merged / clean records"),
    ("30 screening", "Screening outputs"),
    ("40 extraction", "Extraction templates"),
    ("60 prisma", "PRISMA copies (if used)"),
]


def python_exe() -> str:
    return sys.executable


def run_script(name: str) -> int:
    path = os.path.join(script_dir, name)
    if not os.path.isfile(path):
        print(f"[ERROR] Missing: {path}")
        return 1
    print(f"\n>>> Running {name}\n")
    return subprocess.call([python_exe(), path], cwd=script_dir)


def check_deps() -> None:
    req = os.path.join(script_dir, "requirements.txt")
    print(f"\n>>> pip install -r {req}\n")
    subprocess.call([python_exe(), "-m", "pip", "install", "-r", req])


def open_folder(rel: str) -> None:
    path = os.path.join(project_root, rel)
    if not os.path.isdir(path):
        print(f"[ERROR] Folder not found: {path}")
        return
    if sys.platform == "win32":
        os.startfile(path)  # noqa: S606
    else:
        subprocess.call(["xdg-open", path])


def print_menu() -> None:
    print("\n" + "=" * 50)
    print("  SYSTEMATIC REVIEW — local runner")
    print(f"  Project: {project_root}")
    print("=" * 50)
    print("\nPipeline steps:")
    for key, label, _, interactive in STEPS:
        tag = " (interactive)" if interactive else ""
        print(f"  {key}  {label}{tag}")
    print("\nFolders:")
    for key, (_, label) in enumerate(FOLDERS, start=10):
        print(f"  {key}  Open {label}")
    print("\n  0  Exit")


def main() -> None:
    while True:
        print_menu()
        choice = input("\nChoice: ").strip()

        if choice == "0":
            break

        if choice == "6":
            check_deps()
            continue

        step = next((s for s in STEPS if s[0] == choice), None)
        if step:
            _, _, script, _ = step
            if script:
                run_script(script)
            continue

        if choice.isdigit() and 10 <= int(choice) < 10 + len(FOLDERS):
            open_folder(FOLDERS[int(choice) - 10][0])
            continue

        print("[ERROR] Unknown choice.")


if __name__ == "__main__":
    main()
