import logging
import logging.handlers as handlers
import os
import shutil
import time
from dataclasses import InitVar, dataclass
from datetime import datetime, timezone, tzinfo
from enum import Enum
from hashlib import md5
from pathlib import Path
from time import sleep
from typing import Any
from uuid import uuid4

import numpy as np

from helpers.const import LOG_PATH


class EnumLog(Enum):
    ERROR = "errors"
    WARNING = "warning"
    INFO = "info"
    DEBUG = "debug"


class SizedTimedRotatingFileHandler(handlers.TimedRotatingFileHandler):  # type:ignore

    def __init__(  # type:ignore
        self,
        filename: str,
        maxBytes: int = 0,
        backupCount: int = 0,
        encoding: Any = None,
        delay: int = 0,
        when: str = "h",
        interval: int = 1,
        utc: bool = False,
    ):  # type:ignore
        handlers.TimedRotatingFileHandler.__init__(
            self,
            filename,
            when,
            interval,
            backupCount,
            encoding,
            delay,  # type:ignore
            utc,  # type:ignore
        )
        self.maxBytes = maxBytes

    def shouldRollover(self, record):  # type:ignore

        if self.stream is None:  # delay was set...
            self.stream = self._open()
        if self.maxBytes > 0:  # are we rolling over?
            msg = "%s\n" % self.format(record)
            # due to non-posix-compliant Windows feature
            self.stream.seek(0, 2)
            if self.stream.tell() + len(msg) >= self.maxBytes:
                return 1
        t = int(time.time())
        if t >= self.rolloverAt:
            return 1
        return 0


