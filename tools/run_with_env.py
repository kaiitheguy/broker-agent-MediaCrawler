# tools/run_with_env.py
import os, sys, subprocess, textwrap

def main():
    # 让爬虫只抓 N 条（来自 CI 输入）
    max_items = os.environ.get("MAX_ITEMS")
    if max_items:
        os.environ["XHS_SPIDER_LIMIT"] = max_items

    # 默认指纹（可被 env 覆盖）
    os.environ.setdefault("XHS_UA", "")
    os.environ.setdefault("XHS_LOCALE", "en-US")
    os.environ.setdefault("XHS_TIMEZONE", "America/New_York")
    os.environ.setdefault("XHS_PROXY_URL", "")  # 可为空

    # 通过 sitecustomize 猴补 Playwright
    sitecustomize = textwrap.dedent(r"""
    import os
    from playwright.async_api import chromium

    _orig = chromium.launch_persistent_context

    async def _patched_launch_persistent_context(*args, **kwargs):
        proxy = os.environ.get("XHS_PROXY_URL", "").strip()
        if proxy:
            kwargs.setdefault("proxy", {"server": proxy})

        ua = os.environ.get("XHS_UA", "").strip()
        if ua:
            kwargs.setdefault("user_agent", ua)

        kwargs.setdefault("locale", os.environ.get("XHS_LOCALE", "en-US"))
        kwargs.setdefault("timezone_id", os.environ.get("XHS_TIMEZONE", "America/New_York"))
        return await _orig(*args, **kwargs)

    chromium.launch_persistent_context = _patched_launch_persistent_context
    """).strip()

    with open("sitecustomize.py", "w", encoding="utf-8") as f:
        f.write(sitecustomize)

    # 执行你现有的节流脚本
    env = os.environ.copy()
    subprocess.check_call([sys.executable, "throttle_xhs.py"], env=env)

if __name__ == "__main__":
    main()
