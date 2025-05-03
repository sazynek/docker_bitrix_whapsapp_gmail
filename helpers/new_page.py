import asyncio
import os
import re
from asyncio import sleep
from hashlib import md5
from typing import Any, Literal

import aiohttp
import numpy as np
from playwright.async_api import BrowserContext, Page

from helpers.check_url_can_parsed import check_url_can_parsed
from helpers.const import DOMAIN
from helpers.create_func import Creator
from helpers.custom_logger import logs
from helpers.custom_request import custom_request
from helpers.scroller import scroller
from sys_argv.sys_argv import (
    CUSTOM_REQUEST_DIRECTORY_PATH,
    CUSTOM_REQUEST_STATE,
    MAIN_DIRECTORY_FOR_ALL_FILES,
    MOVE_CUSTOM_REQUEST_TO_MAIN_DIRECTORY,
)


async def new_page(page: Page, context: BrowserContext) -> None:
    global_list: list = []
    fail: list = []
    success: list = []
    logger: dict[Literal["fail", "success"], list[str]] = {
        "fail": fail,
        "success": success,
    }

    await page.goto(
        "https://hd.kinopoisk.ru/selection/novelties?selectionWindowId=onboarding",
        wait_until="domcontentloaded",
    )
    await sleep(3)
    await scroller(page)
    list_items = await page.locator('div[data-tid="ListItemCard"]').all()
    # print(f"item exist" if len(list_items) > 0 else f"item not exist")
    logs.info(f"item exist" if len(list_items) > 0 else f"item not exist", __name__)
    if list_items and len(list_items) > 0:
        try:
            links = np.array(
                [
                    (
                        await link.locator('a[data-tid="NextLink"]').get_attribute(
                            "aria-label"
                        ),
                        f'https:{await link.locator('img[data-tid="AdaptiveImage"]').get_attribute("src")}',
                        f"{DOMAIN}{await link.locator('a[data-tid="NextLink"]').get_attribute("href")}",
                    )
                    for link in list_items
                    if link is not None
                ]
            )
            links_ = await check_url_can_parsed(links)
            if True if CUSTOM_REQUEST_STATE.strip().capitalize() == "True" else False:
                links_ = await custom_request(page, context)
            for link in links_:
                # if len(global_list) == 4:
                #     break
                link_title = link[0]
                link_img = link[1]
                link_url = link[2]

                assert (
                    link_title is not None
                    and link_img is not None
                    and link_url is not None
                )

                full_inf = await new_page2(
                    page, context, logger, link_url, link_img, link_title
                )
                global_list.append(full_inf)
            pass
        except Exception as e:
            # print(f"links error {e}")
            logs.err(f"links error {e}", __name__)

        finally:
            # print("start create files")
            logs.info("start create files", __name__)

            tasks: list = []
            json_main_data: list[dict] = []
            # print(global_list)
            array = np.array(global_list)
            async with aiohttp.ClientSession() as session:
                for i in array:
                    path_img = i[0]
                    path_json = i[1]
                    json_data = i[2]
                    img = i[3]
                    json_main_data += [json_data]
                    task_json = asyncio.create_task(
                        Creator.create_json(json_data, path_json)
                    )
                    task_img = asyncio.create_task(
                        Creator.load_image(img, session, path_img)
                    )
                    task_url = asyncio.create_task(Creator.create_urls(logger))
                    task_url = asyncio.create_task(
                        Creator.create_main_json(json_main_data)
                    )

                    tasks.append(task_json)
                    tasks.append(task_img)
                    tasks.append(task_url)
                await asyncio.gather(*tasks)
                await Creator.create_main_json_sorted()
        await sleep(4)
        task_xlsx = asyncio.create_task(Creator.create_excel())
        task_xml = asyncio.create_task(Creator.create_xml())
        await asyncio.gather(*[task_xlsx, task_xml])

    else:
        # print("recurse restart")
        logs.warn("recurse restart", __name__)
        raise RecursionError("recurse")


