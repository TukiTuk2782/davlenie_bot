# Blood Pressure Telegram Bot

Telegram bot for recording blood pressure measurements into Google Sheets.

## Configuration

Profiles are configured in `users.json` under the `users` list. Each enabled profile
contains:

- `name`: profile name shown in bot messages.
- `enabled`: when `false`, the profile is skipped.
- `telegram_id`: Telegram user ID allowed to use this profile.
- `bot_token`: Telegram bot token.
- `spreadsheet_id`: Google Sheets document ID used as the pressure journal.
- `group_id`: chat ID where saved measurement reports are sent.
- `service_account_file`: optional path to Google service account credentials.

Multiple enabled profiles may share the same `bot_token`. The app starts one
Telegram polling session per unique token and routes private messages to profiles
by `telegram_id`. The pair `bot_token + telegram_id` must be unique.

## Usage

Run locally with the project virtual environment:

```bash
.venv/bin/python main.py
```

Supported private-chat commands:

- `/start`: shows the active profile name and available commands.
- `/add`: starts pressure entry.
- `/ref`: returns the Google Sheets journal link for the current profile.
- `/cancel`: cancels the current entry flow.
- `/get_id`: returns the current chat ID and Telegram user ID.

The bot ignores incoming group chat messages. It still sends measurement reports
to the configured `group_id` after a successful save.

## Validation

Basic syntax check:

```bash
.venv/bin/python -m py_compile config.py handlers.py main.py sheets.py states.py
```
