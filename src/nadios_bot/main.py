from nadios_bot.consts import TELEGRAM_BOT_API_KEY, PREVIOUS_SHOWS_PATH, \
    REGISTERED_USERS_PATH, REGISTERED_USERS_DEFAULT_VALUE, LOG_FILE_PATH, PREVIOUS_SHOWS_DEFAULT_VALUE
from nadios_bot.telegram_utils import run_bot, get_all_events, save_events
from logging.handlers import RotatingFileHandler
import datetime
import logging
import json
import os


class MissingEnvironmentVariable(Exception):
    pass


def setup_log():
    os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)
    logging.basicConfig(
        format='[%(levelname)-8s] %(asctime)s: %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            RotatingFileHandler(LOG_FILE_PATH, maxBytes=1000000, backupCount=4),
            logging.StreamHandler()
        ])


def setup_data_file(file_path, file_default_data):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    if not os.path.exists(file_path):
        logging.info(f"Can't find {file_path} - Creating it.")
        with open(file_path, 'w') as f:
            json.dump(file_default_data, f)
        return True
    return False


def setup_events_data_file(file_path, file_default_data):
    just_created = setup_data_file(file_path=file_path, file_default_data=file_default_data)
    days_since_modify = (datetime.datetime.now() - datetime.datetime.fromtimestamp(os.path.getmtime(file_path))).days
    if days_since_modify > 7 and not just_created:
        logging.info(f"{file_path} is to old - Override his content.")
        save_events(get_all_events())
    else:
        logging.info(f"The data file already exist.")



def setup_bot():
    logging.info("Starting setup!")
    if TELEGRAM_BOT_API_KEY is None:
        raise MissingEnvironmentVariable(f"TELEGRAM_BOT_API_KEY does not exist")
    setup_data_file(file_path=REGISTERED_USERS_PATH, file_default_data=REGISTERED_USERS_DEFAULT_VALUE)
    setup_events_data_file(file_path=PREVIOUS_SHOWS_PATH, file_default_data=PREVIOUS_SHOWS_DEFAULT_VALUE)

    logging.info("Finish setup successfully!")


def main():
    setup_log()
    try:
        setup_bot()
        run_bot()
    except Exception as e:
        logging.exception("Oh no!")
        raise e


if __name__ == "__main__":
    main()
