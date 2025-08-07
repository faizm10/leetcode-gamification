import leetcode_api
import pandas as pd

class LeetCodeGamification:
    def __init__(self, username, password):
        self.api = leetcode_api.LeetCodeAPI(username, password)
        self.user_data = self.api.get_user_profile(username)

    def get_user_progress(self):
        submissions = self.api.get_user_submissions(self.user_data['username'])
        problems_solved = len(submissions)
        total_score = sum(submission['score'] for submission in submissions)
        return problems_solved, total_score

    def calculate_rewards(self, problems_solved, total_score):
        rewards = []
        if problems_solved >= 10:
            rewards.append({'badge': 'Beginner', 'description': 'Solved 10 problems'})
        if problems_solved >= 50:
            rewards.append({'badge': 'Intermediate', 'description': 'Solved 50 problems'})
        if total_score >= 1000:
            rewards.append({'badge': 'Score Master', 'description': 'Reached a total score of 1000'})
        return rewards

    def get_leaderboard(self):
        # Fetch top 10 users with the most problems solved
        leaderboard = []
        for user in self.api.get_users():
            user_data = self.api.get_user_profile(user['username'])
            problems_solved, _ = self.get_user_progress()
            leaderboard.append({'username': user_data['username'], 'problems_solved': problems_solved})
        leaderboard.sort(key=lambda x: x['problems_solved'], reverse=True)
        return leaderboard[:10]

def main():
    username = 'your_username'
    password = 'your_password'
    gamification = LeetCodeGamification(username, password)

    print('User Profile:')
    print(gamification.user_data)

    problems_solved, total_score = gamification.get_user_progress()
    print(f'\nProblems Solved: {problems_solved}')
    print(f'Total Score: {total_score}')

    rewards = gamification.calculate_rewards(problems_solved, total_score)
    print('\nRewards:')
    for reward in rewards:
        print(f"Badge: {reward['badge']}, Description: {reward['description']}")

    leaderboard = gamification.get_leaderboard()
    print('\nLeaderboard:')
    for user in leaderboard:
        print(f"Username: {user['username']}, Problems Solved: {user['problems_solved']}")

if __name__ == '__main__':
    main()