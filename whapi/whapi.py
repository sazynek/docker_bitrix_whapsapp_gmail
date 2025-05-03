import json
import re
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Callable

import requests  # type: ignore

from helpers.custom_logger import logs
from tokens.tokens import WH_API_TOKEN, WH_API_URL


class Methods(Enum):
    GET = auto()
    POST = auto()
    PUT = auto()
    DELETE = auto()


@dataclass
class whapi:
    __headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {WH_API_TOKEN}",  # Use the token from the .env file
    }

    @property
    def headers(self) -> dict[str, str]:
        return self.__headers

    @headers.setter
    def headers(self, value: str) -> None:
        assert isinstance(value, str)
        value = value.strip().capitalize()
        if "bearer" not in value.lower():
            value = f"Bearer {value}"
        self.__headers["authorization"] = value

    @staticmethod
    def __corrective_url(urls: tuple[str, str]) -> str:
        # print(urls)
        if urls is not None:
            url, baseurl = urls
            baseurl = re.search(
                r"(?<=https://).*", baseurl, re.IGNORECASE
            ).group()  # type:ignore
            baseurl = rf'https://{re.sub(r"\b/\B", "", baseurl)}'
            url = re.sub(r"\B/\b", "", url)
            req_url = f"{baseurl}/{url}"

            return req_url
        return ""

    @staticmethod
    def body(body: dict | list = [], headers: dict = {}) -> Any:
        if len(headers) <= 0:
            headers = whapi.__headers

        def decorator(func: Callable) -> Callable:
            def wrapper(*args: Any, **kwargs: Any) -> None:
                if len(kwargs) <= 0 and len(args) <= 0:
                    res = func(body, headers)
                else:
                    res = func(*args, **kwargs)
                return res

            if isinstance(body, (dict, list)):
                return wrapper
            else:
                raise TypeError("Argument must be type dict or list")

        return decorator

    @staticmethod
    def __main_whapi_func(
        url: str = "", baseurl: str = WH_API_URL, method: Methods = Methods.POST
    ) -> Any:
        headers = whapi.__headers
        req_url = whapi.__corrective_url((url, baseurl))

        def decorator(func: Callable) -> Callable:
            def wrapper(body: dict | list = [], headers: dict = headers) -> Any:
                body_ = body
                if not "authorization" in headers:
                    raise ValueError("headers must have field `authorization`")
                res = None
                match method:
                    case Methods.GET:
                        res = requests.get(req_url, headers=headers, json=body_)
                    case Methods.POST:
                        res = requests.post(req_url, headers=headers, json=body_)
                    case Methods.PUT:
                        res = requests.put(req_url, headers=headers, json=body_)
                    case Methods.DELETE:
                        res = requests.delete(req_url, headers=headers, json=body_)
                assert res is not None
                result = func(res)

                if res.status_code < 300 and res.status_code >= 200:
                    return json.loads(result.text)

                else:
                    # print(
                    #     f"current status code: {res.status_code if res is not None else None}"
                    # )
                    logs.err(
                        f"current status code: {res.status_code if res is not None else None}",
                        __name__,
                    )
                    return json.loads(result.text)

            return wrapper

        return decorator

    @staticmethod
    def get(url: str = "", baseurl: str = WH_API_URL) -> Any:
        return whapi.__main_whapi_func(url, baseurl, Methods.GET)

    @staticmethod
    def post(url: str = "", baseurl: str = WH_API_URL) -> Any:
        return whapi.__main_whapi_func(url, baseurl, Methods.POST)

    @staticmethod
    def put(url: str = "", baseurl: str = WH_API_URL) -> Any:
        return whapi.__main_whapi_func(url, baseurl, Methods.PUT)

    @staticmethod
    def delete(url: str = "", baseurl: str = WH_API_URL) -> Any:
        return whapi.__main_whapi_func(url, baseurl, Methods.DELETE)


# @whapi.body(body=payload)
# @whapi.post("/messages/text")
# def send_message(result: Any) -> Any:
#     return result


# @whapi.body()
# @whapi.get(f"/settings/events")
# def get_message(result: Any) -> Any:
#     return result
