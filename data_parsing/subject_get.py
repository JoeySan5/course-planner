import requests

# Initial setup
url = "https://reg-prod.ec.lehigh.edu/StudentRegistrationSsb/ssb/classSearch/get_subject"
term = "202510"
offset = 1
max_items = 10  # Maximum number of items to fetch at once
unique_session_id = "ecbxl1729306662848"  # Replace with a dynamic value if necessary

all_subjects = []

# Fetch data in a loop
while True:
    params = {
        "searchTerm": "",
        "term": term,
        "offset": offset,
        "max": max_items,
        "uniqueSessionId": unique_session_id,
        "_": "1729306742287"  # Timestamp value may need to be dynamic
    }

    # Send API request
    response = requests.get(url, params=params)

    if response.status_code == 200:
        subjects = response.json()

        # Exit if there is no more data
        if not subjects:
            break

        # Add results to the list
        all_subjects.extend(subjects)

        # Increase offset for the next set
        offset += 1

    else:
        print(f"Error: {response.status_code}")
        break

# Print all subjects and save them to a text file
with open("subject.txt", "w") as file:
    for subject in all_subjects:
        print(subject)
        file.write(str(subject) + "\n")
