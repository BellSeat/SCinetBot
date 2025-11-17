SCinet Telegram Bot
===================

Small utility bot that keeps the SCinet student volunteers coordinated inside Telegram. It publishes uniform reminders, exposes the help-desk schedule, and provides booth lookup tools via inline queries.

What It Does
------------
- `/hello` – quick sanity check to confirm the bot is alive.
- Inline query (type `@<YourBotName> [query]` in any chat):
  - With no query text, Telegram displays a stack of default cards that include “What to wear today/tomorrow”, “Current/next shift”, and “Today’s schedule”.
  - When text is provided, the bot switches to exhibitor booth search (fuzzy booth name matching and reverse lookup by booth number).

Project Layout
--------------
- `tg.py` – entry point; registers Telegram handlers and runs the polling loop.
- `schedule.py` & `schedule_config.json` – returns the last/current/next shifts and the full schedule for a given day.
- `wear.py` & `wear_config.json` – returns the wardrobe plan for today/tomorrow.
- `booth.py` & `booth.json` – fuzzy booth name search and reverse lookup by booth number.
- `config.json` – stores `{"botToken": "123:ABC"}` for authentication.

Requirements
------------
- Python 3.11+ (needed for `zoneinfo`).
- Packages: `python-telegram-bot>=21`, `fuzzywuzzy[speedup]`, `requests`.
  ```bash
  pip install "python-telegram-bot>=21" "fuzzywuzzy[speedup]" requests
  ```

How to Run
----------
1. Add your bot token to `config.json`.
2. Populate the JSON data files (`schedule_config.json`, `wear_config.json`, `booth.json`) with the latest information.
3. Start the bot locally (or on any host where Python is available):
   ```bash
   python tg.py
   ```
4. In Telegram:
   - Type `@<YourBotName>` to see the default inline cards (wear info + shift info).
   - Type `@<YourBotName> Dell` (or any exhibitor/booth number) to search the booth list.

Hosting Options
---------------
- **Local workstation:** great for testing changes quickly; just run `python tg.py` in a terminal and keep it alive during development.
- **AWS EC2 instance:** deploy the repo to a small instance, install the dependencies, and keep the bot online 24/7.
  - I use a simple `systemd` service file (e.g., `/etc/systemd/system/scinet-bot.service`) that runs `python /opt/scinet/tg.py`, restarts the bot on failure, and hooks into EC2’s boot process so the bot starts automatically.
  - After placing the service file, run `sudo systemctl daemon-reload`, then `sudo systemctl enable --now scinet-bot` to keep it managed by systemd.
  - Update the JSON config files on the instance and `sudo systemctl restart scinet-bot` whenever data changes.

Updating Data
-------------
- Edit the JSON files whenever the schedule, wardrobe plan, or exhibitor list changes.
- Restart `tg.py` to reload the files.
- For timezone changes, set the `timezone` argument in `schedule.Schedule`.

Troubleshooting
---------------
- If the bot does not start, confirm the token and that inline mode is enabled in BotFather (`/setinline`).
- Inline queries require the bot to be added to the chat and may take a second to return results due to fuzzy searching.
