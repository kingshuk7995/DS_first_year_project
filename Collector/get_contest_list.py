import requests
import pandas as pd
import os

def fetch_contest_list():
    '''A function collecting codeforces contest list
    '''
    # Make sure the Dataset folder exists
    os.makedirs('./Dataset', exist_ok=True)

    # Fetch contest list
    url = "https://codeforces.com/api/contest.list"
    response = requests.get(url)
    data = response.json()

    # checking if data came correctly
    if data['status'] != 'OK':
        print("Error:", data.get('comment', 'Unknown error'))
        exit()

    # getting inportent parts
    contests = data['result']

    # Convert to DataFrame
    df = pd.DataFrame(contests)

    # Keep selected columns
    columns_to_keep = ['id', 'name', 'phase', 'durationSeconds', 'startTimeSeconds']
    df = df[columns_to_keep]

    # Save to CSV
    df.to_csv('./Dataset/contests.csv', index=False)
    print("Contest data saved to /Dataset/contests.csv")

if __name__ == "__main__":
    fetch_contest_list()
