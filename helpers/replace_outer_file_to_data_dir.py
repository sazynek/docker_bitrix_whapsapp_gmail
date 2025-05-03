import os
import shutil

import numpy as np

from sys_argv.sys_argv import (
    CUSTOM_REQUEST_DIRECTORY_PATH,
    MAIN_DIRECTORY_FOR_ALL_FILES,
    MOVE_CUSTOM_REQUEST_TO_MAIN_DIRECTORY,
)
from helpers.custom_logger import logs

async def replace_outer_file_to_main_dir() -> None:
    
    mains: list = []
    if MOVE_CUSTOM_REQUEST_TO_MAIN_DIRECTORY.capitalize().strip() == "True":
        if len(str(MAIN_DIRECTORY_FOR_ALL_FILES).strip()) > 0 and os.path.exists(
            str(MAIN_DIRECTORY_FOR_ALL_FILES).strip()
        ):
            mains = np.array(
                os.listdir(str(MAIN_DIRECTORY_FOR_ALL_FILES).strip())
            )  # type:ignore

        if len(str(CUSTOM_REQUEST_DIRECTORY_PATH).strip()) > 0 and os.path.exists(
            str(CUSTOM_REQUEST_DIRECTORY_PATH).strip()
        ):
            dirs1: np.ndarray = np.array(
                os.listdir(str(CUSTOM_REQUEST_DIRECTORY_PATH).strip())
            )
            if len(dirs1) > 0:
                dirs2 = str(CUSTOM_REQUEST_DIRECTORY_PATH).strip() + os.sep + dirs1
                # a = dirs.tolist()
                dirs3: list = []
                for dir2 in dirs2:
                    if os.path.exists(dir2):
                        for dir1 in dirs1:
                            if dir1 in mains and os.path.exists(
                                str(CUSTOM_REQUEST_DIRECTORY_PATH).strip()
                                + os.sep
                                + dir1
                            ):
                                shutil.rmtree(
                                    str(CUSTOM_REQUEST_DIRECTORY_PATH).strip()
                                    + os.sep
                                    + dir1
                                )
                            else:
                                dirs3.append(dir1)
                        # print(
                        #     f"directory [{dir2}] was moved to {str(MAIN_DIRECTORY_FOR_ALL_FILES).strip()}"
                        # )
                        logs.warn(f"directory [{dir2}] was moved to {str(MAIN_DIRECTORY_FOR_ALL_FILES).strip()}", __name__)
                        if os.path.basename(dir2) in dirs3 and os.path.exists(dir2):
                            shutil.move(dir2, str(MAIN_DIRECTORY_FOR_ALL_FILES).strip())



