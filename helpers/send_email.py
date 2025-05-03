import os
import smtplib as smtp
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from functools import wraps
from time import sleep
from types import NoneType
from typing import Any, Callable

from helpers.bitrix_ import Bitrix_
from helpers.custom_logger import logs
from tokens.tokens import GMAIL, PASSWORD_GMAIL


async def sent_gmail(
    to: str,
    subject: str,
    body: str,
    files: tuple[str, ...] | str | None = None,
    google: bool = True,
    recurse: int = 3,
) -> None:
    # logs.info(f"we restart send gmail. Recurse count: {recurse}", __name__)
    logs.info(f"we restart send gmail. Recurse count: {recurse}", __name__)
    if google and recurse >= 0:
        try:
            if isinstance(files, tuple):
                files_core = [
                    file for file in files if os.path.exists(file) and file is not None
                ]
            else:
                files_core = (
                    files
                    if files is not None and os.path.exists(files)
                    else None  # type:ignore
                )
            files_ = (
                None
                if files_core is None
                else (files_core,) if isinstance(files_core, str) else files_core
            )
            server = smtp.SMTP("smtp.gmail.com", 587)

            msg = MIMEMultipart()
            msg["From"] = Header(GMAIL)  # type:ignore
            msg["To"] = Header(to)  # type:ignore
            msg["Subject"] = Header(subject)  # type:ignore
            msg.attach(MIMEText(body, "plain", "utf-8"))
            if files_ is not None:
                for file in files_:
                    with open(file, "rb") as frb:
                        attachedfile = MIMEApplication(frb.read())  # type:ignore
                        attachedfile.add_header(
                            "content-disposition", "attachment", filename=frb.name
                        )
                        msg.attach(attachedfile)
            server.starttls()
            server.login(GMAIL, PASSWORD_GMAIL)
            server.sendmail(GMAIL, to, msg.as_string())
            server.quit()
        except Exception as e:
            timer = 5
            sleep(timer)
            logs.debug(
                f"email can't send, we try to restart send him after {timer} seconds. Recurse count: {recurse}",
                __name__,
            )
            await sent_gmail(to, subject, body, files, google, recurse - 1)
    elif recurse <= 0:
        logs.warn(
            f"we can't send message. Check logs. Recurse: {recurse}/Google: {google}",
            __name__,
        )
        raise ValueError(
            f"we can't send message. Check logs. Recurse: {recurse}/Google: {google}"
        )
    else:
        logs.warn(
            f"sorry, but we support only google mail(email). Google:{google}", __name__
        )


def gmail(
    to: str,
    subject: str,
    body: str,
    files: tuple[str, ...] | str | None = None,
    google: bool = True,
    recurse: int = 3,
) -> Callable:
    assert isinstance(body, (NoneType, str))
    assert isinstance(to, str)

    def wrapper(func: Callable) -> Any:
        @wraps(func)
        async def wrapper_inner(*args: Any, **kwargs: Any) -> Any:
            res = await func(*args, **kwargs)
            if res:
                try:
                    await sent_gmail(to, subject, body, files, google, recurse)
                    logs.info("SENT EMAIL", __name__)
                except Exception as e:
                    logs.err(f"cannot sent email {e}", __name__)
                try:
                    await Bitrix_()()
                    logs.info("SENT BITRIX", __name__)
                except Exception as e:
                    logs.err(f"cannot sent BITRIX {e}", __name__)

        return wrapper_inner

    return wrapper
