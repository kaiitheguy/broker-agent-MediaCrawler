# tools/run_with_env.py
import os, sys, subprocess, argparse, textwrap

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max_items", type=int, default=None)
    ap.add_argument("rest", nargs="*")
    args = ap.parse_args()

    # 让 MediaCrawler 只抓 N 条（该项目支持这个 env）
    if args.max_items:
        os.environ["XHS_SPIDER_LIMIT"] = str(args.max_items)

    # 注入 Playwright 的环境设置，供我们猴补使用
    os.environ.setdefault("XHS_UA", "")
    os.environ.setdefault("XHS_TIMEZONE", "Asia/Shanghai")
    os.environ.setdefault("XHS_LOCALE", "zh-CN")
    # XHS_PROXY_URL 可为空
    os.environ.setdefault("XHS_PROXY_URL", "")

    # 通过 sitecustomize 注入猴子补丁（不改项目源码）
    sitecustomize = textwrap.dedent(r"""
    import os
    from playwright.async_api import chromium

    _orig = chromium.launch_persistent_context

    async def _patched_launch_persistent_context(*args, **kwargs):
        # 代理
        proxy = os.environ.get("XHS_PROXY_URL", "").strip()
        if proxy:
            kwargs.setdefault("proxy", {"server": proxy})

        # UA / locale / timezone
        ua = os.environ.get("XHS_UA", "").strip()
        if ua:
            kwargs.setdefault("user_agent", ua)
        kwargs.setdefault("locale", os.environ.get("XHS_LOCALE", "zh-CN"))
        kwargs.setdefault("timezone_id", os.environ.get("XHS_TIMEZONE", "Asia/Shanghai"))
        return await _orig(*args, **kwargs)

    chromium.launch_persistent_context = _patched_launch_persistent_context
    """).strip()

    # 写入临时 sitecustomize 并让 Python 加载
    tmpdir = os.getcwd()
    sc_path = os.path.join(tmpdir, "sitecustomize.py")
    with open(sc_path, "w", encoding="utf-8") as f:
        f.write(sitecustomize)

    # 执行 throttle 脚本
    env = os.environ.copy()
    subprocess.check_call([sys.executable, "throttle_xhs.py"], env=env)

if __name__ == "__main__":
    main()