async def new_page2(
    page: Page,
    context: BrowserContext,
    logger: dict[Literal["fail", "success"], list],
    *args: Any,
) -> tuple[str, str, dict, str]:
    global CUSTOM_REQUEST_DIRECTORY_PATH
    json_dict: dict = {}
    link, img, title = args
    if ":" in title:
        title = str(title).replace(":", " - ")
    if "?" in title:
        title = str(title).replace("?", " ")
    json_dict["title"] = title
    json_dict["link"] = link
    json_dict["img"] = img

    # print("current page: ", link)
    logs.info(f"current page: {link}", __name__)
    md_ = md5(str(json_dict["title"]).encode("utf-8")).hexdigest()

    # return
    if (
        str(CUSTOM_REQUEST_DIRECTORY_PATH).strip().endswith("/")
        and len(CUSTOM_REQUEST_DIRECTORY_PATH) > 0
        and CUSTOM_REQUEST_STATE.capitalize().strip() == "True"
    ):
        CUSTOM_REQUEST_DIRECTORY_PATH = (
            str(CUSTOM_REQUEST_DIRECTORY_PATH).replace("/", "").strip()
        )
    main_dir = (
        CUSTOM_REQUEST_DIRECTORY_PATH
        if len(CUSTOM_REQUEST_DIRECTORY_PATH) > 0
        and CUSTOM_REQUEST_STATE.capitalize().strip() == "True"
        and MOVE_CUSTOM_REQUEST_TO_MAIN_DIRECTORY.capitalize().strip() == "False"
        else MAIN_DIRECTORY_FOR_ALL_FILES
    )
    main_fail_path = (
        f"{main_dir}{os.sep}{title[:-5].strip().lower()}{os.sep}{md_}_"
        if len(title) > 5
        else f"{main_dir}{os.sep}{title.strip().lower()}{os.sep}{md_}_"
    )
    main_fail_path_json = (
        f"{main_dir}{os.sep}{title[:-5].strip().lower()}/main"
        if len(title) > 5
        else f"{main_dir}{os.sep}{title.strip().lower()}/main"
    )
    try:
        await page.goto(link)
        logger["success"].append(link)
    except Exception as e:
        logger["fail"].append(link)
        logs.err(e, __name__)

    try:
        description = page.locator('section[data-tid="ContentOverview"]').locator("p")
        if description:
            description_ = await description.inner_text(timeout=2000.0)
            # print(description)
            json_dict["description"] = description_
        else:
            json_dict["description"] = "None"

    except Exception as e:
        json_dict["description"] = "None"
        # print(e)
        logs.warn(e, __name__)

    await rating(page, context, json_dict)

    try:
        metadata = (
            await page.locator('section[data-tid="ContentOverview"]')
            .locator('ul > li[data-tid="OverviewMeta"]')
            .all()
        )
        year = metadata[0] if len(metadata) >= 1 else None
        country_season = metadata[1] if len(metadata) >= 2 else None
        duration = metadata[2] if len(metadata) >= 3 else None
        censor = metadata[3] if len(metadata) >= 4 else None
        year_ = (
            re.sub(r"\D", "", await year.inner_text()) if year is not None else "None"
        )
        country_season_ = (
            await country_season.inner_text() if country_season is not None else "None"
        )
        duration_ = await duration.inner_text() if duration is not None else "None"
        censor_ = await censor.inner_text() if censor is not None else "None"
        json_dict["year"] = year_
        json_dict["season" if "сезон" in country_season_ else "country"] = (
            country_season_
        )
        check = True if "сезон" in country_season_ else False
        json_dict["country" if check else "duration"] = duration_
        json_dict["censor"] = censor_

        # print(year_)
        # print(country_)
        # print(duration_)
        # print(censor_)
        logs.info(
            f"\nmeta:\nyear: {year_},\nduration_: {duration_},\ncensor_: {censor_},\ncountry_season_: {country_season_}\n",
            __name__,
        )
    except Exception as e:
        # print(e)
        logs.err(e, __name__)
    return main_fail_path_json, main_fail_path, json_dict, img


async def rating(page: Page, context: BrowserContext, json_dict: dict) -> None:
    for rating_locator in [
        'div[data-tid="Tag"]',
        'div[data-tid="QualitySticker"]',
        'a[data-tid="KinopoiskTop250List"] > span[data-tid="KinopoiskTop250ListRating"] > span:nth-child(2)',
    ]:
        try:
            rating = page.locator('section[data-tid="ContentOverview"]').locator(
                rating_locator
            )
            if rating:
                rating_ = await rating.inner_text(timeout=2000.0)
                if rating_ and "," in rating_:
                    rating_ = rating_.replace(",", ".")
                json_dict["rating"] = str(float(rating_))
                break
            else:
                json_dict["rating"] = "None"
        except Exception as e:
            json_dict["rating"] = "None"
            logs.warn(e, __name__)
            continue
