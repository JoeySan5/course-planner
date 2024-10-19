import requests
import json
import uuid  # Added to generate UUID

# API request URL
url = "https://reg-prod.ec.lehigh.edu/StudentRegistrationSsb/ssb/searchResults/searchResults"

# Load subject codes from subject.txt file
subjects = []
with open("subject.txt", "r") as file:
    for line in file:
        try:
            # Example: {'code': 'CSE', 'description': 'Computer Science & Engineering'}
            subject = eval(line.strip())  # Each line is in dictionary format, so use eval()
            subjects.append(subject['code'])  # Extract only the 'code' key value
        except Exception as e:
            print(f"Failed to parse line: {line}. Error: {e}")

# Set headers
headers = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.8",
    "priority": "u=1, i",
    "referer": "https://reg-prod.ec.lehigh.edu/StudentRegistrationSsb/ssb/classSearch/classSearch",
    "sec-ch-ua": "\"Chromium\";v=\"130\", \"Google Chrome\";v=\"130\", \"Not?A_Brand\";v=\"99\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
    "x-synchronizer-token": str(uuid.uuid4())  # Generate a new token for each request
}

# Updated cookies
cookies = {
    "JSESSIONID": "88D5BC2530D171EF44549CBE58B865F5",
    "cookie-agreed-version": "1.0.0",
    "cookie-agreed": "2",
    "_gcl_au": "1.1.1656405112.1726156705",
    "_ga_74Q0ZK57LT": "GS1.1.1727281673.2.0.1727281676.0.0.0",
    "_scid": "fPRxYgyP2uvIwL1lujEK8nkJPexUC3ZC",
    "_cat": "CAT1.3.509035946.1727840279055",
    "_fbp": "fb.1.1727840279230.96900342252094147",
    "_ga_T8K9FT0CMZ": "GS1.2.1727912919.1.0.1727912919.60.0.0",
    "_hjSessionUser_2580298": "eyJpZCI6IjMwNjA4MjhhLTRmMDAtNTJmMC04MjMyLWQ4MGQ0ZGY4Njk2NiIsImNyZWF0ZWQiOjE3Mjc5MTI5MjExMDEsImV4aXN0aW5nIjpmYWxzZX0=",
    "_ga_7PM892EE02": "GS1.1.1727912917.1.0.1727912927.50.0.0",
    "_ga_P7DT1QXXSK": "GS1.1.1727912918.1.0.1727912927.0.0.0",
    "_ga_ZYGQ8432T2": "GS1.1.1727912918.1.0.1727912927.51.0.0",
    "_ga_MT3CG3F57S": "GS1.1.1727964541.1.0.1727964545.0.0.0",
    "_ga_S5QSGJSW1S": "GS1.1.1727964615.2.1.1727964634.40.0.0",
    "_ga_DFHMDWEZZW": "GS1.1.1728326112.1.0.1728326114.58.0.0",
    "_ga_93S97588TJ": "GS1.1.1728326110.1.1.1728326218.0.0.0",
    "_gid": "GA1.2.1630953423.1728899565",
    "_ga_ELPWQRV7QW": "GS1.1.1729002564.6.0.1729002566.0.0.0",
    "__utmc": "182352186",
    "_ScCbts": "%5B%5D",
    "_sctr": "1%7C1729224000000",
    "_ga_D24LL2GQD5": "GS1.1.1729356830.4.0.1729356834.56.0.0",
    "__utmz": "182352186.1729356836.2.2.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided)",
    "__utma": "182352186.1110982444.1725418647.1729356836.1729358800.3",
    "__utmb": "182352186.4.10.1729358800",
    "_ga_15PFH9QL67": "GS1.1.1729356830.171.1.1729359385.0.0.0",
    "_ga": "GA1.2.1110982444.1725418647",
    "_scid_r": "h3RxYgyP2uvIwL1lujEK8nkJPexUC3ZCdSkXQg",
    "_ga_50ZXY9W4WM": "GS1.2.1729358800.6.1.1729359385.26.0.0",
    "_ga_2MCQTKR9B6": "GS1.1.1729356830.171.1.1729359407.3.0.0",
    "AWSALB": "+nA8Z8mmptIcupJno4QlCmHdv1ZDz563e17DgRr+VogoqClqAnTnPyv9h8jklWVIn0KlxGx1pWlw4fYj5Jx7NbG+km2MpcTU41vh88z0+5AVIZJPndw8ZFlQ1iDB",
    "AWSALBCORS": "+nA8Z8mmptIcupJno4QlCmHdv1ZDz563e17DgRr+VogoqClqAnTnPyv9h8jklWVIn0KlxGx1pWlw4fYj5Jx7NbG+km2MpcTU41vh88z0+5AVIZJPndw8ZFlQ1iDB"
}

# List to store all course data
all_courses = []

# Request data using each subject code
for code in subjects:
    print(f"Fetching data for subject: {code}")
    # Set query parameters
    params = {
        "txt_subject": code,
        "txt_term": "202510",
        "startDatepicker": "",
        "endDatepicker": "",
        "uniqueSessionId": str(uuid.uuid4()),
        "pageOffset": "0",
        "pageMaxSize": "300",
        "sortColumn": "subjectDescription",
        "sortDirection": "asc"
    }

    # Send request
    response = requests.get(url, headers=headers, params=params, cookies=cookies)

    # Check response and store data
    if response.status_code == 200:
        try:
            response_json = response.json()
            data = response_json.get("data", [])
            print(f"Fetched {len(data)} courses for subject {code}")
            all_courses.extend(data)  # Add to the overall data
        except json.JSONDecodeError:
            print(f"Failed to process JSON response for subject {code}.")
    else:
        print(f"Request failed for subject {code}: Status code {response.status_code}")

# Save all data to a single JSON file
with open("all_courses_data.json", "w") as f:
    json.dump(all_courses, f, indent=4)

print("All subject data collection is complete. Saved to JSON file.")
