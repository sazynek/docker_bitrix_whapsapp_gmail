import asyncio
import json
import os
import shutil
from glob import glob
from json import JSONDecodeError

import aiofiles
import numpy as np

from sys_argv.sys_argv import (
    CUSTOM_REQUEST_DIRECTORY_PATH,
    MAIN_DIRECTORY_FOR_ALL_FILES,
    REMOVE_ONE_FILE,
    REMOVE_ONE_FILE_FULLPATH_TO_DIR,
    START_PARSING_FROM_THE_BEGINNING,
)


async def remove_files(
    arg_REMOVE_ONE_FILE: str | None = None,
    arg_REMOVE_ONE_FILE_FULLPATH_TO_DIR: str | None = None,
) -> None:
    global CUSTOM_REQUEST_DIRECTORY_PATH
    global REMOVE_ONE_FILE_FULLPATH_TO_DIR
    global REMOVE_ONE_FILE

    REMOVE_ONE_FILE = (
        arg_REMOVE_ONE_FILE if arg_REMOVE_ONE_FILE is not None else REMOVE_ONE_FILE
    )
    REMOVE_ONE_FILE_FULLPATH_TO_DIR = (
        arg_REMOVE_ONE_FILE_FULLPATH_TO_DIR
        if arg_REMOVE_ONE_FILE_FULLPATH_TO_DIR is not None
        else REMOVE_ONE_FILE_FULLPATH_TO_DIR
    )
    if os.path.exists(REMOVE_ONE_FILE_FULLPATH_TO_DIR):
        CUSTOM_REQUEST_DIRECTORY_PATH = os.path.basename(CUSTOM_REQUEST_DIRECTORY_PATH)
        if CUSTOM_REQUEST_DIRECTORY_PATH in REMOVE_ONE_FILE_FULLPATH_TO_DIR:
            shutil.move(REMOVE_ONE_FILE_FULLPATH_TO_DIR, MAIN_DIRECTORY_FOR_ALL_FILES)
            REMOVE_ONE_FILE_FULLPATH_TO_DIR = f"{MAIN_DIRECTORY_FOR_ALL_FILES}{os.sep}{os.path.basename(REMOVE_ONE_FILE_FULLPATH_TO_DIR)}"
        path_urls = f"{MAIN_DIRECTORY_FOR_ALL_FILES}/urls.json"
        # print("state", REMOVE_ONE_FILE_FULLPATH_TO_DIR)
        # print("state", REMOVE_ONE_FILE)

        if os.path.exists(path_urls):
            value: bool = (
                True
                if str(START_PARSING_FROM_THE_BEGINNING).capitalize().strip() == "True"
                else False
            )
            async with aiofiles.open(path_urls, "r", encoding="utf-8") as frj:
                json_urls = json.loads(await frj.read())
                if value:
                    if ("success" and "fail") in json_urls:
                        json_urls_success = json_urls["success"]
                        json_urls_fail = json_urls["fail"]
                        json_all_urls = np.concatenate(
                            (json_urls_success, json_urls_fail)
                        )
                        await delete_all_folder_by_urls(json_all_urls)
                else:
                    if (
                        ("success" and "fail") in json_urls
                        and REMOVE_ONE_FILE.strip().capitalize() == "True"
                        and os.path.exists(REMOVE_ONE_FILE_FULLPATH_TO_DIR.strip())
                    ):
                        json_urls_success = json_urls["success"]
                        json_urls_fail = json_urls["fail"]
                        json_all_urls = np.concatenate(
                            (json_urls_success, json_urls_fail)
                        )
                        file = glob(f"{REMOVE_ONE_FILE_FULLPATH_TO_DIR}{os.sep}*.json")[
                            0
                        ]
                        # print(f"start removing one file {file}")
                        logs.warn(f"start removing one file {file}", __name__)
                        if file and os.path.isfile(file):
                            async with aiofiles.open(
                                file, "r", encoding="utf-8"
                            ) as frj:
                                link: str = json.loads(await frj.read())["link"]
                            await delete_all_folder_by_urls(np.array([link]))
                            json_all_urls = json_all_urls[
                                np.where(json_all_urls != link)
                            ]
                            json_urls_success = np.intersect1d(
                                json_all_urls, json_urls_success
                            )
                            json_urls_fail = np.intersect1d(
                                json_all_urls, json_urls_fail
                            )
                            async with aiofiles.open(
                                path_urls, "w", encoding="utf-8"
                            ) as fwj:
                                await fwj.write(
                                    json.dumps(
                                        {
                                            "fail": json_urls_fail.tolist(),
                                            "success": json_urls_success.tolist(),
                                        },
                                        ensure_ascii=False,
                                        indent=4,
                                    )
                                )
            is_delete_main_json = False
            if value:

                os.remove(path_urls)
                if os.path.exists(CUSTOM_REQUEST_DIRECTORY_PATH):
                    shutil.rmtree(CUSTOM_REQUEST_DIRECTORY_PATH)
            if os.path.exists(f"{MAIN_DIRECTORY_FOR_ALL_FILES}/main.json"):
                async with aiofiles.open(
                    f"{MAIN_DIRECTORY_FOR_ALL_FILES}/main.json", "r", encoding="utf-8"
                ) as frj:
                    j_data = json.loads(await frj.read())
                    if len(j_data) <= 0:
                        is_delete_main_json = True
                if is_delete_main_json:
                    # print("remove main.json")
                    logs.warn("remove main.json", __name__)
                    os.remove(f"{MAIN_DIRECTORY_FOR_ALL_FILES}/main.json")


