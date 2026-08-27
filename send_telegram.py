#!/usr/bin/env python3
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
    except Exception as exc:
        print(f"ERROR: failed to send Telegram message: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
