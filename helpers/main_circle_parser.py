import asyncio

from helpers.create_func import Creator
from helpers.custom_logger import logs
from helpers.help import help
from helpers.main import main
from helpers.remove_files import remove_files
from helpers.replace_outer_file_to_data_dir import replace_outer_file_to_main_dir
from sys_argv.sys_argv import (
    MOVE_CUSTOM_REQUEST_TO_MAIN_DIRECTORY,
    RECURSE_COUNT,
    REMOVE_ONE_FILE,
    SORTED_WITHOUT_PARSE,
    args,
)


async def main_circle_parser() -> None:
    global SORTED_WITHOUT_PARSE
    filter_, logic_ = SORTED_WITHOUT_PARSE.split(",")

    if REMOVE_ONE_FILE.strip().capitalize() == "True":
        await remove_files()
    elif (
        logic_.strip().capitalize() == "True"
        and REMOVE_ONE_FILE.strip().capitalize() != "True"
    ):
        await Creator.create_main_json_sorted(sortOnly=filter_.strip().lower())
    elif args.help is not None:
        help()
    elif MOVE_CUSTOM_REQUEST_TO_MAIN_DIRECTORY.strip().capitalize() == "True":
        await replace_outer_file_to_main_dir()
    else:
        try:
            print("start main parser")
            logs.info("start main parser", __name__)
            await main(RECURSE_COUNT=int(str(RECURSE_COUNT).lower().strip()))
        except Exception as e:
            # logs.err(f'err: {e}', __name__)
            print(f"{__name__}: {e}")


def run() -> tuple[str, bool]:
    asyncio.run(main_circle_parser())
    return ("main_thread_finished", True)
