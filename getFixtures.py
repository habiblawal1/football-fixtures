import requests

# helps retrieve our environmen variables
import os
import sys

# smtplib handles sending emails
import smtplib

# MIMEText & MIMEMultipart helps format the emails we send
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# loads variables from .env
from dotenv import load_dotenv

from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# ─── Configuration ──────────────────────────────────────────────────────────────
SCRIPT_DIR   = os.path.dirname(__file__)
FLAG_FILE    = os.path.join(SCRIPT_DIR, "last_fixture_run.log")
TEAM         = "AC Me Rol1in"        # customise as needed
FIXTURES_URL = "https://www.powerleague.com/league?league_id=fc705d00-05d4-c09b-db14-fa41402f1258&division_id=fc705d00-05d4-c09b-db14-fa4100d25e58"
# ─── End Configuration ──────────────────────────────────────────────────────────

def should_run(window_days: int = 6) -> bool:
    """Return True if the script hasn’t run in the past `window_days` days."""
    if not os.path.exists(FLAG_FILE):
        return True
    last_mod = datetime.fromtimestamp(os.path.getmtime(FLAG_FILE))
    return (datetime.now() - last_mod) > timedelta(days=window_days)

def update_flag() -> None:
    """Edit the flag file to mark ‘just ran’."""
    with open(FLAG_FILE, "w") as f:
        f.write(f"Last run at: {datetime.now().isoformat()}")

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

        print("Email Sent Succesfully!")

    except Exception as e:
        print(f"#####\nError sending mail:\n\n {e}\n#####")


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
    send_email(subject, fixtures_string)
    update_flag()


if __name__ == "__main__":
    print("\nScript triggered at", datetime.now())
    if not should_run():
        print("Script already ran this week. Exiting.")
        sys.exit(0)
    get_next_fixture()
