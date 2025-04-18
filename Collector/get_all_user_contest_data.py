'''
Here we are trying to build the function using which we would get the dataset for 
one user directly just with passing his username
'''
import requests
import pandas as pd
from collections import Counter

def get_user_data(user:str,contest_required_data:pd.DataFrame = None)->pd.DataFrame:
    '''
    Function to collect the data of user and return the DataFrame as designed in analysis_user_data.ipynb
    ## Parameters
    user -> user Id in codeforces
    contest_required_data -> pd.read_csv('contests.csv')
    ## second parameter passed to ignore the loading time of the csv file
    '''
    final_df = None
    try:
        # Fetching Contest Data
        url_contest_data = f"https://codeforces.com/api/user.rating?handle={user}"
        res = requests.get(url=url_contest_data)
        res.raise_for_status()
        response_contest_data = res.json()
        del res
        if response_contest_data['status'] != 'OK':
            print(f"Error : contest data fetching for {user}")
            raise Exception(response_contest_data.get('comment','Unknown API Error'))
        
        # contest DataFrame (unprocesed)
        contest_data = pd.DataFrame(response_contest_data['result'])
        # Fetching Submission Data
        url_submission_data = f"https://codeforces.com/api/user.status?handle={user}"
        res = requests.get(url=url_submission_data)
        res.raise_for_status()
        response_submission_data = res.json()
        del res
        if response_submission_data['status'] != 'OK':
            print(f"Error : submission data fetching for {user}")
            raise Exception(response_submission_data.get('comment','Unknown API Error'))

        # submission DataFrame (unprocessed)
        submission_data = pd.DataFrame(response_submission_data['result'])
        
        # processing
        contest_data.drop(columns=['contestName','ratingUpdateTimeSeconds'],inplace=True)
        columns_to_keep = ['id','creationTimeSeconds','verdict']
        submission_data = submission_data[columns_to_keep].copy(deep=True)
        
        submission_problem_response = [row['problem'] for row in response_submission_data['result']]
        submission_problem_data = pd.DataFrame(submission_problem_response)
        
        problem_data_columns_to_drop = ['contestId','index','name','type','points']
        submission_problem_data.drop(columns=problem_data_columns_to_drop,inplace=True)

        # concatonated dataframe
        combined_submission_data = pd.concat([submission_data, submission_problem_data], axis=1)

        # getting the contest_required_data from contests.csv
        if contest_required_data is None:
            contest_required_data = pd.read_csv('Dataset/contests.csv')

        merged_data = pd.merge(contest_data, contest_required_data[['id', 'startTimeSeconds']], left_on='contestId', right_on='id', how='left')
        contest_data['startTimeSeconds'] = merged_data['startTimeSeconds']        

        # Ensure 'tags' are always lists
        combined_submission_data['tags'] = combined_submission_data['tags'].apply(lambda x: x if isinstance(x, list) else [])

        # Only count accepted submissions
        combined_submission_data_ok = combined_submission_data[combined_submission_data['verdict'] == 'OK']

        # All tags ever seen in OK submissions
        all_tags = set(tag for tags in combined_submission_data_ok['tags'] for tag in tags)

        # Final rows to collect enriched contest info
        final_rows = []
        
        for _, row in contest_data.iterrows():
            contest_time = row['startTimeSeconds']
    
            # Submissions before this contest
            prior_subs = combined_submission_data[combined_submission_data['creationTimeSeconds'] < contest_time]
            total_subs = len(prior_subs)
    
            # Accepted submissions before this contest
            prior_ok = combined_submission_data_ok[combined_submission_data_ok['creationTimeSeconds'] < contest_time]
            accepted_count = len(prior_ok)
    
            # Acceptance rate
            acceptance_rate = accepted_count / total_subs if total_subs > 0 else 0.0
    
            # Average rating of accepted submissions
            avg_rating = prior_ok['rating'].dropna().mean() if not prior_ok.empty else 0.0
    
            # Count tags
            tag_counter = Counter()
            for tags in prior_ok['tags']:
                tag_counter.update(tags)
    
            # Build row with contest data + new features
            enriched = row.to_dict()
            enriched['acceptance_rate'] = acceptance_rate
            enriched['avg_rating'] = avg_rating
    
            for tag in all_tags:
                enriched[tag] = tag_counter.get(tag, 0)
    
            final_rows.append(enriched)

        # Final enriched DataFrame
        final_df = pd.DataFrame(final_rows)

    except Exception as e:
        print(f"Exception occured : {e}")
        return e
    finally:
        return final_df

if __name__ == '__main__':
    # Check the function
    contest_list = pd.read_csv('Dataset/contests.csv')
    print(get_user_data(user='kingshukpatra11').columns)

