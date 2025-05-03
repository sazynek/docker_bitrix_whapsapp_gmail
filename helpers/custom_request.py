import asyncio
import re

import numpy as np
from playwright.async_api import BrowserContext, Page

from helpers.custom_logger import logs
from sys_argv.sys_argv import CUSTOM_REQUEST_STATE, CUSTOM_REQUEST_URLS


async def custom_request(page: Page, context: BrowserContext) -> np.ndarray:
    pattern = r'(?<=url\(")\/\/(?!=")[\w\/:\-\s\.]*'
    # print(f"start custom request:{CUSTOM_REQUEST_URLS}")
    logs.info(f"start custom request:{CUSTOM_REQUEST_URLS}")

    if (
        (
            len(CUSTOM_REQUEST_URLS) >= 7
            and ("https" in CUSTOM_REQUEST_URLS or "http" in CUSTOM_REQUEST_URLS)
        )
        and True
        if CUSTOM_REQUEST_STATE.strip().capitalize() == "True"
        else False
    ):

        int_dict: dict = {}
        int_dict["link"] = CUSTOM_REQUEST_URLS

        await page.goto(int_dict["link"])  # type: ignore
        try:
            t = page.locator('h1[data-tid="OverviewTitle"] > img')
            int_dict["title"] = str(await t.get_attribute("alt")) if t else "None"
            if (
                "смотреть" in int_dict["title"].lower()
                and "None" not in int_dict["title"]
            ):
                int_dict["title"] = (
                    int_dict["title"]
                    .lower()
                    .replace("смотреть", "")
                    .strip()
                    .capitalize()
                )
        except Exception as e:
            print(e)
            logs.warn(e, __name__)

        try:
            img = await page.locator(  # type: ignore
                'div[data-tid="ContentBackgroundImage"] > div'
            ).get_attribute("style")
            img = re.search(pattern, str(img), flags=re.IGNORECASE).group() if img else None  # type: ignore
            int_dict["img"] = f"https:{img}" if img and img is not None else "None"
        except Exception as e:
            print(e)
            logs.warn(e, __name__)

        return np.array([(int_dict["title"], int_dict["img"], int_dict["link"])])
    else:
        print("custom request failed")
        raise ValueError(
            "Your urls can't be corrected or you forgot on this functionality"
            f"current state: {CUSTOM_REQUEST_STATE}"
        )
