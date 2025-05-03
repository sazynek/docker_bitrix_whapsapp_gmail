import datetime
import json
import os
import re
from random import randint
from time import sleep as sleep_

import aiofiles  # type: ignore
from dotenv import get_key

from helpers.const import STATE_THREAD
from helpers.custom_logger import logs


def find_env_file(
    key: str, path: str = os.getcwd(), is_print: bool = False, dev: bool = True
) -> str:
    dotenv_path = os.path.join(path, "dev.env" if dev else ".env")
    real_key = get_key(dotenv_path, key.upper().strip())

    if is_print:
        logs.debug("\n" + f"key {key.upper().strip()}: " + f"{real_key}", __name__)

    assert real_key is not None

    return real_key


async def write_cookies(cookies: str, file_name: str = "any.txt") -> None:
    async with aiofiles.open(file_name, "w", encoding="utf-8") as fw:
        cookies = str(cookies)
        cookies = cookies.replace("True", "true")
        cookies = cookies.replace("False", "false")
        cookies = cookies.replace("False", "false")
        cookies = re.sub(r"\'", '"', cookies)
        cook = json.loads(cookies)
        await fw.write(json.dumps(cook, ensure_ascii=False, indent=4))


def timer() -> None:
    global STATE_THREAD
    count: float = 0.0
    random_value = randint(0, 101)
    random_value = float(f"0.{random_value}")  # type:ignore
    while STATE_THREAD[0]:
        count += random_value
        print(
            f"{datetime.datetime.now()}  [ThreadPoolEx] [INFO ]   Timer: {round(count,3)}"
        )
        # logs.info(f"Timer: {round(count,3)}", __name__)
        sleep_(random_value)
