import re
from datetime import datetime, timezone
from typing import Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from helpers.custom_logger import logs
from helpers.script import script
from sys_argv.sys_argv import (
    REPLACE_CURRENT_WORKS_OF_SCRIPT_NEW_WORKS,
    TIMER,
    TIMER_TYPE,
)


async def select_time_type(scheduler: AsyncIOScheduler, **kwargs: Any) -> None:

    logs.info("value: " + f"{TIMER_TYPE.lower().strip()}")
    logs.info(
        "interval: " + f"every {TIMER.lower().strip()} {TIMER_TYPE.lower().strip()}"
    )
    logs.info("timezone: " + f"{timezone.utc}")
    logs.info(f"start at with timezone {timezone.utc}: " + f"{datetime.utcnow()}")
    logs.info("current time: " + f"{datetime.now()}")
    logs.info(
        f"different was be corrected by: "
        + f"{re.search(r"\+[\d:]+", str(datetime.now().astimezone())).group().strip()} hours",  # type:ignore
    )
    match str(TIMER_TYPE).lower().strip():
        case "seconds":
            scheduler.add_job(
                script,
                trigger=IntervalTrigger(
                    timezone=timezone.utc,
                    start_date=datetime.now().astimezone(),
                    seconds=int(str(TIMER).lower().strip()),
                ),
                replace_existing=(
                    True
                    if (REPLACE_CURRENT_WORKS_OF_SCRIPT_NEW_WORKS).capitalize().strip()
                    == "True"
                    else False
                ),
                next_run_time=datetime.now().astimezone(),
                kwargs={**kwargs},
            )
        case "minutes":
            scheduler.add_job(
                script,
                trigger=IntervalTrigger(
                    timezone=timezone.utc,
                    start_date=datetime.now().astimezone(),
                    jitter=0,
                    minutes=int(str(TIMER).lower().strip()),
                ),
                next_run_time=datetime.now().astimezone(),
                replace_existing=(
                    True
                    if str(REPLACE_CURRENT_WORKS_OF_SCRIPT_NEW_WORKS)
                    .capitalize()
                    .strip()
                    == "True"
                    else False
                ),
                kwargs={**kwargs},
            )
        case "hours":
            scheduler.add_job(
                script,
                trigger=IntervalTrigger(hours=int(str(TIMER).lower().strip())),
                replace_existing=(
                    True
                    if str(REPLACE_CURRENT_WORKS_OF_SCRIPT_NEW_WORKS)
                    .capitalize()
                    .strip()
                    == "True"
                    else False
                ),
                next_run_time=datetime.now().astimezone(),
                kwargs={**kwargs},
            )
        case "days":
            scheduler.add_job(
                script,
                trigger=IntervalTrigger(
                    timezone=timezone.utc, days=int(str(TIMER).lower().strip())
                ),
                replace_existing=(
                    True
                    if str(REPLACE_CURRENT_WORKS_OF_SCRIPT_NEW_WORKS)
                    .capitalize()
                    .strip()
                    == "True"
                    else False
                ),
                next_run_time=datetime.now().astimezone(),
                kwargs={**kwargs},
            )
        case "weeks":
            scheduler.add_job(
                script,
                trigger=IntervalTrigger(
                    start_date=datetime.now().astimezone(),
                    weeks=int(str(TIMER).lower().strip()),
                ),
                replace_existing=(
                    True
                    if str(REPLACE_CURRENT_WORKS_OF_SCRIPT_NEW_WORKS)
                    .capitalize()
                    .strip()
                    == "True"
                    else False
                ),
                next_run_time=datetime.now().astimezone(),
                kwargs={**kwargs},
            )
