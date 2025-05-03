import asyncio
import base64
import json
import os
from dataclasses import InitVar, dataclass
from pathlib import Path

import aiofiles
from fast_bitrix24 import BitrixAsync

from helpers.custom_logger import logs
from sys_argv.sys_argv import MAIN_DIRECTORY_FOR_ALL_FILES
from tokens.tokens import webhook


@dataclass
class Bitrix_(BitrixAsync):

    hook = webhook
    brx_status_path: InitVar[str] = "./bitrix_data"

    async def __call__(self) -> None:
        await self.__take_status_list()
        await self.__sent_file_to_brx()
        # await self.custom_field(name="Semen", custom_field=("email", "aga_go@gmail.ru"))

    def __post_init__(self, brx_status_path: str) -> None:
        super().__init__(webhook=self.hook)

        self.__brx_status_path = brx_status_path

        Path(self.__brx_status_path).mkdir(parents=True, exist_ok=True)

    async def __take_status_list(self) -> dict | None:
        path = os.path.join(self.__brx_status_path, "main.json")
        if os.path.exists(path):
            async with aiofiles.open(path, "r", encoding="utf-8") as frj:
                json_file = json.loads(await frj.read())
            if len(json_file) > 0:
                return json_file
        values = await self.get_all(" crm.status.list")  # type: ignore
        if values:
            values_ = {
                value["STATUS_ID"]: value["NAME"]
                for value in values
                if value["ENTITY_ID"] == "DEAL_STAGE"
            }
            print(values_)
            async with aiofiles.open(path, "w", encoding="utf-8") as fwj:
                await fwj.write(json.dumps(values_, ensure_ascii=False, indent=4))
            return values_

        return None

    async def __create_deal(self, payload: dict) -> None:
        # pl = {"FIELDS": {"TITLE": "New Deal #55", "STAGE_ID": "SUCCESS"}}
        try:
            await self.call("crm.deal.add", payload)  # type: ignore
            print("deal add to bitrix")
        except Exception as e:
            logs.debug(f"deal NOT add to bitrix. Err: {e}", __name__)

    async def update_deal(
        self, title: str = "New deal #1", update: dict | None = None
    ) -> None:
        json_file = await self.__take_status_list()
        deals = await self.get_all("crm.deal.list")  # type: ignore
        # print(deals)
        deal = [deal for deal in deals if title.lower() in deal["TITLE"].lower()]
        if deal:
            deal_ = deal[0]
            if json_file is None:
                raise ValueError("json status file is not exist")
            if update is not None and update["STAGE_ID"] in json_file:
                payload = {"id": deal_["ID"], **update}
                print(payload)
                res = await self.call("crm.deal.update", payload)  # type: ignore
                print(res)
                print("deal update at bitrix")

    async def __sent_file_to_brx(self) -> None:
        paths = [
            os.path.join(MAIN_DIRECTORY_FOR_ALL_FILES, "main.json"),
            os.path.join(MAIN_DIRECTORY_FOR_ALL_FILES, "main.xlsx"),
            os.path.join(MAIN_DIRECTORY_FOR_ALL_FILES, "main.xml"),
        ]
        tasks: list = []
        pass
        for path in paths:
            try:
                if not os.path.exists(path):
                    raise FileNotFoundError(f"file is not exists: {path}")
                task = asyncio.create_task(self.__mini_task(path))
                tasks.append(task)
            except FileNotFoundError as e:
                logs.err(e, __name__)
                break
        if len(tasks) != 0:
            js, xlsx, xml = await asyncio.gather(*tasks)
        else:
            return
        print(f"sent :{js, xlsx, xml}")
        try:
            res = await self.call(
                "disk.storage.uploadFile",
                [
                    {
                        "id": 1,
                        "data": {"NAME": "main.json"},
                        "fileContent": ["main.json", js],
                        "generateUniqueName": True,
                    },
                    {
                        "id": 1,
                        "data": {"NAME": "main.xlsx"},
                        "fileContent": ["main.xlsx", xlsx],
                        "generateUniqueName": True,
                    },
                    {
                        "id": 1,
                        "data": {"NAME": "main.xml"},
                        "fileContent": ["main.xml", xml],
                        "generateUniqueName": True,
                    },
                ],
            )
            logs.info(f"bitrix response on request all main.* files: {res}", __name__)
        except Exception as e:
            logs.err(f"Bitrix request has been failed: {e}", __name__)

    async def __mini_task(self, path: str) -> str:
        print(path)
        async with aiofiles.open(path, "rb") as file:
            encoded_file = base64.b64encode(await file.read()).decode()
        return encoded_file

    async def custom_field(self, name: str, custom_field: tuple[str, str]) -> None:
        """

        custom_field(значение строчное(str), имя строчное(str))

        """
        try:
            cus_name, cus_value = custom_field

            pl = (
                "crm.deal.userfield.add",
                {
                    "fields": {
                        "FIELD_NAME": f"{name}",
                        "EDIT_FORM_LABEL": f"{cus_name}",
                        "USER_TYPE_ID": "address",
                    }
                },
            )
            await self.call(pl[0], pl[1])  # type:ignore

            pl2 = {
                "FIELDS": {
                    "TITLE": f"{name}",
                    "STAGE_ID": "NEW",
                    f"UF_CRM_{name.upper()}": f"{cus_value}",
                }
            }

            await self.__create_deal(payload=pl2)
        except Exception as e:
            logs.err(f"Something problem with custom fields. Err: {e}", __name__)
