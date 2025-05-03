import asyncio
from random import randint
from time import perf_counter
from typing import Any

from playwright.async_api import async_playwright

from helpers.const import STATE_THREAD
from helpers.custom_logger import logs
from helpers.init_playwright import initial_playwright
from helpers.new_page import new_page
from helpers.remove_files import remove_files
from helpers.replace_outer_file_to_data_dir import replace_outer_file_to_main_dir
from helpers.send_email import gmail
from sys_argv.sys_argv import SLEEP_TIME_AFTER_REQUEST_FAILED, WHATS_APP_ON
from tokens.tokens import TO
from whapi.whapi_methods import send_message


@gmail(
    to=TO,
    subject="Кинопоиск - данные парсинга",
    body="Добрый день. Вам переслали главный файл со всей информацией после парсинга в 3 экземплярах(json, xlsx, xml)",
    files=(
        "./data/main.json",
        "./data/main.xlsx",
        "./data/main.xml",
    ),
)
async def script(**kwargs: Any) -> bool:  # type: ignore
    global STATE_THREAD
    STATE_THREAD[0] = True
    min, max = SLEEP_TIME_AFTER_REQUEST_FAILED.strip().split(",")
    start = perf_counter()
    RECURSE_COUNT = kwargs["RECURSE_COUNT"]
    print("script start work. Recurse: {}".format(RECURSE_COUNT))
    logs.info("script start work. Recurse: {}".format(RECURSE_COUNT), __name__)
    remove_task = asyncio.create_task(remove_files())
    replace_task = asyncio.create_task(replace_outer_file_to_main_dir())
    try:
        async with async_playwright() as playwright:
            task_init = asyncio.create_task(
                initial_playwright(playwright, headless=True)
            )
            _, initial, _ = await asyncio.gather(remove_task, task_init, replace_task)
            page, context = initial
            # print("ALL WORK!!!!!!!!!!!!!!!!!!!!!")
            await new_page(page, context)
            if str(WHATS_APP_ON).strip().capitalize() == "True":
                await send_message()
            return True
    except RecursionError as e:
        if RECURSE_COUNT > 0 and "recurse" in str(e):
            RECURSE_COUNT -= 1
            await asyncio.sleep(randint(int(min), int(max)))
            await script(RECURSE_COUNT=RECURSE_COUNT)
    finally:
        end = perf_counter()
        # print(
        #     f"Time execute to recurse script  with recuse {RECURSE_COUNT} is {end-start:2f}"
        # )
        logs.info(
            f"Time execute to recurse script  with recuse {RECURSE_COUNT} is {end-start:2f}"
        )
