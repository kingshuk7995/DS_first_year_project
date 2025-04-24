import requests
import pandas as pd
from collections import Counter
from time import sleep
from tqdm import tqdm
from random import sample

def get_user_data(user: str, contest_required_data: pd.DataFrame = None) -> pd.DataFrame:
    '''
    Function to collect the data of a user and return a DataFrame enriched with historical features
    Parameters:
        user -> Codeforces user handle
        contest_required_data -> Optional: pre-loaded contests.csv to avoid repeated loading
    '''
    try:
        # --- Fetch contest data ---
        url_contest = f"https://codeforces.com/api/user.rating?handle={user}"
        res_contest = requests.get(url_contest)
        res_contest.raise_for_status()
        contest_response = res_contest.json()
        if contest_response['status'] != 'OK':
            raise Exception(contest_response.get('comment', 'Unknown API Error'))
        contest_data = pd.DataFrame(contest_response['result'])

        # --- Fetch submission data ---
        url_submissions = f"https://codeforces.com/api/user.status?handle={user}"
        res_sub = requests.get(url_submissions)
        res_sub.raise_for_status()
        submission_response = res_sub.json()
        if submission_response['status'] != 'OK':
            raise Exception(submission_response.get('comment', 'Unknown API Error'))
        submission_data = pd.DataFrame(submission_response['result'])

        # --- Process contest data ---
        contest_data.drop(columns=['contestName', 'ratingUpdateTimeSeconds'], inplace=True)

        # --- Process submission data ---
        submission_data = submission_data[['id', 'creationTimeSeconds', 'verdict']].copy()
        problems = [item.get('problem', {}) for item in submission_response['result']]
        submission_problem_data = pd.DataFrame(problems)

        # Handle missing expected columns
        for col in ['rating', 'tags']:
            if col not in submission_problem_data:
                if col == 'tags':
                    submission_problem_data['tags'] = [[] for _ in range(len(submission_problem_data))]
                else:
                    submission_problem_data[col] = None

        # Drop unnecessary columns
        submission_problem_data.drop(columns=[col for col in ['contestId', 'index', 'name', 'type', 'points'] if col in submission_problem_data], inplace=True)

        # Combine submission data
        combined_submission_data = pd.concat([submission_data, submission_problem_data], axis=1)
        combined_submission_data['tags'] = combined_submission_data['tags'].apply(lambda x: x if isinstance(x, list) else [])

        # Filter accepted submissions
        accepted_subs = combined_submission_data[combined_submission_data['verdict'] == 'OK']
        all_tags = set(tag for tags in accepted_subs['tags'] for tag in tags)

        # Load contest_required_data if not provided
        if contest_required_data is None:
            contest_required_data = pd.read_csv('Dataset/contests.csv')

        # Add contest start time
        merged = pd.merge(contest_data, contest_required_data[['id', 'startTimeSeconds']],
                          left_on='contestId', right_on='id', how='left')
        contest_data['startTimeSeconds'] = merged['startTimeSeconds']

        # Build enriched rows
        final_rows = []
        for _, row in contest_data.iterrows():
            contest_time = row['startTimeSeconds']

            prior_subs = combined_submission_data[combined_submission_data['creationTimeSeconds'] < contest_time]
            prior_ok = accepted_subs[accepted_subs['creationTimeSeconds'] < contest_time]
            total_subs = len(prior_subs)
            accepted_count = len(prior_ok)

            acceptance_rate = accepted_count / total_subs if total_subs > 0 else 0.0
            avg_rating = prior_ok['rating'].dropna().mean() if not prior_ok.empty else 0.0

            tag_counter = Counter()
            for tags in prior_ok['tags']:
                tag_counter.update(tags)

            enriched = row.to_dict()
            enriched['acceptance_rate'] = acceptance_rate
            enriched['avg_rating'] = avg_rating

            for tag in all_tags:
                enriched[tag] = tag_counter.get(tag, 0)

            final_rows.append(enriched)

        return pd.DataFrame(final_rows)

    except Exception as e:
        print(f"[{user}] Exception occurred: {e}")
        return None


if __name__ == '__main__':
    # Load static contest data
    contest_data = pd.read_csv('Dataset/contests.csv')

    # Loading all headers
    handles = pd.read_csv('Dataset/all_users.csv')['handle'].to_list()

    # taking 50 random handles
    handles = sample(handles,50)

    # Store user-wise DataFrames
    dataframes = []

    for handle in tqdm(handles, desc="Fetching user data"):
        df = get_user_data(user=handle, contest_required_data=contest_data)
        if df is not None and not df.empty:
            dataframes.append(df)
        sleep(1)  # Avoid hitting rate limits

    # Save the final dataset
    final_df = pd.concat(dataframes, ignore_index=True)
    final_df.to_csv('Dataset/final.csv', index=False)
    print("Final dataset saved to Dataset/final.csv")
