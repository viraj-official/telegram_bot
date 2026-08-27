# Automated 30-minute Telegram message (GitHub Actions + Telegram Bot API)

Sends a fixed message to a Telegram chat every 30 minutes, for free, using a
GitHub Actions scheduled workflow — no server to rent or keep alive.

## How it works

- `send_telegram.py` — posts a message to the Telegram Bot API. Uses only Python's standard library (no extra installs needed). Reads credentials from environment variables, nothing sensitive is in the code.
- `.github/workflows/send-telegram.yml` — a GitHub Actions workflow that runs `send_telegram.py` on a `*/30 * * * *` cron schedule (every 30 minutes, UTC), for free, on GitHub's servers.

## One-time setup (about 5 minutes)

### 1. Create a Telegram bot and get its token
1. In Telegram, open a chat with **@BotFather**.
2. Send `/newbot` and follow the prompts (pick a name, then a username ending in `bot`).
3. BotFather replies with a token that looks like `123456789:AAH...`. Copy it — this is your `TELEGRAM_BOT_TOKEN`.
4. Send your new bot at least one message (e.g. "hi") so Telegram creates a chat with it — this is required before the bot can message you back.

### 2. Get your chat ID
1. Open this URL in your browser, replacing `<TOKEN>` with your bot token:
   `https://api.telegram.org/bot<TOKEN>/getUpdates`
2. You should see JSON containing something like `"chat":{"id":123456789,...}`. That number is your `TELEGRAM_CHAT_ID`.
   - If you see `"result":[]` (empty), it means Telegram hasn't seen a message from you yet — go back to step 1.4, send your bot a message, then reload this URL.

### 3. Create a GitHub repository
1. Go to https://github.com/new, create a new repository (private is fine, and recommended).
2. Upload these files to it, keeping the folder structure:
   - `send_telegram.py`
   - `.github/workflows/send-telegram.yml`
   - `README.md` (optional, just for your own reference)

   Easiest way: on your computer, run inside this folder:
   ```
   git init
   git add .
   git commit -m "Add scheduled Telegram message sender"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git push -u origin main
   ```

### 4. Add your secrets to the repo
In your new repo: **Settings → Secrets and variables → Actions → New repository secret**. Add two:

| Secret name | Value |
|---|---|
| `TELEGRAM_BOT_TOKEN` | the token from BotFather, e.g. `123456789:AAH...` |
| `TELEGRAM_CHAT_ID` | the numeric chat ID from step 2 |

Never put these values directly in the code or commit them — GitHub Secrets keeps them encrypted and out of the repo history.

### 5. Test it
Go to the **Actions** tab in your repo → click the "Send scheduled Telegram message" workflow → **Run workflow** (this uses the `workflow_dispatch` trigger, so you don't have to wait for the schedule). Check the run logs and your Telegram chat.

Once that works, it will keep running automatically every 30 minutes without you doing anything else.

## Things worth knowing

- **Timing isn't exact.** GitHub Actions cron schedules are UTC and are *not* guaranteed to fire at the precise minute — under heavy GitHub load, a run can be delayed by several minutes. This is a platform limitation, not a bug in the script.
- **Auto-disable after inactivity.** GitHub automatically disables a scheduled workflow if the repository has had **no commits for 60 days**. If that happens, just push any small commit (or click "Re-enable workflow" in the Actions tab) to turn it back on.
- **Free tier limits.** Scheduled workflows on public repos are unlimited; on private repos they draw from your account's free Actions minutes (2,000 min/month on a free personal account). A run here takes well under a minute, so 30-minute-interval runs cost roughly 1,400–1,500 minutes/month — comfortably within the free quota, but worth knowing if you add more workflows.
- **Telegram rate limits.** Telegram allows roughly 1 message/second to a given chat, and this job sends one message every 30 minutes — nowhere close to any limit.
- **Changing the schedule.** Edit the `cron:` line in `.github/workflows/send-telegram.yml`. Cron format is `minute hour day month weekday`, always UTC — e.g. `0,30 * * * *` and `*/30 * * * *` are equivalent (every :00 and :30).
- **Changing the message content.** Edit `MESSAGE_TEMPLATE` near the top of `send_telegram.py`.
- **Group chats:** if you'd rather post to a Telegram group instead of your personal chat, add the bot to the group, send a message in it, then repeat step 2 — group chat IDs are negative numbers (e.g. `-100123456789`), which is normal.
