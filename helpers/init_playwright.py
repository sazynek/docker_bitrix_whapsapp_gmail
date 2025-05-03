import json
import os

import aiofiles
from fake_useragent import FakeUserAgent
from playwright.async_api import BrowserContext, Page, Playwright

from helpers.register import register


async def initial_playwright(  # type:ignore
    playwright: Playwright, *, headless: bool = True
) -> tuple[Page, BrowserContext]:
    browser = await playwright.chromium.launch(
        headless=headless, args=["--start-maximized"]
    )
    context = await browser.new_context(
        no_viewport=True,
        user_agent=FakeUserAgent().chrome,
        is_mobile=False,
        screen={"height": 1920, "width": 1080},
    )

    page = await context.new_page()
    if os.path.exists("main_cook.json"):
        async with aiofiles.open("main_cook.json", "r", encoding="utf-8") as fr:
            cookies_file = json.loads(await fr.read())
            # print(type(cookies_file))
            await context.add_cookies(cookies_file)
    else:
        print("NEW REGISTER")

        await context.clear_cookies()
        await register(page, context)
    # print('PAGE: ',page)
    return page, context
