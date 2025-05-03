import json
import os

import aiofiles
import numpy as np

from helpers.custom_logger import logs
from sys_argv.sys_argv import MAIN_DIRECTORY_FOR_ALL_FILES


async def check_url_can_parsed(links: np.ndarray) -> np.ndarray:
    path = os.path.join(MAIN_DIRECTORY_FOR_ALL_FILES, "urls.json")

    new_list_links: list = []
    old_list_urls: list = []
    if os.path.exists(path):
        async with aiofiles.open(path, "r", encoding="utf-8") as frj:
            json_data = json.loads(await frj.read())
            json_data_success = json_data["success"]
            json_data_failed = json_data["fail"]
            json_data_ = np.array(json_data_success)
            for i in links:
                url = i[2]
                if (
                    url not in json_data_
                    and url not in np.array(new_list_links).ravel()
                ):
                    new_list_links.append(i)
                else:
                    old_list_urls.append(url)
            full_json_data = np.concatenate((json_data_, json_data_failed))

            new_json_data_success: np.ndarray = np.array([])
            new_json_data_failed: np.ndarray = np.array([])
            for i in full_json_data:
                if i not in old_list_urls:
                    full_json_data = np.delete(
                        full_json_data, np.where(full_json_data == i)
                    )
            # print(full_json_data)
            for i in full_json_data:
                if i in json_data_ and i not in new_json_data_success:
                    # print(i in json_data_)
                    new_json_data_success = np.append(new_json_data_success, i)
                if i in json_data_failed and i not in json_data_failed:
                    new_json_data_failed = np.append(new_json_data_failed, i)

            async with aiofiles.open(path, "w", encoding="utf-8") as fwj:
                await fwj.write(
                    json.dumps({"fail": new_json_data_failed.tolist(), "success": new_json_data_success.tolist()}, ensure_ascii=False, indent=4)  # type: ignore
                )
        logs.info("json has been loaded", __name__)
        return np.array(new_list_links)
    else:
        # print("main json already not exist, return current np.array")
        logs.info("main json already not exist, return current np.array", __name__)

        return links
