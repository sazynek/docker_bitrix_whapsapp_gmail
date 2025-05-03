RECURSE_COUNT = "5"  # целые числа, как 123, 321, не  1 2 3 или 3.21 или 3,21(`число` указывает на то, сколько раз будет запускаться програма после ошибки.)
MAIN_DIRECTORY_FOR_ALL_FILES = "./data"

# настройки для расписания
TIMER_TYPE = "minutes"  # seconds, minutes, hours, day, weeks(`вылечины`)
TIMER = "2"  # целые числа, как 123 или 2222, не 1 2 3, 2.222 или 2,222(здесь мы указываем `интервал` работы)
START_PARSING_FROM_THE_BEGINNING =  "False"  # запишите `True` или `False`(логические значения да или нет)


REPLACE_CURRENT_WORKS_OF_SCRIPT_NEW_WORKS =  "False"  # запишите `True` или `False`(логические значения да или нет)


FILTER_TO_SORT_ITEMS = "rating"  # rating, censor, years

# работа с отдельными запросами по страницам
CUSTOM_REQUEST_URLS = ""  # rating, censor, years
CUSTOM_REQUEST_STATE =  "False"  # запишите `True` или `False`(логические значения да или нет)

MOVE_CUSTOM_REQUEST_TO_MAIN_DIRECTORY = "False"  # стандартная папка MAIN_DIRECTORY_FOR_ALL_FILES('./data'), запишите `True` или `False`(логические значения да или нет)
CUSTOM_REQUEST_DIRECTORY_PATH = "./custom"  # стандартная папка MAIN_DIRECTORY_FOR_ALL_FILES('./data'),если не указано значение, вы моежете указать свою(например: './my_papka/eche_my_papka/eche_odna')

PARSE_ONE_TIME = "True"  # запускает парсер единажды, запишите `True` или `False`(логические значения да или нет)

REMOVE_ONE_FILE = "False"
REMOVE_ONE_FILE_FULLPATH_TO_DIR = "D:\\torrent_game\\codes\\allProjects\\__python__\\openai_CLI\\data\\реинкарнация. предсмертные муки, 2024,"
SLEEP_TIME_AFTER_REQUEST_FAILED = "3, 7"
SORTED_WITHOUT_PARSE = "rating, False"  # rating, censor, years и после запятой `True` или False
WHATS_APP_ON='False'

PROXY = ""
# Example: python @restartAll true @recurse 7 @sleep 2,2