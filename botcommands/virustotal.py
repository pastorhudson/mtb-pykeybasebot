from virustotal_python import Virustotal
import os
from dotenv import load_dotenv
import random

load_dotenv(dotenv_path='./secret.env')
# Normal Initialisation.
vtotal = Virustotal(os.environ.get('VIRUS_TOTAL_API_KEY'))

observations = [
    "This is disgusting. I hate my life.",
    "This URL may contain harmful code. . . Let's let Marvin look at it first :unamused:",
    "I hope this kills me.",
    "This could be my last web request. . .",
    "This is @ihuman 's fault, and I will never forget."
]
def get_scan(url):
    # mock_report =
    # report = json.loads(mock_report)

    # Query url(s) to VirusTotal.
    # A list containing a url to be scanned by VirusTotal.
    # resp = vtotal.url_scan(["ihaveaproblem.info"])  # Query a single url.
    # A list of url(s) to be scanned by VirusTotal (MAX 4 per standard request rate).
    scan = vtotal.url_scan(
        [url]
    )

    # Retrieve scan report(s) for given file(s) from Virustotal.
    # A list containing the resource (SHA256) HASH of a known malicious file.
    report = vtotal.url_report(
        [url]
    )

    # pprint(report)

    msg = f"{random.choice(observations)}```\nVirus Total Report for {url}\n" \
          f"Positives: {report['json_resp']['positives']}\n" \
          f"Results: "

    bad_result = False

    for scanner in report['json_resp']['scans']:
        if report['json_resp']['scans'][scanner]['detected']:
            bad_result = True
            bad = f"({scanner}: {report['json_resp']['scans'][scanner]['result']}), "
            msg += bad
    msg = msg[:-2]

    if not bad_result:
        msg += "Clean"

    msg += f"```" \
           f"\nVirus Total Report Link: {report['json_resp']['permalink']}"

    return msg


if __name__ == "__main__":
    print(get_scan('182.114.210.195'))
