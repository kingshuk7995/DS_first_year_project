# 🧠 DS First Year Project

## Project Overview
This project focuses on analyzing and predicting user performance in Codeforces contests using data collected from the Codeforces API. The primary goal is to predict whether a user's rating will increase or decrease in the next contest based on historical data and problem-solving patterns.

## Project Structure

### 1. **Collector**
This module contains scripts to collect and preprocess data from the Codeforces API.
- **`get_contest_list.py`**: Fetches the list of contests and saves it to `Dataset/contests.csv`.
- **`get_user_list_from_contest_rank.py`**: Extracts user handles from recent contests and saves them to `Dataset/all_users.csv`.
- **`get_all_user_contest_data.py`**: Collects detailed user data, including contest performance and problem-solving statistics, and saves it to `Dataset/final.csv`.
- **`analysis_user_data.ipynb`**: Notebook for analyzing collected user data.

### 2. **Dataset**
This folder contains the datasets used and generated during the project.
- **`contests.csv`**: List of contests fetched from the Codeforces API.
- **`all_users.csv`**: List of user handles extracted from recent contests.
- **`final.csv`**: Detailed user data with enriched features.
- **`cleaned_data.csv`**: Preprocessed dataset used for training and evaluation.
- **`validation.csv`**: Validation dataset for model evaluation.

### 3. **Notebooks**
- **`training.ipynb`**: Notebook for training machine learning models to predict rating changes.
- **`visualisation.ipynb`**: Notebook for visualizing and analyzing the dataset.

## Key Features

### Data Collection
- Utilizes the Codeforces API to fetch contest and user data.
- Processes user submissions to extract problem-solving patterns and historical performance.

### Data Analysis
- Visualizes rating changes, problem type distributions, and user performance trends.
- Identifies outliers and handles missing data using techniques like KNN imputation.

### Machine Learning
- Implements K-Nearest Neighbors (KNN) and Random Forest classifiers to predict rating changes.
- Evaluates models using accuracy, confusion matrices, and classification reports.
- Explores hyperparameter tuning (e.g., varying the number of neighbors in KNN).
- Train set consists 200 users randomly taken from all_users.csv and their contests are splitted randomly for train and test data.
- Evaluation with validation set of 15 users randomly taken from all_users.csv who are not in test or train set.

## Questions Addressed
1. **What problems can we solve with this data?**
   - Predict the types of problems a user can solve to improve performance.
   - Detect anomalies and flag users for plagiarism checks.
   - Predict whether a user's rating will increase or decrease in the next contest.

2. **What insights can we gain from the data?**
   - What features are most predictive of performance?
   - How do problem-solving patterns vary across users?
   - What are the outlier cases, and how should they be handled?

## How to Run the Project
1. **Set Up the Environment**:
   - Install the required dependencies using `pip install -r requirements.txt`.

2. **Collect Data**:
   - Run `get_contest_list.py` to fetch contest data.
   - Run `get_user_list_from_contest_rank.py` to extract user handles.
   - Run `get_all_user_contest_data.py` to collect detailed user data.

3. **Preprocess Data**:
   - Use `visualisation.ipynb` to clean and analyze the dataset.

4. **Train Models**:
   - Use `training.ipynb` to train and evaluate machine learning models.

## Future Path
- Explore additional machine learning models for better predictions.
- Incorporate more features, such as user activity levels and contest difficulty.
- Develop a web interface for real-time predictions.

## References
- **Codeforces API Documentation**: [https://codeforces.com/apiHelp](https://codeforces.com/apiHelp)
