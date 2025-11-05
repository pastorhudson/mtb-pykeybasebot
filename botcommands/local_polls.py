import pandas as pd
import requests
import zipfile
import io
from prettytable import PrettyTable


def get_local_poll(search_term=None):
    """
    Get local poll results from Fayette County, PA

    Args:
        search_term: Optional search term to filter races/candidates.
                    Searches both contest names and candidate names.
                    If None, lists all available races.
    """
    # Get the current version number
    print("Fetching current version...")
    version_url = "https://results.enr.clarityelections.com/PA/Fayette/125144/current_ver.txt"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    }

    version_response = requests.get(version_url, headers=headers)
    version_response.raise_for_status()
    current_version = version_response.text.strip()

    print(f"Current version: {current_version}")

    # Construct the download URL with the current version
    url = f"https://results.enr.clarityelections.com//PA/Fayette/125144/{current_version}/reports/summary.zip"

    # Download the zip file
    print("Downloading zip file...")
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    # Extract the CSV from the zip file
    print("Extracting CSV from zip...")
    with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
        with zip_file.open('summary.csv') as csv_file:
            df = pd.read_csv(csv_file)

    print("Data loaded successfully!\n")

    # If no search term provided, list all available races
    if search_term is None:
        return list_all_races(df)

    # Search for matching races (case-insensitive)
    search_lower = search_term.lower()

    # First try to match contest names
    contest_matches = df[df['contest name'].str.lower().str.contains(search_lower, na=False)]

    # Also try to match candidate names
    candidate_matches = df[df['choice name'].str.lower().str.contains(search_lower, na=False)]

    # Combine and get unique contests
    all_matches = pd.concat([contest_matches, candidate_matches]).drop_duplicates()

    if len(all_matches) == 0:
        return f"No races or candidates found matching '{search_term}'\n\nUse get_local_poll() with no arguments to see all available races."

    # Get unique contest names from matches
    unique_contests = all_matches['contest name'].unique()

    # Display results for each matching contest
    msg = ""
    for contest_name in unique_contests:
        msg += display_race_results(df, contest_name)
        msg += "\n"

    return msg


def list_all_races(df):
    """List all available races in the data"""
    msg = "```\n"
    msg += "AVAILABLE RACES\n"
    msg += "=" * 80 + "\n\n"

    unique_contests = df['contest name'].unique()

    table = PrettyTable()
    table.field_names = ["#", "Race Name"]
    table.align["#"] = "r"
    table.align["Race Name"] = "l"

    for idx, contest in enumerate(unique_contests, 1):
        table.add_row([idx, contest])

    msg += table.get_string()
    msg += "\n\n"
    msg += f"Total: {len(unique_contests)} races\n"
    msg += "\nUsage: get_local_poll('search term') to view specific race results\n"
    msg += "```"
    return msg


def display_race_results(df, contest_name):
    """Display results for a specific race"""
    race_data = df[df['contest name'] == contest_name]

    if len(race_data) == 0:
        return f"No data found for race: {contest_name}\n"

    # Get precinct reporting information
    total_precincts = race_data.iloc[0]['num Precinct total']
    reporting_precincts = race_data.iloc[0]['num Precinct rptg']
    all_precincts_reported = (total_precincts == reporting_precincts)

    # Display the race results
    msg = "```\n"
    msg += f"{contest_name}\n"
    msg += "=" * 80 + "\n"
    msg += f"Precincts Reporting: {reporting_precincts} of {total_precincts}\n"
    if not all_precincts_reported:
        msg += "⚠️  PARTIAL RESULTS - Not all precincts have reported\n"
    msg += "\n"

    # Create prettytable
    table = PrettyTable()
    table.field_names = ["Candidate", "Party", "Votes", "Percent", "Status"]
    table.align["Candidate"] = "l"
    table.align["Party"] = "c"
    table.align["Votes"] = "r"
    table.align["Percent"] = "r"
    table.align["Status"] = "c"

    # Sort by votes to identify leader
    race_data_sorted = race_data.sort_values('total votes', ascending=False)

    for idx, (_, row) in enumerate(race_data_sorted.iterrows()):
        candidate = row['choice name']
        party = row['party name'] if pd.notna(row['party name']) else ""
        votes = row['total votes']
        percent = row['percent of votes']

        # Only show "Winner" if all precincts have reported and this is the top vote getter
        if idx == 0 and all_precincts_reported and candidate != "Write-in":
            status = "✓ WINNER"
        elif idx == 0 and not all_precincts_reported:
            status = "Leading"
        else:
            status = ""

        table.add_row([candidate, party, f"{votes:,}", f"{percent}%", status])

    msg += table.get_string()
    msg += "\n\n"

    # Summary information
    summary_table = PrettyTable()
    summary_table.field_names = ["Metric", "Value"]
    summary_table.align["Metric"] = "l"
    summary_table.align["Value"] = "r"
    summary_table.add_row(["Registered Voters", f"{race_data.iloc[0]['registered voters']:,}"])
    summary_table.add_row(["Ballots Cast", f"{race_data.iloc[0]['ballots cast']:,}"])
    summary_table.add_row(["Under Votes", race_data.iloc[0]['under votes']])
    summary_table.add_row(["Over Votes", race_data.iloc[0]['over votes']])

    msg += summary_table.get_string()
    msg += "\n```"
    return msg


if __name__ == "__main__":
    # Examples:
    # Show all available races
    # print(get_local_poll())

    # Search for specific races
    # print(get_local_poll("Treasurer"))
    print(get_local_poll("Lancaster"))
    # print(get_local_poll("President"))