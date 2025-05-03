import os
from asyncio import sleep
from time import sleep as t_sleep

from playwright.async_api import BrowserContext, Page

from helpers.custom_logger import logs
from helpers.global_func import write_cookies
from sys_argv.sys_argv import PARSE_ONE_TIME
from tokens.tokens import LOGIN_NAME, PASSWORD


async def register(page: Page, context: BrowserContext) -> bool:
    global PARSE_ONE_TIME
    await context.clear_cookies()
    if not os.path.exists("main_cook.json"):
        PARSE_ONE_TIME = "False"
    # await stealth_async(page)
    await page.goto("https://hd.kinopoisk.ru/", wait_until="domcontentloaded")

    all_a_teg = await page.locator("div > a").all()
    try:
        log_btn = [
            (await i.inner_text(), i)
            for i in all_a_teg
            if "Войти" in await i.inner_text()
        ][0]
        await log_btn[1].click()
        # print("account start to registering")
        logs.info("account start to registering", __name__)
        await sleep(3)
        await page.locator('a[id="passp:exp-register"]').click()
        await page.locator(
            "ul.RegistrationButtonPopup-list",
        ).get_by_text("Войти по логину").click()
        await page.locator(
            'span.Textinput > input[placeholder="Логин или email"]',
        ).click()
        await page.keyboard.insert_text(text=str(LOGIN_NAME))
        await page.keyboard.press(key="Enter")
        page.set_default_timeout(timeout=3000.0)
        t_sleep(3)
        try:
            code_msg = page.locator(
                'span.Textinput > input[data-t="field:input-pushCode"]'
            )
            # print(page.url)
            logs.info(f"page: {page.url}", __name__)
            input_res = input("Enter code from message on your phone:")
	    print("Enter code from message on your phone:")
            await code_msg.click()
            await page.keyboard.insert_text(text=input_res.strip().lower())
        except Exception as e:
            logs.warn("register is was not successfully ")
        try:
            password = page.locator(
                'div.Field-inputWrapper > span.Textinput  > input[data-t="field:input-passwd"]'
            )
            await password.click()
            await page.keyboard.insert_text(PASSWORD)
            await page.keyboard.press(key="Enter")

        except Exception as e:
            logs.warn("register is was not successfully ")
        t_sleep(5)
        if not os.path.exists("main_cook.json"):
            cook = await context.cookies()
            for i in cook:
                if "name" in i:
                    name = i["name"]
                    if len(name) > 0 and "yandex_login" in name and "value" in i:
                        value = i["value"]
                        if len(value) > 0:
                            await write_cookies(
                                cookies=str(cook), file_name="main_cook.json"
                            )
                        else:
                            logs.warn("register is was not successfully ")
        t_sleep(1)
        return False
    except IndexError as e:
        if "captcha" in page.url:
            # print("captcha")
            try:
                await page.locator('input[id="js-button"]').click()
            except Exception:
                pass
            await sleep(4)
            logs.info(f"captcha: on", __name__)
            raise RecursionError("recurse")
        else:
            # print("account has been registered")
            logs.info("account has been registered", __name__)
        t_sleep(1)
        return True
