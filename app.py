import os
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from time import perf_counter
from typing import Any

from helpers.const import STATE_THREAD
from helpers.custom_logger import logs
from helpers.global_func import timer
from helpers.main_circle_parser import run
from sys_argv.sys_argv import PARSE_ONE_TIME
from whapi.whapi_methods import whapi_methods


def app() -> None:
    global STATE_THREAD
    start = perf_counter()
    futures: list = []
    result = ""
    state = False
    try:
        with ThreadPoolExecutor() as t:
            for idx, i in enumerate([run, timer, whapi_methods]):

                if idx != 0:
                    if (
                        PARSE_ONE_TIME.strip().capitalize() == "True"
                        and idx == 1
                        and os.path.exists("main_cook.json")
                    ):
                        futures.append(t.submit(i))  # type: ignore
                    elif (
                        PARSE_ONE_TIME.strip().capitalize() == "False"
                        and idx == 2
                        and os.path.exists("main_cook.json")
                    ):
                        futures.append(t.submit(i))
                    else:
                        continue
                else:
                    futures.append(t.submit(i))  # type: ignore
            t.shutdown(wait=False, cancel_futures=True)
            ready, not_ready = wait(futures, return_when=FIRST_COMPLETED)

            for j in ready:
                res, st = j.result()
                result = res
                state = st

            if result == "main_thread_finished" and state:
                for thread in not_ready:
                    if thread.running():
                        STATE_THREAD[0] = False
    except Exception as e:
        logs.err(f"main program is failed __name__ {e}", __name__)
    finally:
        end = perf_counter()
        logs.info(f"All time execute program: {end - start:4f}", __name__)


# All time execute program: 349.409017. Первый тест в сыром виде по всех категориям.(с первичной сортировкой)
# 2025-04-28 22:14:07,548 [MainThread  ] [INFO ]  All time execute program: 691.263566 before fix
# 2025-04-28 23:38:48,067 [MainThread  ] [INFO ]  All time execute program: 307.130747 after fix
# 2025-04-29 19:43:50,941 [MainThread  ] [INFO ]  All time execute program: 249.000862 after fix all but, and rework
if __name__ == "__main__":
    app()
