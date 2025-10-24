import requests

# helps retrieve our environmen variables
import os
import sys

# Debug: (moved) will log where this script ran from and which python executed it when run under launchd

# smtplib handles sending emails
import smtplib

# MIMEText & MIMEMultipart helps format the emails we send
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# loads variables from .env
from dotenv import load_dotenv

from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import Optional
import json

# ─── Configuration ──────────────────────────────────────────────────────────────
SCRIPT_DIR   = os.path.dirname(__file__)
FLAG_FILE    = os.path.join(SCRIPT_DIR, "last_fixture_run.log")
TEAM         = "AC Me Rol1in"        # customise as needed
# You can customise FIXTURES_URL if needed. Keep a valid URL here.
FIXTURES_URL = "https://www.powerleague.com/league?league_id=95c0a561-3a86-aa83-e014-e4a7c0838ce5&division_id=95c0a561-3a86-aa83-e014-e4a7583dc7e5"
# ─── End Configuration ──────────────────────────────────────────────────────────

# Write a small startup debug entry to the project log so launchd runs are visible
try:
    with open(os.path.join(os.path.dirname(__file__), "launchd.log"), "a") as _log:
        _log.write(f"getFixtures.py running: file={__file__} python={sys.executable} cwd={os.getcwd()}\n")
except Exception:
    # If logging fails, continue silently
    pass

SCHEDULE_WEEKDAY = 4  # Friday (Monday=0)
SCHEDULE_HOUR = 9
SCHEDULE_MINUTE = 0


def _scheduled_datetime_for_week(now: Optional[datetime] = None) -> datetime:
    """Return the scheduled datetime (this week's Friday at 09:00) for `now`.

    This uses local (naive) datetimes consistent with how the script is run.
    """
    now = now or datetime.now()
    # Compute how many days until Friday of the current week
    days_ahead = SCHEDULE_WEEKDAY - now.weekday()
    # If days_ahead is negative, this computes a date earlier in the week
    friday = now + timedelta(days=days_ahead)
    return datetime(friday.year, friday.month, friday.day, SCHEDULE_HOUR, SCHEDULE_MINUTE)


