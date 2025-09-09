# tools/run_with_env.py
import os, sys, subprocess, textwrap
from urllib.parse import urlparse

def main():
    # 限制抓取条数（workflow input → env → XHS_SPIDER_LIMIT）
    max_items = os.environ.get("MAX_ITEMS")
    if max_items:
        os.environ["XHS_SPIDER_LIMIT"] = max_items

    # 指纹（用你本机的）
    os.environ.setdefault("XHS_UA", "")
    os.environ.setdefault("XHS_LOCALE", "en-US")
    os.environ.setdefault("XHS_TIMEZONE", "America/New_York")

    # 代理优先顺序：URL → 组合 USER+PASS+ENDPOINT
    proxy_url = os.environ.get("XHS_PROXY_URL", "").strip()
    if not proxy_url:
        hp  = os.environ.get("XHS_PROXY_ENDPOINT", "").strip()
        usr = os.environ.get("XHS_PROXY_USER", "").strip()
        pwd = os.environ.get("XHS_PROXY_PASS", "").strip()
        if hp and usr and pwd:
            proxy_url = f"http://{usr}:{pwd}@{hp}"
        elif hp:
            proxy_url = f"http://{hp}"
    os.environ["XHS_PROXY_URL"] = proxy_url  # 可能为空

    # 用 sitecustomize 猴补 Playwright 的 proxy/UA/locale/timezone
    sitecustomize = textwrap.dedent(r"""
    import os
    from urllib.parse import urlparse
    from playwright.async_api import chromium

    _orig = chromium.launch_persistent_context

    async def _patched_launch_persistent_context(*args, **kwargs):
        p = os.environ.get("XHS_PROXY_URL", "").strip()
        if p:
            up = urlparse(p)
            proxy = {"server": f"{up.scheme}://{up.hostname}:{up.port}"}
            if up.username and up.password:
                proxy["username"] = up.username
                proxy["password"] = up.password
            kwargs.setdefault("proxy", proxy)

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

    env = os.environ.copy()
    subprocess.check_call([sys.executable, "throttle_xhs.py"], env=env)

if __name__ == "__main__":
    main()
