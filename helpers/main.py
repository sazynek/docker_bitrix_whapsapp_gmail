import asyncio
from typing import Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from helpers.const import STATE_THREAD
from helpers.custom_logger import logs
from helpers.script import script
from helpers.select_time_type import select_time_type
from sys_argv.sys_argv import CUSTOM_REQUEST_STATE, PARSE_ONE_TIME


async def main(**kwargs: Any) -> bool:  # type: ignore
    global STATE_THREAD
    scheduler = AsyncIOScheduler()
    try:
        if (
            str(CUSTOM_REQUEST_STATE).strip().capitalize() == "False"
            and str(PARSE_ONE_TIME).strip().capitalize() == "False"
        ):
            await select_time_type(scheduler, **kwargs)
            scheduler.start()
            while True:
                await asyncio.sleep(0.1)
        else:
            await script(**kwargs)
    except Exception as e:
        logs.err(f'err: {e}', __name__)
    finally:
        if (
            str(CUSTOM_REQUEST_STATE).strip().capitalize() == "False"
            and str(PARSE_ONE_TIME).strip().capitalize() == "False"
        ):
            scheduler.shutdown()
