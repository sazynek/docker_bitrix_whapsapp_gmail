from helpers.global_func import find_env_file

WH_API_TOKEN, WH_API_URL = find_env_file("WH_API_TOKEN"), find_env_file("WH_API_URL")


LOGIN_NAME, PHONE, PASSWORD = (
    find_env_file("LOGIN_NAME"),
    find_env_file("PHONE"),
    find_env_file("PASSWORD"),
)

PORT, HOST, CHAT_ID = (
    int(find_env_file("PORT")),
    find_env_file("HOST"),
    find_env_file("CHAT_ID"),
)
GMAIL, PASSWORD_GMAIL, TO = (
    find_env_file("GMAIL"),
    find_env_file("PASSWORD_GMAIL"),
    find_env_file("TO"),
)

webhook = find_env_file("WEBHOOK")
