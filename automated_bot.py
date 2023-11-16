import json
import random
import configparser
import requests
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Load configuration from the INI file
def load_config(file_path):
    config = configparser.ConfigParser()
    config.read(file_path)
    return config


# Initialize a session for HTTP requests
session = requests.Session()


# Function to simulate user signup
def signup_user(base_url, username):
    payload = {
        "username": username,
        "email": f"{username}@example.com",
        "password": username
    }
    response = session.post(f'{base_url}/auth/signup', json=payload)
    if response.status_code == 201:
        logging.info(f'User {username} signed up successfully.')
    else:
        logging.error(f'Error signing up user {username}: {response.text}')


def signup_users(base_url, num_users):
    for user_id in range(1, num_users + 1):
        username = f'user_{user_id}'
        signup_user(base_url, username)


# Function to simulate user login
def login_user(base_url, username):
    login_data = {'username': f"{username}@example.com", 'password': username}
    response = session.post(f'{base_url}/auth/login', data=login_data)
    if response.status_code == 200:
        auth_data = response.json()
        logging.info(f'User {username} logged in successfully.')
        return auth_data['access_token']
    else:
        logging.error(f'Error logging in user {username}.')
        return None


def login_users(base_url, users):
    user_tokens = {}
    for user in users:
        token = login_user(base_url, user)
        if token:
            user_tokens[user] = token
    return user_tokens


# Function to create a post
def create_post(base_url, user, access_token, post_content):
    url = f'{base_url}/api/posts/create?content={post_content}'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    response = session.post(url, headers=headers)
    if response.status_code == 200:
        logging.info(f'User {user} created a post.')
    else:
        logging.error(
            f'Error creating a post for user {user}. Status Code: {response.status_code}, Response Content: {response.text}')


def create_posts(base_url, users, max_posts_per_user, user_tokens):
    for user in users:
        num_posts = random.randint(1, max_posts_per_user)
        access_token = user_tokens.get(user)
        for _ in range(num_posts):
            post_content = f'This is a random post by {user}.'
            create_post(base_url, user, access_token, post_content)


# Function to like a post
def like_post(base_url, user, access_token, post_id):
    url = f'{base_url}/api/posts/like?post_id={post_id}'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    response = session.post(url, headers=headers)
    if response.status_code == 200:
        logging.info(f'User {user} liked post {post_id}')
    else:
        logging.error(f'Error liking post {post_id} by user {user}.')


def like_posts(base_url, users, max_likes_per_user, user_tokens, total_posts):
    for user in users:
        num_likes = random.randint(1, max_likes_per_user)
        access_token = user_tokens.get(user)
        for _ in range(num_likes):
            post_id = random.randint(1, total_posts)
            like_post(base_url, user, access_token, post_id)


if __name__ == "__main__":
    config = load_config('bot_config.ini')
    base_url = 'http://localhost:8000'
    number_of_users = int(config['BotConfiguration']['number_of_users'])
    max_posts_per_user = int(config['BotConfiguration']['max_posts_per_user'])
    max_likes_per_user = int(config['BotConfiguration']['max_likes_per_user'])
    total_posts = number_of_users * max_posts_per_user

    # Simulate user signup and login
    signup_users(base_url, number_of_users)
    users = [f'user_{user_id}' for user_id in range(1, number_of_users + 1)]
    user_tokens = login_users(base_url, users)

    # Simulate post creation and liking
    create_posts(base_url, users, max_posts_per_user, user_tokens)
    like_posts(base_url, users, max_likes_per_user, user_tokens, total_posts)

