import asyncio
import glob
import json
import os
import re
from typing import Any

import aiofiles
from flask import Flask, jsonify, request

from helpers.const import PREFIX
from helpers.custom_logger import logs
from helpers.remove_files import remove_files
from sys_argv.sys_argv import (
    MAIN_DIRECTORY_FOR_ALL_FILES,
    REMOVE_ONE_FILE,
    REMOVE_ONE_FILE_FULLPATH_TO_DIR,
    WHATS_APP_ON,
)
from tokens.tokens import CHAT_ID, HOST, PHONE, PORT
from whapi.whapi import whapi


async def send_message() -> bool:
    payload: dict = {"to": f"{PHONE}"}
    body = "Парсинг был завершен."
    path: str = os.path.join(MAIN_DIRECTORY_FOR_ALL_FILES, "main.json")
    path_urls: str = os.path.join(MAIN_DIRECTORY_FOR_ALL_FILES, "urls.json")
    json_file_len: int = 0
    parse_urls_success: int = 0
    parse_urls_failed: int = 0

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as frj:
            json_file = json.load(frj)
            json_file_len = len(json_file)
            body += f"\nКол-во всех файлов: {json_file_len}.\n"
    else:
        body += f"\nКол-во всех файлов: 0.\n"
    if os.path.exists(path):
        with open(path_urls, "r", encoding="utf-8") as frj:
            json_file = json.load(frj)
            parse_urls_success = len(json_file["success"])
            parse_urls_failed = len(json_file["fail"])
            body += f"Кол-во успешных запросов: {parse_urls_success}.\n"
            body += f"Кол-во проваленных запросов: {parse_urls_failed}.\n"
            body += f"Состояние не было определенно: {abs(json_file_len-parse_urls_failed-parse_urls_success)}\n"
    else:
        body += f"Кол-во успешных запросов: 0.\n"
        body += f"Кол-во проваленных запросов: 0.\n"
        body += f"Состояние не было определенно: 0\n"

    payload["body"] = body
    # print(payload)

    @whapi.body(body=payload)
    @whapi.post("/messages/text")
    def send_message_(res: Any) -> Any:
        return res

    res = send_message_()
    logs.info(res)
    return res["sent"] if "sent" in res else False


# /messages/list/CHAT_ID
async def get_last_msg_from_text() -> str | None | tuple[str, str, str]:
    @whapi.body(body={"": ""})
    @whapi.get(f"/messages/list/{CHAT_ID}?count=1")
    def get_last_msg_from_text_(res: Any) -> None:
        return res

    res = get_last_msg_from_text_()
    res = res["messages"][0]
    if "action" in res["type"]:
        act = res["action"]  # type: ignore
        match act["type"]:  # type: ignore
            case "edit":
                return act["edited_content"]["caption"]  # type: ignore
    elif "link_preview" in res["type"]:
        return (
            res["link_preview"]["title"],
            res["link_preview"]["url"],
            res["link_preview"]["description"],
        )

    else:
        match res["type"]:
            case "image":
                return res["image"]["caption"]
            case "text":
                return res["text"]["body"]

    return None


@whapi.post("/messages/text")
def sender(body: str = "") -> None:
    pass


async def del_prf(query: str) -> str:
    if query is not None:
        query_prefix = re.search(
            r"(?=/)\S*", query, re.IGNORECASE
        ).group()  # type:ignore
        return query.replace(query_prefix, "").strip().lower()


async def mini_task(data: dict, query: str) -> dict | None:
    title = data["title"].lower()
    if query in title:
        return data
    return None


async def mini_task_for_delete(path: str, query: str) -> Any | None:
    async with aiofiles.open(path, "r", encoding="utf-8") as frj:
        js = json.loads(await frj.read())
    title = js["title"].lower()
    if query in title:
        return path
    return None


async def sent_by_name(query: str = "", PHONE: str = PHONE) -> None:
    """

    /find

    """
    payload: dict = {"to": f"{PHONE}", "body": "file is not found"}
    tasks: list = []
    path = os.path.join(MAIN_DIRECTORY_FOR_ALL_FILES, "main.json")
    word = f"{PREFIX}find "
    if word in query:
        query = await del_prf(query)
        async with aiofiles.open(path, "r", encoding="utf-8") as frj:
            js_file = json.loads(await frj.read())
            for i in js_file:
                task = asyncio.create_task(mini_task(i, query))
                tasks.append(task)
        res = await asyncio.gather(*tasks)
        res = [i for i in res if type(i) == dict]
        if res:
            payload["body"] = f"file is contains in json format:\n\t\t{res[0]}\n"
        sender(body=payload)


async def remove_by_name(query: str = "", PHONE: str = PHONE) -> None:
    """

    /remove

    """
    global REMOVE_ONE_FILE
    global REMOVE_ONE_FILE_FULLPATH_TO_DIR
    path = MAIN_DIRECTORY_FOR_ALL_FILES
    payload: dict = {"to": f"{PHONE}", "body": "file is not found"}
    tasks: list = []
    word = f"{PREFIX}remove"
    if word in query:
        query = await del_prf(query)

        files = glob.glob(f"{path}/**/*.json")
        for i in files:
            task = asyncio.create_task(mini_task_for_delete(i, query))
            tasks.append(task)
        res = await asyncio.gather(*tasks)
        # print(res)
        res = [i for i in res if type(i) == str]

        if res:
            str_res = res[0]
            REMOVE_ONE_FILE = "True"
            REMOVE_ONE_FILE_FULLPATH_TO_DIR = str_res
            await remove_files(
                arg_REMOVE_ONE_FILE=REMOVE_ONE_FILE,
                arg_REMOVE_ONE_FILE_FULLPATH_TO_DIR=os.path.dirname(
                    REMOVE_ONE_FILE_FULLPATH_TO_DIR
                ),
            )
            payload["body"] = f"file has been deleted by path:\n\t\t{str_res}"
        sender(body=payload)


app = Flask(__name__)


@app.route("/hook", methods=["POST"])
async def webhook():  # type:ignore

    data = request.json

    if "messages" in data:  # type:ignore
        for message in data["messages"]:  # type:ignore
            sender = message["from"]  # Sender's number
            text = message.get("body", "")  # Text of message
            await sent_by_name(query=text, PHONE=sender)
            await remove_by_name(query=text, PHONE=sender)
    return jsonify({"status": "success"}), 200


def whapi_methods() -> None:
    if WHATS_APP_ON.strip().capitalize() == "True":
        print("start local server")
        app.run(host=HOST, port=int(str(PORT).strip()))


# if __name__ == "__main__":
#     asyncio.run(whapi_methods())
