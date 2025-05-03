from asyncio import sleep

from playwright.async_api import Page


async def scroller(page: Page) -> None:
    scroll_time = 6
    while scroll_time >= 0:
        scroll_time -= 1
        await page.evaluate("window.scrollBy(0, 1000)")
        await sleep(0.3)
