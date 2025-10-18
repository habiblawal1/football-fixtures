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

1. Make script file executable

   ```bash
   chmod +x </path/to/your/football-fixtures>/scripts/run_get_fixtures.sh
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

This script can be automated using macOS's native scheduler, launchd. You can schedule it to run every Friday at 12:00 PM.

### 1. Create a .plist file

Save this file as:
~/Library/LaunchAgents/com.getfixtures.plist

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
   "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.getfixtures</string>

    <!-- Run the wrapper script (use /bin/bash and the script path) -->
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>/Users/habiblawal/GitHub/football-fixtures/scripts/run_get_fixtures.sh</string>
    </array>

    <!-- Schedule: Friday (weekday 6) at 9:00 -->
    <key>StartCalendarInterval</key>
    <dict>
        <key>Weekday</key>
        <integer>6</integer>
        <key>Hour</key>
        <integer>9</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>

    <!-- If the machine is asleep at 9:00 this StartInterval acts as a fallback retry -->
    <key>StartInterval</key>
    <integer>3600</integer>

    <!-- Run once when the job is loaded (i.e. at boot/login) -->
    <key>RunAtLoad</key>
    <true/>

    <!-- Log files -->
    <key>StandardOutPath</key>
    <string>/Users/habiblawal/GitHub/football-fixtures/launchd.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/habiblawal/GitHub/football-fixtures/launchd-error.log</string>
</dict>
</plist>
```

📝 Replace:

- `/path/to/python` with the path to your Python binary (`which python`)
- `/path/to/your/football-fixtures` with your project directory

### 2. Load the launch agent

```bash
launchctl unload ~/Library/LaunchAgents/com.getfixtures.plist 2>/dev/null || true
launchctl load ~/Library/LaunchAgents/com.getfixtures.plist
```

To test it manually:

```bash
launchctl start com.getfixtures
```

To reload after edits:

```bash
launchctl unload ~/Library/LaunchAgents/com.getfixtures.plist
launchctl load ~/Library/LaunchAgents/com.getfixtures.plist
```

To check logs:

```bash
tail -f /path/to/your/football-fixtures/launchd.log
```

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
