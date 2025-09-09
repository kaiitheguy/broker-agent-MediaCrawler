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