def _read_flag() -> Optional[dict]:
    """Read JSON flag file and return its payload, or None if missing/invalid."""
    if not os.path.exists(FLAG_FILE):
        return None
    try:
        with open(FLAG_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return None


def should_run(window_days: int = 6) -> bool:
    """Return True only if the scheduled time this week has passed and
    we haven't already recorded a successful run in this ISO week.

    Behavior:
    - If now < this week's Friday 09:00 -> don't run.
    - If no flag present and now >= scheduled time -> run.
    - If flag is present and its ISO week matches this week -> don't run.
    - Otherwise -> run.
    """
    now = datetime.now()
    sched = _scheduled_datetime_for_week(now)

    # Only allow running once the scheduled time this week has passed.
    if now < sched:
        return False

    flag = _read_flag()
    if not flag:
        return True

    last_iso = tuple(flag.get("iso_year_week", ()))
    this_iso = now.isocalendar()[:2]
    if last_iso == this_iso:
        return False

    return True

def update_flag() -> None:
    """Atomically write a JSON flag recording the successful run.

    Payload example: {"timestamp": "...", "iso_year_week": [2025, 43]}
    """
    now = datetime.now()
    payload = {"timestamp": now.isoformat(), "iso_year_week": now.isocalendar()[:2]}
    tmp = FLAG_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(payload, f)
    os.replace(tmp, FLAG_FILE)

def getFixturePageHTML():
    # Send a GET request to the URL
    response = requests.get(FIXTURES_URL)
    if response.status_code != 200:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        exit()

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")
    return soup


def num_to_ordinal(n):
    """Convert an integer to its ordinal string (e.g., 1 -> 1st)."""
    n = int(n)
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def format_time_12h(time_str):
    """Convert 24-hour time (e.g., '19:40') to 12-hour format (e.g., '7:40pm')."""
    time_str = time_str.strip()  # remove any leading/trailing whitespace
    try:
        return (
            datetime.strptime(time_str, "%H:%M").strftime("%I:%M%p").lstrip("0").lower()
        )
    except ValueError:
        print(
            f"Failed to convert time: '{time_str}' — falling back to original format."
        )
        return time_str


def create_player_list_string():
    """Print the 9-player list with 'Habib' in the 1st position."""
    captain = "Habib"
    player_list = ""
    for i in range(1, 10):
        name = captain if i == 1 else ""
        player_list += f"{i}. {name}\n"
    return player_list


def next_fixture_string(opponent, fixture_time, opp_table_pos):
    """Format and print the next fixture details."""
    position_str = f"{num_to_ordinal(opp_table_pos)} place"
    time_12hr = format_time_12h(fixture_time)
    fixture_details = (
        f"Monday 6aside Harris League vs {opponent} ({position_str}) @ {time_12hr}\n"
    )
    player_list = create_player_list_string()
    return fixture_details + player_list


def get_table_position(soup, team_name):
    # Find the standings table wrapper
    standings_wrapper = soup.find("div", class_="League__Current__Standings")
    if not standings_wrapper:
        print("Failed to parse the table standings in the html.")
        exit()

    # Loop through all rows in the standings
    rows = standings_wrapper.find_all("tr")
    for row in rows:
        columns = row.find_all("td")
        if len(columns) >= 2:
            pos_cell = columns[0]
            team_cell = columns[1]

            team_link = team_cell.find("a", class_="team-link")
            pos_span = pos_cell.find("span")

            if team_link and pos_span:
                name = team_link.get_text(strip=True)
                if name.lower() == team_name.lower():
                    return pos_span.get_text(strip=True)

    print(f"Can't find {team_name}'s position in the table.")
    exit()


def send_email(subject, body):
    load_dotenv()

    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587

    EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
    RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")
    PASSWORD = os.getenv("APP_PASSWORD")

    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = RECIPIENT_EMAIL
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, PASSWORD)
            server.sendmail(EMAIL_ADDRESS, RECIPIENT_EMAIL, msg.as_string())

        print("Email Sent Successfully!")
        return True

    except Exception as e:
        print(f"#####\nError sending mail:\n\n {e}\n#####")
        return False


def get_next_fixture():
    soup = getFixturePageHTML()
    # Find all rows under the Next Games section
    rows = soup.find_all("tr")

    next_fixture = None

    for row in rows:
        teams = row.find_all("a", class_="team-link")
        time_span = row.find(
            "span", class_="flex items-center justify-center h-5 mx-2 tiny"
        )

        if len(teams) == 2 and time_span:
            team1 = teams[0].get_text(strip=True)
            team2 = teams[1].get_text(strip=True)

            if TEAM in [team1, team2]:
                opponent = team2 if TEAM == team1 else team1
                time = time_span.get_text(strip=True).split(" - ")[0]  # e.g., "19:40"
                next_fixture = {"opponent": opponent, "time": time}
                break

    if (
        not next_fixture
        or not next_fixture.get("opponent")
        or not next_fixture.get("time")
    ):
        print("No upcoming fixture found for ", TEAM)
        exit()
    opp_table_pos = get_table_position(soup, next_fixture["opponent"])
    fixtures_string = next_fixture_string(
        next_fixture["opponent"], next_fixture["time"], opp_table_pos
    )
    print(fixtures_string)
    subject = "Harris League Next Fixture"
    # Only mark the run as successful after the email is sent successfully.
    email_ok = send_email(subject, fixtures_string)
    if email_ok:
        try:
            update_flag()
        except Exception:
            print("Warning: failed to update flag file after successful email")
    else:
        print("Email failed; not updating last_fixture_run.log so job may retry next schedule")


if __name__ == "__main__":
    print("\nScript triggered at", datetime.now())
    if not should_run():
        print("Script already ran this week. Exiting.")
        sys.exit(0)
    get_next_fixture()
