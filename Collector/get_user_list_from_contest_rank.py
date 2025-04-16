import os
import pandas as pd
import requests
from time import sleep

# check if run get_contest_list at past
def check_contests_fetched():
    '''Check if contest list is available; fetch if missing'''
    if not os.path.exists("Dataset/contests.csv"):
        from get_contest_list import fetch_contest_list
        fetch_contest_list()

# to fetch user ids
def fetch_all_users_from_finished_contests():
    #checking
    check_contests_fetched()

    # Load contests
    contest_list = pd.read_csv('Dataset/contests.csv')
    finished_contests = contest_list[contest_list['phase'] == 'FINISHED'].copy(deep=True)

    # storing unique ids
    userIDs = set()

    # taking recent participants in the dataset for consistency
    for contestID in finished_contests['id'].head(50):
        try:
            # Fetch all participants by setting a very large count (max limit for the contest size)
            url = f"https://codeforces.com/api/contest.standings?contestId={contestID}&from=1&count=1000"
            response = requests.get(url, timeout=10)
            response.raise_for_status()     # checking response

            response_json = response.json()

            # checking response
            if response_json['status'] != 'OK':
                raise Exception(response_json.get('comment', 'Unknown API error'))

            rows = response_json['result']['rows']
            for row in rows:
                for member in row['party']['members']:
                    userIDs.add(member['handle'])

            print(f"Fetched users from contest {contestID}")

            sleep(1)

        except Exception as e:
            print(f"Failed to fetch standings for contest {contestID}: {e}")

    print(f"\nTotal unique users fetched: {len(userIDs)}")

    # Save userIDs to CSV
    os.makedirs("Dataset", exist_ok=True)
    pd.Series(sorted(userIDs)).to_csv("Dataset/all_users.csv", index=False, header=["handle"])
    print("Saved all users to Dataset/all_users.csv")

if __name__ == "__main__":
    fetch_all_users_from_finished_contests()
