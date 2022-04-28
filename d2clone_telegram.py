#!/usr/bin/env python
import os

import requests
from telegram import Update, ParseMode
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

    def html_text(self, region=None, ladder=None, hardcore=None):
        text = ""
        for key, value in self.progress.items():
            if filtered(key, region, ladder, hardcore):
                text += f"<b>[{value}/6]</b> {Regions.TEXT[key[0]]} {Ladder.TEXT[key[1]]} {Hardcore.TEXT[key[2]]}\n"
        text += "<i>Data courtesy of diablo2.io</i>"
        return text


def filtered(key, region, ladder, hardcore):
    return (
        (not region or key[0] == region)
        and (not ladder or key[1] == ladder)
        and (not hardcore or key[2] == hardcore)
    )


def parse_args(args):
    region = None
    ladder = None
    hardcore = None

    if any("am" in arg for arg in args):
        region = Regions.AMERICAS
    if any("eu" in arg for arg in args):
        region = Regions.EUROPE
    if any("asi" in arg for arg in args):
        region = Regions.ASIA

    if any("non" in arg for arg in args):
        ladder = Ladder.NON_LADDER
    if any("ladder" in arg for arg in args) and not any("non" in arg for arg in args):
        ladder = Ladder.LADDER

    if any("hard" in arg for arg in args):
        hardcore = Hardcore.HARDCORE
    if any("soft" in arg for arg in args):
        hardcore = Hardcore.SOFTCORE

    return region, ladder, hardcore


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "<b>Stay awhile and listen!</b>\n"
        "Use /uberdiablo to check Diablo Clone Tracker\n"
        "Add filters with <code>/uberdiablo softcore non-ladder americas</code>\n"
        "<i>Data courtesy of diablo2.io</i>",
        parse_mode=ParseMode.HTML,
    )


def uber_diablo(update: Update, context: CallbackContext) -> None:
    lower_args = [arg.lower() for arg in context.args]
    region, ladder, hardcore = parse_args(lower_args)

    dclone_tracker = DCloneTracker()
    dclone_tracker.update()

    message = dclone_tracker.html_text(region=region, ladder=ladder, hardcore=hardcore)

    if update.message:
        update.message.reply_text(message, parse_mode=ParseMode.HTML)


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
