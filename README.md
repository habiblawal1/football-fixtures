# 📋 Powerleague Fixture Fetcher (`getFixtures.py`)

This Python script fetches the **next match fixture** for a specific Powerleague football team, displays the **opponent**, their **current league position**, the **fixture time in 12-hour format**, and a formatted **9-player list**. It also sends this output to your email and can be fully automated on macOS via `launchd`.

---

## 🚀 Features

- ✅ Scrapes the latest fixtures from Powerleague
- ✅ Identifies your team's next scheduled match
- ✅ Extracts the opponent and their current table position
- ✅ Formats fixture time to 12-hour format (e.g. `7:40pm`)
- ✅ Generates a 9-player matchday list
- ✅ **Sends the output to your email address**
- ✅ **Automatically runs every Friday at 12:00 PM using macOS `launchd`**

---

## 🛠️ Installation

### 1. Clone or download the script

Place the `getFixtures.py` file in your project directory.

### 2. Install required Python libraries

Using virtualenv is prefererable because it isolates project dependencies and prevents version conflicts.

1. Runs module that creates and manages your virtual environment inside the .venv folder

   ```bash
   python3 -m venv .venv
   ```

1. Sets your current shell to use the Python and pip inside .venv instead of the system-wide ones.

   ```bash
   source .venv/bin/activate
   ```

1. Install dependencies inside the new venv

   ```bash
   pip install -r requirements.txt
   ```

### 3. Create a .env file

In the same directory, create a .env file with your email credentials:

```ini
EMAIL_ADDRESS=youremail@gmail.com
APP_PASSWORD=your_gmail_app_password
RECIPIENT_EMAIL=teammate@example.com
```

🛡️ Do not commit this file. Your .gitignore should include .env.

## ▶️ Usage

To run the script manually:

```bash
python getFixtures.py
```

You'll see the fixture printed in the terminal and emailed to your recipient.

## ⏰ Automate with launchd (macOS)

This repo includes a recommended `launchd` setup that runs the job every Friday at 09:00 local time and — if the laptop was off at that time — will run once when the agent is loaded at next login/boot.

Important behavior notes (implemented in the script):

- The script's `should_run()` only allows a run when the current time is at-or-after this week's scheduled datetime (Friday 09:00) and there is no recorded successful run for the current ISO week.
- The script records a successful run by writing a small JSON payload to `last_fixture_run.log` — and it only writes that payload after the email has been successfully sent. This prevents duplicate successful emails in the same week while allowing a missed-schedule run to happen at next boot.

### Files included

- `scripts/run_get_fixtures.sh` — wrapper that cds to the project, uses `.venv` Python if present, and logs debug output to `launchd.log`/`launchd-error.log`.
- `schedulers/launchd/com.getfixtures.plist` — recommended plist you can copy to `~/Library/LaunchAgents`.

### 1. Make the wrapper executable.

Ensure you **include the path to the football-fixtures repo** in the placeholder

```bash
chmod +x </path/to/your/football-fixtures>/scripts/run_get_fixtures.sh
```

### 2. Install the plist for your user

Copy the plist from the repo into your LaunchAgents folder and load it Ensure you **include the path to the football-fixtures repo** in the placeholder:

```bash
cp </path/to/your/football-fixtures>/schedulers/launchd/com.getfixtures.plist ~/Library/LaunchAgents/com.getfixtures.plist
```

```bash
launchctl unload ~/Library/LaunchAgents/com.getfixtures.plist 2>/dev/null || true
```

```bash
launchctl load ~/Library/LaunchAgents/com.getfixtures.plist
```

To test run immediately:

```bash
launchctl start com.getfixtures
```

To reload the agent after you edit the plist:

```bash
launchctl unload ~/Library/LaunchAgents/com.getfixtures.plist
```

```bash
launchctl load ~/Library/LaunchAgents/com.getfixtures.plist
```

### 3. Logs & debugging

Tail the project logs to see what happened during a launchd run:

```bash
tail -f /Users/habiblawal/GitHub/football-fixtures/launchd.log /Users/habiblawal/GitHub/football-fixtures/launchd-error.log
```

The wrapper writes debug info (cwd, python executable) to `launchd.log` so you can confirm the same interpreter and script copy were used.

### 4. Common issues

- If the job runs repeatedly (e.g. hourly), ensure your plist does not contain a `StartInterval` key — the included plist intentionally omits it.
- If the job appears to run but nothing happens, check that `scripts/run_get_fixtures.sh` is executable and that the wrapper's Python has the required packages installed (activate `.venv` or install deps into the target interpreter).
- If email fails, the script will NOT update `last_fixture_run.log` — that allows the job to retry on the next scheduled Friday (or on next boot if the scheduled time was missed).

### 5. Why this meets the requirement

- Scheduled weekly at Friday 09:00 via `StartCalendarInterval`.
- `RunAtLoad` causes the agent to run at login/boot, but the script's `should_run()` prevents an early run unless the scheduled Friday 09:00 has already passed — so login on Monday won’t trigger an early run.
- The JSON flag records successful runs only after the email is sent, so failures don't incorrectly block future retries.

## 📤 Example Output

```
Monday 6aside Harris League vs SAVILLES 6 (1st place) @ 7:40pm
1.
2.
3.
4.
5.
6.
7.
8.
9.
```

## 🔍 How It Works

🔹 **getFixturePageHTML()**  
Fetches and parses HTML from the Powerleague fixture page.

🔹 **get_next_fixture(yourTeam)**  
Finds your team's next scheduled match, opponent, and time. Formats the output and sends it by email.

🔹 **get_table_position(soup, team_name)**  
Searches the standings and retrieves the opponent's league position.

🔹 **next_fixture_string(...)**  
Returns the formatted string combining match info and the player list.

🔹 **send_email(subject, body)**  
Uses Gmail's SMTP server and .env credentials to email the fixture to your team.

🔹 **create_player_list_string()**  
Builds the 9-player matchday list (customisable to include player names if desired).

🔹 **format_time_12h() / num_to_ordinal()**  
Formats the fixture time and opponent's league rank for display.

## 🧠 Notes

Enable App Passwords for Gmail to send emails securely.

The script depends on Powerleague's current page structure — future changes to the site may require updating the scraping logic. You will need to update the `fixturesUrl` variable. The current URL is listed below:

```python
fixturesUrl = "https://www.powerleague.com/league?league_id=fc705d00-05d4-c09b-db14-fa41402f1258&division_id=fc705d00-05d4-c09b-db14-fa4100d25e58"
```

You can modify the team name (myTeam) and customise the player list inside the script.

The team name is currently set as:

```python
myTeam = "AC Me Rol1in"
```

You can change this at the bottom of the script.

The captain name is hardcoded as `Habib`. You can modify the captain variable in print_player_list().

If the script cannot find the fixture or opponent's table position, it will exit with a clear error message.
