#!/usr/bin/env python3
"""
Sends a fixed/static message to a Telegram chat via the Telegram Bot API.

Uses only the Python standard library (urllib) so there is nothing extra
to install in the GitHub Actions runner.

Credentials are read from environment variables so nothing sensitive is
hard-coded in this file:

  TELEGRAM_BOT_TOKEN  - the token @BotFather gave you, e.g. 123456:ABC-DEF...
  TELEGRAM_CHAT_ID    - the numeric chat ID to send to

Locally you can set these in your shell before running:
  export TELEGRAM_BOT_TOKEN="123456:ABC-DEF..."
  export TELEGRAM_CHAT_ID="123456789"
  python3 send_telegram.py

On GitHub Actions these are pulled from repository Secrets (see the
workflow file and README for setup steps).
"""

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

MESSAGE_TEMPLATE = (
    "This is an automated message sent every 30 minutes.\n\n"
    "Sent at: {timestamp} UTC"
)


def main() -> int:
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    missing = [
        name
        for name, val in (
            ("TELEGRAM_BOT_TOKEN", bot_token),
            ("TELEGRAM_CHAT_ID", chat_id),
        )
        if not val
    ]
    if missing:
        print(f"ERROR: missing required environment variable(s): {', '.join(missing)}", file=sys.stderr)
        return 1

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    text = MESSAGE_TEMPLATE.format(timestamp=timestamp)

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = json.dumps({"chat_id": chat_id, "text": text}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        if not body.get("ok"):
            print(f"ERROR: Telegram API returned an error: {body}", file=sys.stderr)
            return 1
        print(f"Message sent successfully to chat {chat_id} at {timestamp} UTC")
        return 0
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        print(f"ERROR: HTTP {exc.code} from Telegram API: {detail}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001 - want to log any failure clearly in CI logs
        print(f"ERROR: failed to send Telegram message: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
