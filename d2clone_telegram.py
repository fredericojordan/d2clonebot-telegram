#!/usr/bin/env python
import os

import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

BASE_URL = "https://diablo2.io/dclone_api.php"


class Regions:
    AMERICAS = 1
    EUROPE = 2
    ASIA = 3
    TEXT = {1: "Americas", 2: "Europe", 3: "Asia"}


class Ladder:
    LADDER = 1
    NON_LADDER = 2
    TEXT = {1: "Ladder", 2: "Non-ladder"}


class Hardcore:
    HARDCORE = 1
    SOFTCORE = 2
    TEXT = {1: "Hardcore", 2: "Softcore"}


class SortDirection:
    ASCENDING = "a"
    DESCENDING = "d"


class SortKey:
    PROGRESS = "p"
    REGION = "r"
    LADDER = "l"
    HARDCORE = "h"
    TIMESTAMP = "t"


def get_diablo_tracker(
    region=None, ladder=None, hardcore=None, sort_key=None, sort_direction=None
):
    params = {
        "region": region,
        "ladder": ladder,
        "hc": hardcore,
        "sk": sort_key,
        "sd": sort_direction,
    }
    filtered_params = {k: v for k, v in params.items() if v is not None}
    headers = {"User-Agent": "d2clone-telegram"}
    response = requests.get(BASE_URL, params=filtered_params, headers=headers)
    return response.json() if response.status_code == 200 else None


class DCloneTracker:
    def __init__(self):
        self.progress = {
            (Regions.AMERICAS, Ladder.LADDER, Hardcore.HARDCORE): None,
            (Regions.AMERICAS, Ladder.LADDER, Hardcore.SOFTCORE): None,
            (Regions.AMERICAS, Ladder.NON_LADDER, Hardcore.HARDCORE): None,
            (Regions.AMERICAS, Ladder.NON_LADDER, Hardcore.SOFTCORE): None,
            (Regions.EUROPE, Ladder.LADDER, Hardcore.HARDCORE): None,
            (Regions.EUROPE, Ladder.LADDER, Hardcore.SOFTCORE): None,
            (Regions.EUROPE, Ladder.NON_LADDER, Hardcore.HARDCORE): None,
            (Regions.EUROPE, Ladder.NON_LADDER, Hardcore.SOFTCORE): None,
            (Regions.ASIA, Ladder.LADDER, Hardcore.HARDCORE): None,
            (Regions.ASIA, Ladder.LADDER, Hardcore.SOFTCORE): None,
            (Regions.ASIA, Ladder.NON_LADDER, Hardcore.HARDCORE): None,
            (Regions.ASIA, Ladder.NON_LADDER, Hardcore.SOFTCORE): None,
        }

    def update(self):
        progress_json = get_diablo_tracker()
        updated_statuses = []

        if not progress_json:
            return None
        else:
            for entry in progress_json:
                key = (int(entry["region"]), int(entry["ladder"]), int(entry["hc"]))
                if not self.progress[key] == int(entry["progress"]):
                    if self.progress[key]:
                        updated_statuses.append(key)
                    self.progress[key] = int(entry["progress"])

        return updated_statuses

    def text(self):
        text = ""
        for key, value in self.progress.items():
            text += f"**[{value}/6]** {Regions.TEXT[key[0]]} {Ladder.TEXT[key[1]]} {Hardcore.TEXT[key[2]]}\n"
        text += "> Data courtesy of diablo2.io"
        return text


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Hi! Use /uberdiablo to check Diablo Clone Tracker")


def uber_diablo(update: Update, context: CallbackContext) -> None:
    dclone_tracker = DCloneTracker()
    dclone_tracker.update()
    update.message.reply_text(dclone_tracker.text())


def main() -> None:
    token = os.environ.get("TELEGRAM_TOKEN")
    updater = Updater(token)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", start))
    dispatcher.add_handler(CommandHandler("uberdiablo", uber_diablo))

    updater.start_polling()

    updater.idle()


if __name__ == "__main__":
    if not os.environ.get("TELEGRAM_TOKEN"):
        print("Please set the TELEGRAM_TOKEN environment variable!")
        exit(1)
    else:
        main()
