import argparse

import numpy as np

from config import *
from helpers.const import DOMAIN

# Initialize parser
parser = argparse.ArgumentParser(prefix_chars="@", allow_abbrev=True)
many_argv = np.array(
    [
        "@recurse",
        "@mainDir",
        "@ttype",
        "@timer",
        "@restartAll",
        "@newWork",
        "@sort",
        "@custom",
        "@customSt",
        "@customCanMove",
        "@customPath",
        "@once",
        "@fileCanRemove",
        "@fileRemove",
        "@proxy",
        "@sleep",
        "@sortOnly",
        "@whapi",
        "@help",
    ]
)

for argv in many_argv:
    parser.add_argument(argv)

args = parser.parse_args()

WHATS_APP_ON = args.whapi.strip().capitalize() if args.whapi is not None else WHATS_APP_ON
RECURSE_COUNT = (
    args.recurse.strip().strip() if args.recurse is not None else RECURSE_COUNT
)
MAIN_DIRECTORY_FOR_ALL_FILES = (
    args.mainDir.strip() if args.mainDir is not None else MAIN_DIRECTORY_FOR_ALL_FILES
)


TIMER_TYPE = args.ttype.strip() if args.ttype is not None else TIMER_TYPE
TIMER = args.timer.strip() if args.timer is not None else TIMER
START_PARSING_FROM_THE_BEGINNING = (
    args.restartAll.strip().capitalize()
    if args.restartAll is not None
    else START_PARSING_FROM_THE_BEGINNING
)

REPLACE_CURRENT_WORKS_OF_SCRIPT_NEW_WORKS = (
    args.newWork.strip().capitalize()
    if args.newWork is not None
    else REPLACE_CURRENT_WORKS_OF_SCRIPT_NEW_WORKS
)

FILTER_TO_SORT_ITEMS = (
    args.sort.strip()
    if args.sort is not None and str(args.sort).strip() in ["censor", "years", "rating"]
    else FILTER_TO_SORT_ITEMS
)

CUSTOM_REQUEST_URLS = (
    args.custom.strip()
    if args.custom is not None and (("http" or "https") and DOMAIN) in args.custom
    else CUSTOM_REQUEST_URLS
)
CUSTOM_REQUEST_STATE = (
    "True"
    if args.custom is not None and (("http" or "https") and DOMAIN) in args.custom
    else (
        args.customSt.strip().capitalize()
        if args.customSt is not None
        else CUSTOM_REQUEST_STATE
    )
)
MOVE_CUSTOM_REQUEST_TO_MAIN_DIRECTORY = (
    args.customCanMove.strip().capitalize()
    if args.customCanMove is not None
    else MOVE_CUSTOM_REQUEST_TO_MAIN_DIRECTORY
)
CUSTOM_REQUEST_DIRECTORY_PATH = (
    args.customPath.strip()
    if args.customPath is not None
    else CUSTOM_REQUEST_DIRECTORY_PATH
)

PARSE_ONE_TIME = (
    args.once.strip().capitalize() if args.once is not None else PARSE_ONE_TIME
)

REMOVE_ONE_FILE = (
    "True"
    if args.fileRemove is not None
    else (
        args.fileCanRemove.strip().capitalize()
        if args.fileCanRemove is not None
        else REMOVE_ONE_FILE
    )
)

REMOVE_ONE_FILE_FULLPATH_TO_DIR = (
    args.fileRemove.strip()
    if args.fileRemove is not None
    else REMOVE_ONE_FILE_FULLPATH_TO_DIR
)
SLEEP_TIME_AFTER_REQUEST_FAILED = (
    args.sleep.strip() if args.sleep is not None else SLEEP_TIME_AFTER_REQUEST_FAILED
)

SORTED_WITHOUT_PARSE = (
    args.sortOnly.strip()
    if args.sortOnly is not None
    and str(args.sortOnly).split(",")[0].strip().lower()
    in ["censor", "years", "rating"]
    else SORTED_WITHOUT_PARSE
)
PROXY = args.proxy.strip() if args.proxy is not None else PROXY
