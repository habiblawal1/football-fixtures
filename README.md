# 📋 Powerleague Fixture Fetcher (`getFixtures.py`)

This Python script fetches the **next match fixture** for a specific Powerleague football team, displays the **opponent**, their **current league position**, the **fixture time in 12-hour format**, and a formatted **9-player list** with your captain.

---

## 🚀 Features

- ✅ Scrapes the latest fixtures from Powerleague  
- ✅ Identifies your team's next scheduled match  
- ✅ Extracts the opponent and their current table position  
- ✅ Formats the fixture time to 12-hour format (e.g. `7:40pm`)  
- ✅ Outputs a 9-player matchday list (with the captain hardcoded as `Habib`)  

---

## 🛠️ Installation

### 1. Clone or download the script

Place the `getFixtures.py` file in your project directory.

### 2. Install required Python libraries

```bash
pip install requests beautifulsoup4
```

## ▶️ Usage

To run the script, use:

```bash
python getFixtures.py
```

Make sure you're connected to the internet, as the script fetches live fixture and league data from Powerleague's website.

## 📤 Example Output

```
Monday 6aside Harris League vs SAVILLES 6 (1st place) @ 7:40pm
1. Habib
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

🔹 **getNextFixture(yourTeam)**
Finds your team's next scheduled match and opponent. Passes the details to the display function.

🔹 **get_table_position(soup, team_name)**
Searches the standings table and retrieves the opponent's current league position.

🔹 **print_next_fixture(opponent, fixture_time, opp_table_pos)**
Prints the formatted fixture message and player list.

🔹 **print_player_list()**
Prints numbers 1 through 9, with Habib as the named player in the first spot.

🔹 **format_time_12h(time_str)**
Converts 24-hour clock format like 19:40 to 12-hour format 7:40pm.

🔹 **num_to_ordinal(n)**
Formats league positions: 1 becomes 1st, 2 → 2nd, etc.

## 🧠 Notes

The team name is currently set as:

```python
myTeam = "AC Me Rol1in"
```

You can change this at the bottom of the script.

The captain name is hardcoded as "Habib". You can modify the captain variable in print_player_list().

If the script cannot find the fixture or opponent's table position, it will exit with a clear error message.

The script relies on Powerleague's page structure — if the site changes, the scraping logic may need to be updated.