import asyncio
import json
import os
from asyncio import sleep
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import aiofiles
import aiohttp
import numpy as np
from json2xml import json2xml
from json2xml.utils import readfromjson
from json_excel_converter import Converter
from json_excel_converter.xlsx import Writer

from helpers.custom_logger import logs
from sys_argv.sys_argv import FILTER_TO_SORT_ITEMS, MAIN_DIRECTORY_FOR_ALL_FILES


@dataclass()
class Creator:

    @staticmethod
    async def load_image(image: str, session: aiohttp.ClientSession, path: str) -> None:
        real_path = os.path.join(
            os.path.dirname(path), f"{os.path.basename(path)}.jpeg"
        )

        await sleep(0.3)
        async with session.get(image) as resp:
            if resp.status == 200 and not os.path.exists(real_path):
                Path(os.path.dirname(path)).mkdir(exist_ok=True, parents=True)
                async with aiofiles.open(real_path, "wb") as fwb:
                    await fwb.write(await resp.read())  # type: ignore

    @staticmethod
    async def create_json(json_data: dict, path: str) -> None:
        real_path = os.path.join(
            os.path.dirname(path), f"{os.path.basename(path)}.json"
        )
        if not os.path.exists(real_path):
            Path(os.path.dirname(path)).mkdir(exist_ok=True, parents=True)
            async with aiofiles.open(real_path, "w", encoding="utf-8") as fwj:
                await fwj.write(json.dumps(json_data, ensure_ascii=False, indent=4))  # type: ignore

    @staticmethod
    async def create_urls(
        json_data: dict[Literal["fail", "success"], list],
        path: str = f"{str(MAIN_DIRECTORY_FOR_ALL_FILES).replace('/','').strip() if str(MAIN_DIRECTORY_FOR_ALL_FILES).endswith('/') else str(MAIN_DIRECTORY_FOR_ALL_FILES)}{os.sep}urls",
    ) -> None:
        real_path = os.path.join(
            os.path.dirname(path), f"{os.path.basename(path)}.json"
        )
        Path(os.path.dirname(path)).mkdir(exist_ok=True, parents=True)
        if os.path.exists(real_path):
            async with aiofiles.open(real_path, "r", encoding="utf-8") as frj:
                old_inf_json: dict = await frj.read()  # type:ignore
                if len(old_inf_json) > 0:
                    old_inf_json = json.loads(old_inf_json)  # type: ignore
                elif len(old_inf_json) == 0:
                    old_inf_json = json.loads(json.dumps({"fail": [], "success": []}))  # type: ignore
                else:
                    old_inf_json = json.loads(old_inf_json)  # type: ignore

                json_data["fail"].extend(old_inf_json["fail"])
                json_data["success"].extend(old_inf_json["success"])
                json_data["fail"] = list(set(json_data["fail"]))  # type:ignore
                json_data["success"] = list(set(json_data["success"]))  # type:ignore

        async with aiofiles.open(real_path, "w", encoding="utf-8") as fwj:
            await fwj.write(json.dumps(json_data, ensure_ascii=False, indent=4))  # type: ignore

    @staticmethod
    async def create_main_json_sorted(sortOnly: str = "") -> None:
        lock = asyncio.Lock()
        global FILTER_TO_SORT_ITEMS
        FILTER_TO_SORT_ITEMS = (
            sortOnly if len(sortOnly) > 0 and sortOnly != "" else FILTER_TO_SORT_ITEMS
        )
        old_inf_json: list = []
        real_path = os.path.join(MAIN_DIRECTORY_FOR_ALL_FILES, "main.json")
        if os.path.exists(real_path):
            async with aiofiles.open(real_path, "r", encoding="utf-8") as frj:
                old_inf_json = await frj.read()  # type:ignore
                if len(old_inf_json) > 0:
                    old_inf_json = json.loads(old_inf_json)  # type:ignore
                elif len(old_inf_json) == 0:
                    old_inf_json = []
            json_data_ = np.array(old_inf_json)
            tasks_a: list = []
            for i in json_data_:
                await Creator.create_main_json_sorted_helper_filter(i)

            logs.info(
                f'{print([i["rating"] for i in json_data_ if "rating" in i])}\n {print([i["censor"] for i in json_data_ if "censor" in i])}\n{print([i.get("year") for i in json_data_])}'
            )
            rate_arr: np.ndarray = np.array([])
            match str(FILTER_TO_SORT_ITEMS).lower().strip():
                case "rating":
                    rate_arr = np.array(
                        sorted(
                            [(float(i["rating"])) for i in json_data_],
                            reverse=True,
                        )
                    )
                    rate_arr = np.char.mod("%s", rate_arr)
                case "censor":
                    rate_arr = np.array(
                        sorted(
                            [
                                (int(str(i["censor"]).replace("+", "").strip()))
                                for i in json_data_
                            ],
                            reverse=True,
                        )
                    )
                    rate_arr = np.char.mod("%s", rate_arr)
                    rate_arr = rate_arr + "+"  # type: ignore
                case "years":
                    rate_arr = np.array(
                        sorted(
                            [
                                (int(str(i["year"]).replace("+", "").strip()))
                                for i in json_data_
                            ],
                            reverse=True,
                        )
                    )

                    rate_arr = np.char.mod("%s", rate_arr)
            sorted_list: list = []
            for rate_sorted in rate_arr:
                for j in json_data_:
                    await Creator.create_main_json_sorted_helper(
                        j, rate_sorted, sorted_list
                    )

            arr = set([i["link"] for i in sorted_list])
            sorted_list = [i for i in sorted_list if i["link"] in arr]  # type:ignore
            print(f"list of sorted items: {sorted_list}")
            async with aiofiles.open(real_path, "w", encoding="utf-8") as fwj:
                await fwj.write(json.dumps(sorted_list, ensure_ascii=False, indent=4))

    @staticmethod
    async def create_main_json_sorted_helper(
        j: Any, rate_sorted: Any, sorted_list: list
    ) -> None:
        if rate_sorted in j.values() and j not in sorted_list:
            sorted_list.append(j)

    @staticmethod
    async def create_main_json_sorted_helper_filter(i: Any) -> None:
        if "rating" in i:
            if i["rating"] == "None":
                i["rating"] = "0.0"
        if "censor" in i:
            if i["censor"] == "None":
                i["censor"] = "0+"
        if "year" in i:
            if i["year"] == "None":
                i["year"] = "0+"

    @staticmethod
    async def create_main_json(
        json_data: list[dict[str, Any]] = [],
        path: str = f"{str(MAIN_DIRECTORY_FOR_ALL_FILES).replace('/','').strip() if str(MAIN_DIRECTORY_FOR_ALL_FILES).endswith('/') else str(MAIN_DIRECTORY_FOR_ALL_FILES)}{os.sep}main",
    ) -> None:

        old_inf_json: list = []
        Path(os.path.dirname(path)).mkdir(exist_ok=True, parents=True)
        real_path = os.path.join(
            os.path.dirname(path), f"{os.path.basename(path)}.json"
        )
        if os.path.exists(real_path):
            async with aiofiles.open(real_path, "r", encoding="utf-8") as frj:
                old_inf_json = await frj.read()  # type:ignore
                if len(old_inf_json) > 0:
                    old_inf_json = json.loads(old_inf_json)  # type:ignore
                elif len(old_inf_json) == 0:
                    old_inf_json = []

            json_data.extend(old_inf_json)
        json_data_1 = np.array(json_data)
        json_data_2 = np.array(old_inf_json if old_inf_json else [])

        for i in json_data_1:
            if i not in json_data_2:
                json_data_2 = np.append(json_data_2, i)
        try:
            if os.path.exists(real_path) and len(json_data_2) > 0:
                os.remove(real_path)
        except Exception:
            pass
        Path(MAIN_DIRECTORY_FOR_ALL_FILES).mkdir(exist_ok=True, parents=True)
        if len(json_data_2) > 0:
            async with aiofiles.open(real_path, "w", encoding="utf-8") as fwj:
                await fwj.write(
                    json.dumps(json_data_2.tolist(), ensure_ascii=False, indent=4)
                )

    @staticmethod
    async def create_xml() -> None:
        path = os.path.join(MAIN_DIRECTORY_FOR_ALL_FILES, "main.json")
        xml_path = os.path.join(MAIN_DIRECTORY_FOR_ALL_FILES, "main.xml")
        if os.path.exists(path):
            try:
                data = readfromjson(path)
                async with aiofiles.open(xml_path, "w", encoding="utf-8") as fxml:
                    await fxml.write(json2xml.Json2xml(data, item_wrap=True, pretty=True).to_xml())  # type: ignore
            except Exception as e:
                print(f"xml error: {e}")
                logs.err(f"xml error: {e}", __name__)

    @staticmethod
    async def create_excel() -> None:
        path = os.path.join(MAIN_DIRECTORY_FOR_ALL_FILES, "main.json")
        xlsx_path = os.path.join(MAIN_DIRECTORY_FOR_ALL_FILES, "main.xlsx")
        if os.path.exists(path):
            try:
                async with aiofiles.open(path, "r", encoding="utf-8") as fxml:
                    data = json.loads(await fxml.read())  # type: ignore
                conv = Converter()
                conv.convert(
                    data,
                    Writer(
                        file=xlsx_path,
                        column_widths={
                            "title": 50,
                            "link": 20,
                            "img": 20,
                            "description": 20,
                        },
                    ),
                )
            except Exception as e:
                print(f"excel error: {e}")
                logs.err(f"excel error: {e}", __name__)


# if __name__ == "__main__":
# asyncio.run(Creator.create_main_json())