@dataclass
class CustomLogger:
    name: InitVar[str] = __name__
    max_byte: InitVar[int] = 50000

    def __post_init__(self, name: str, max_byte: int) -> None:
        self.__max_byte = max_byte
        path_of_log_file: np.ndarray = np.array(
            [
                EnumLog.ERROR.value,
                EnumLog.WARNING.value,
                EnumLog.INFO.value,
                EnumLog.DEBUG.value,
            ]
        )
        self.__name = name
        self.__name = self.__check_main_name(self.__name)
        self.__logger: logging.Logger = logging.getLogger(name=self.__name)
        self.__formatter = logging.Formatter(
            "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"
        )
        
        for custom_path in path_of_log_file:
            path = os.path.join(LOG_PATH, custom_path)
            if not os.path.exists(path):
                Path(path).mkdir(exist_ok=True, parents=True)
                Path(os.path.join(path, "copy")).mkdir(exist_ok=True, parents=True)

    def __base_log(self, err_msg: str, name: str, type: EnumLog) -> None:
        sleep(0.1)
        err_msg = str(err_msg)
        path_main_log_file = f"{LOG_PATH}{os.sep}{type.value}{os.sep}"
        try:
            for i in os.listdir(path_main_log_file):
                path_file = os.path.join(path_main_log_file, i)
                if i.endswith(".log") and os.path.isfile(path_file):
                    print(
                        "------------------------------------------",
                        path_file,
                        "------------------------------------------",
                    )
                    os.remove(path_file)
        except Exception as e:
            pass
        if len(err_msg) <= 0 or not err_msg or err_msg is None:
            raise ValueError("len of logger msg must be more then 0 and not are None")
        name = self.__check_main_name(self.__name if len(self.__name) > 0 else name)
        if name == "__main__":
            name = name.replace("__", "")
            name = f"__{name}"
        self.__logger.name = name
        hash_err_msg = (
            f'{md5(str(self.__logger.name).encode("utf-8")).hexdigest()[:-20]}__'
        )
        time_ = f'__{"-".join(
            list(
                map(
                    str,
                    datetime.now().astimezone().timetuple()[:4],
                )
            )
        )}__'
        full_path_log: str = (
            f"{LOG_PATH}{os.sep}{type.value}{os.sep}{self.__logger.name}{time_}{hash_err_msg}.log"
        )
        uuid = f"id={str(uuid4())[:-15]}"
        copy_full_path_log: str = (
            f"{LOG_PATH}{os.sep}{type.value}{os.sep}copy{os.sep}{self.__logger.name}{time_}{hash_err_msg}__{uuid}__.log"
        )
        h_file = logging.FileHandler(
            full_path_log,
            mode="a",
            encoding="utf-8",
        )
        ####
        h_file.setFormatter(self.__formatter)
        # #self.__logger.addHandler(h_file)
        # print(full_path_log)
        h_console_out = logging.StreamHandler()
        h_size = None
        h_console_out.setFormatter(self.__formatter)
        # self.__logger.addHandler(h_console_out)
        if os.path.exists(full_path_log):
            if os.path.getsize(full_path_log) >= self.__max_byte:
                h_size = SizedTimedRotatingFileHandler(
                    copy_full_path_log,
                    backupCount=300,
                    encoding="utf-8",
                    when="h",
                    maxBytes=self.__max_byte,
                    interval=10,
                )

                h_size.setFormatter(self.__formatter)
                self.__logger.addHandler(h_size)
                h_size.close()
        match type:
            case EnumLog.ERROR:
                self.__logger.setLevel(logging.ERROR)
                self.__formatter = logging.Formatter(
                    "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"
                )
                h_file.setLevel(logging.ERROR)
                h_console_out.setLevel(logging.ERROR)
                self.__logger.addHandler(h_file)
                self.__logger.addHandler(h_console_out)
                if h_size is not None:
                    h_size.setLevel(logging.ERROR)
                    self.__logger.addHandler(h_size)
                self.__logger.error(err_msg, exc_info=True)
            case EnumLog.WARNING:
                self.__logger.setLevel(logging.WARNING)
                self.__formatter = logging.Formatter(
                    "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"
                )
                h_file.setLevel(logging.WARNING)
                h_console_out.setLevel(logging.WARNING)
                self.__logger.addHandler(h_file)
                self.__logger.addHandler(h_console_out)
                if h_size is not None:
                    h_size.setLevel(logging.WARNING)
                    self.__logger.addHandler(h_size)
                self.__logger.warning(err_msg, exc_info=True)
            case EnumLog.INFO:
                self.__logger.setLevel(logging.INFO)
                self.__formatter = logging.Formatter(
                    "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"
                )
                h_file.setLevel(logging.INFO)
                h_console_out.setLevel(logging.INFO)
                self.__logger.addHandler(h_file)
                self.__logger.addHandler(h_console_out)
                if h_size is not None:
                    h_size.setLevel(logging.INFO)
                    self.__logger.addHandler(h_size)
                self.__logger.info(err_msg, exc_info=True)
            case EnumLog.DEBUG:
                self.__logger.setLevel(logging.DEBUG)
                self.__formatter = logging.Formatter(
                    "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"
                )
                h_file.setLevel(logging.DEBUG)
                h_console_out.setLevel(logging.DEBUG)
                self.__logger.addHandler(h_file)
                self.__logger.addHandler(h_console_out)
                if h_size is not None:
                    h_size.setLevel(logging.DEBUG)
                    self.__logger.addHandler(h_size)
                self.__logger.debug(err_msg, exc_info=False)
        h_file.close()

    def __none_func(self) -> None:
        pass

    def __check_main_name(self, name: str) -> str:
        return f'__{name.replace("__", "")}' if name == "__main__" else name

    def err(
        self,
        err_msg: Any,
        name: str = __name__,
    ) -> None:
        # print(name)
        self.__base_log(err_msg, name, type=EnumLog.ERROR)
        print(self.__logger.level)

    def warn(
        self,
        err_msg: Any,
        name: str = __name__,
    ) -> None:
        # print(name)
        self.__base_log(err_msg, name, type=EnumLog.WARNING)

    def info(
        self,
        err_msg: Any,
        name: str = __name__,
    ) -> None:
        # print(name)
        self.__base_log(err_msg, name, type=EnumLog.INFO)

    def debug(
        self,
        err_msg: Any,
        name: str = __name__,
    ) -> None:
        # print(name)
        self.__base_log(err_msg, name, type=EnumLog.DEBUG)


logs = CustomLogger()


# for i in range(2):
#     logs.err(i)
