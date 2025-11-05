import pandas as pd
import requests
import zipfile
import io
from prettytable import PrettyTable



def get_local_poll():
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
        # Read summary.csv from the zip
        with zip_file.open('summary.csv') as csv_file:
            df = pd.read_csv(csv_file)

    print("Data loaded successfully!\n")

    # Filter for the County Treasurer race (Matt Lancaster's race)
    county_treasurer_race = df[df['contest name'] == 'County Treasurer (Vote For 1)']

    # Get precinct reporting information
    total_precincts = county_treasurer_race.iloc[0]['num Precinct total']
    reporting_precincts = county_treasurer_race.iloc[0]['num Precinct rptg']
    all_precincts_reported = (total_precincts == reporting_precincts)

    # Display the race results
    msg = """```\n"""
    msg += "COUNTY TREASURER RACE\n"
    # msg += "=" * 80
    msg += f"Precincts Reporting: {reporting_precincts} of {total_precincts}\n"
    if not all_precincts_reported:
        msg += "⚠️  PARTIAL RESULTS - Not all precincts have reported\n"

    # Create prettytable
    table = PrettyTable()
    table.field_names = ["Candidate", "Party", "Votes", "Percent", "Status"]
    table.align["Candidate"] = "l"
    table.align["Party"] = "c"
    table.align["Votes"] = "r"
    table.align["Percent"] = "r"
    table.align["Status"] = "c"

    # Sort by votes to identify leader
    county_treasurer_race_sorted = county_treasurer_race.sort_values('total votes', ascending=False)

    for idx, (_, row) in enumerate(county_treasurer_race_sorted.iterrows()):
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
    msg += "\n"

    # Summary information
    summary_table = PrettyTable()
    summary_table.field_names = ["Metric", "Value"]
    summary_table.align["Metric"] = "l"
    summary_table.align["Value"] = "r"
    summary_table.add_row(["Registered Voters", f"{county_treasurer_race.iloc[0]['registered voters']:,}"])
    summary_table.add_row(["Ballots Cast", f"{county_treasurer_race.iloc[0]['ballots cast']:,}"])
    summary_table.add_row(["Under Votes", county_treasurer_race.iloc[0]['under votes']])
    summary_table.add_row(["Over Votes", county_treasurer_race.iloc[0]['over votes']])

    msg += summary_table.get_string()
    msg += "\n```"
    return msg


if __name__ == "__main__":
    print(get_local_poll())