async def delete_all_folder_by_urls(urls: np.ndarray) -> None:
    path_main = f"{MAIN_DIRECTORY_FOR_ALL_FILES}/main.json"

    json_main: np.ndarray = np.array([])
    json_main_links: np.ndarray = np.array([])
    values: list = []
    if os.path.exists(path_main):
        async with aiofiles.open(path_main, "r", encoding="utf-8") as frj:
            json_main = np.append(json_main, json.loads(await frj.read()))
            json_main_links = np.array([i["link"] for i in json_main if "link" in i])
    tasks: np.ndarray = np.array([])
    if os.path.exists(str(MAIN_DIRECTORY_FOR_ALL_FILES).strip()):

        files = glob(f"{MAIN_DIRECTORY_FOR_ALL_FILES.strip()}{os.sep}**{os.sep}*.json")

        for file in files:
            dir = os.path.dirname(file)
            task = asyncio.create_task(
                parse_folder_json_files(
                    file, urls, dir, (json_main, json_main_links, path_main, values)
                )
            )
            tasks = np.append(tasks, task)  # type:ignore
        await asyncio.gather(*tasks)


async def parse_folder_json_files(
    path: str,
    urls: np.ndarray,
    dir: str,
    json_main: tuple[np.ndarray, np.ndarray, str, list],
) -> np.ndarray:
    # print(f"parse path: {path}")

    json_full_inf_arr, json_main_links, path_main_file, values = json_main

    delete_file_state = False

    async with aiofiles.open(path, "r", encoding="utf-8") as frj:
        json_url = json.loads(await frj.read())["link"]
        if json_url in urls:
            delete_file_state = True
            if os.path.exists(path_main_file):
                if json_url in json_main_links:
                    values += np.where(json_url == json_main_links)

    if len(values) > 0:
        json_full_inf_arr = np.delete(json_full_inf_arr, values)
        async with aiofiles.open(path_main_file, "w", encoding="utf-8") as fwj:
            # print(json_full_inf_arr)
            await fwj.write(
                json.dumps(json_full_inf_arr.tolist(), ensure_ascii=False, indent=4)
            )
        while await is_not_valid_json(path_main_file):
            async with aiofiles.open(path_main_file, "w", encoding="utf-8") as fwj:
                # print(json_full_inf_arr)
                await fwj.write(
                    json.dumps(json_full_inf_arr.tolist(), ensure_ascii=False, indent=4)
                )
    if delete_file_state:
        #     print("start deleting file")
        logs.warn(f"start deleting file: {dir}\nstate: {delete_file_state}", __name__)
        shutil.rmtree(dir)
    return json_full_inf_arr


from helpers.custom_logger import logs


async def is_not_valid_json(path: str, count: int = 5) -> bool:

    try:
        async with aiofiles.open(path, "r", encoding="utf-8") as frj:
            json.loads(await frj.read())
        logs.warn("json is valid", __name__)
        return False
    except Exception as e:
        logs.warn("json is not valid", __name__)
        return True


# https://hd.kinopoisk.ru/film/1f8e3fb3aa5b438b90b138da7fb38587
