# Project Notes

## Runtime

- Python dependencies are listed in `requirements.txt`.
- Use the local virtual environment when available:
  `.venv/bin/python main.py`.
- Basic syntax validation:
  `.venv/bin/python -m py_compile config.py handlers.py main.py sheets.py states.py`.

## Bot Architecture

- `users.json` defines enabled bot profiles.
- `main.py` groups enabled profiles by `bot_token` and starts one polling session
  per unique Telegram bot token.
- `handlers.py` creates one profile router per profile and routes private
  messages by `telegram_id`.
- Profiles sharing a `bot_token` are supported, but `bot_token + telegram_id`
  must remain unique.
- Incoming group chat messages are ignored by handlers. Outgoing report messages
  to each profile's `group_id` are still sent after successful saves.

## External Services

- Google Sheets writes use `gspread` and a service account JSON file.
- `spreadsheet_id` from `users.json` is used both for saving pressure rows and
  for the `/ref` journal link.
