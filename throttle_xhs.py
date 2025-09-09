import os
import sys
import time
import random
import subprocess
import argparse

KEYWORDS = ["美股", "特斯拉", "纳指"]

LOGIN_TYPE = os.getenv("XHS_LOGIN_TYPE", "cookie")
SAVE_DATA_OPTION = os.getenv("XHS_SAVE", "sqlite")
COOKIES_PATH = os.getenv("XHS_COOKIES_PATH", "").strip()

def run_one_keyword(kw: str, max_items: int = None) -> bool:
    args = [
        sys.executable, "main.py",
        "--platform", "xhs",
        "--lt", LOGIN_TYPE,
        "--type", "search",
        "--keywords", kw,
        "--save_data_option", SAVE_DATA_OPTION,
    ]
    if COOKIES_PATH:
        args += ["--cookies", COOKIES_PATH]
    if max_items:
        args += ["--start", "0", "--end", str(max_items)]  # MediaCrawler 支持 start/end

    print("CMD:", " ".join(args))
    ret = subprocess.run(args)
    return ret.returncode == 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--max_items", type=int, default=None, help="Limit number of items per keyword")
    args = parser.parse_args()

    for kw in KEYWORDS:
        success = run_one_keyword(kw, args.max_items)
        sleep_time = random.randint(5, 10)  # 测试时缩短
        print(f"[{kw}] done={success}, sleep {sleep_time}s…")
        time.sleep(sleep_time)
    print("Gentle crawl finished.")
