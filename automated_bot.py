import random
import configparser
import time

import requests
import logging

from sqlalchemy import select, create_engine
from sqlalchemy.orm import sessionmaker

from src.conf.config import config
from src.database.models import User

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def load_config(file_path):
    """
    The load_config function reads the configuration file and returns a config object.


    :param file_path: Specify the path to the config file
    :return: A configparser
    
    """
    config = configparser.ConfigParser()
    config.read(file_path)
    return config


session = requests.Session()


class DatabaseSessionManager:

    def __init__(self, url: str):
        """    
        The __init__ function creates a new database engine and session maker.
        The engine is used to create connections to the database, while the session
        maker is used to create sessions that can be used for querying and modifying
        the data in the database.
        
        :param self: Represent the instance of the object itself
        :param url: str: Create the engine
        :return: Nothing
        
        """
        self._engine = create_engine(url)
        self._session_maker = sessionmaker(bind=self._engine)

    def session(self):
        """    
        The session function is a factory that creates a new session object.
        It's called by the request handler to create a new session for each request.
        The function itself is defined in the SessionManager class, which we'll use as our application-wide database manager.
        
        :param self: Represent the instance of the class
        :return: A new session object
        
        """
        return self._session_maker()


SQLALCHEMY_DATABASE_URL = (
    "postgresql+psycopg2://"
    + f"{config.postgres_user}:{config.postgres_password}"
    + f"@{config.postgres_host}:{config.postgres_port}"
    + f"/{config.postgres_db}"
)

session_manager = DatabaseSessionManager(SQLALCHEMY_DATABASE_URL)


def confirm_user_in_database(email: str):
    """
    The confirm_user_in_database function takes an email address as a parameter and confirms the user in the database.
        If no user is found, it prints out that no user was found.
    
    :param email: str: Pass in the email of the user to be confirmed
    :return: A boolean value
    
    """
    with session_manager.session() as session:

        stmt = select(User).where(User.email == email)
        result = session.execute(stmt)
        user = result.scalar_one_or_none()

        if user:

            user.confirmed = True
            session.commit()
            print(f"User {email} confirmed successfully.")
        else:
            print(f"User {email} not found.")


def signup_user(base_url, username):
    """
    The signup_user function takes a base_url and username as arguments.
    It then creates a payload with the username, email address (username@example.com), and password all set to the same value as the username argument.
    The function then makes an HTTP POST request to /auth/signup using this payload, which will create a new user in our database if successful.
    
    :param base_url: Specify the url of the application
    :param username: Create a unique username for each user
    :return: A 201 status code if the user was created successfully
    
    """
    time.sleep(1)
    payload = {
        "username": username,
        "email": f"{username}@example.com",
        "password": username
    }
    response = session.post(f'{base_url}/auth/signup', json=payload)
    if response.status_code == 201:
        logging.info(f'User {username} signed up successfully.')
        confirm_user_in_database(f"{username}@example.com")
    else:
        logging.error(f'Error signing up user {username}: {response.text}')


def signup_users(base_url, num_users):
    """
    The signup_users function signs up a number of users to the application.
    
    :param base_url: Specify the url of the website that we want to sign up users on
    :param num_users: Determine how many users to sign up
    :return: Nothing
    
    """
    for user_id in range(1, num_users + 1):
        username = f'user_{user_id}'
        signup_user(base_url, username)


def login_user(base_url, username):
    """
    The login_user function takes a base_url and username as arguments.
    It then creates a login_data dictionary with the username and password,
    and uses that to POST to the /auth/login endpoint. If successful, it returns 
    the access token from the response JSON.
    
    :param base_url: Specify the url of the server
    :param username: Login the user
    :return: A token
    
    """
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
    """
    The login_users function takes a base_url and a list of users as arguments.
    It returns a dictionary with the user names as keys and their tokens as values.
    
    :param base_url: Specify the url of the server
    :param users: Pass in the list of users to login
    :return: A dictionary of users and their tokens
    
    """
    user_tokens = {}
    for user in users:
        token = login_user(base_url, user)
        if token:
            user_tokens[user] = token
    return user_tokens


def create_post(base_url, user, access_token, post_content):
    """
    The create_post function creates a post for the user.
        Args:
            base_url (str): The base url of the application.
            user (str): The username of the account to create a post with.
            access_token (str): A valid access token for that user's account. 
    
    :param base_url: Specify the base url of the api
    :param user: Identify the user who is creating a post
    :param access_token: Authenticate the user and create a post
    :param post_content: Pass in the content of the post
    :return: A response object
    
    """
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
    """
    The create_posts function creates a random number of posts for each user.
    
    :param base_url: Specify the url of the server
    :param users: Get the user name
    :param max_posts_per_user: Determine how many posts each user will have
    :param user_tokens: Store the access tokens for each user
    :return: Nothing
    
    """
    for user in users:
        num_posts = random.randint(1, max_posts_per_user)
        access_token = user_tokens.get(user)
        for _ in range(num_posts):
            post_content = f'This is a random post by {user}.'
            create_post(base_url, user, access_token, post_content)


def like_post(base_url, user, access_token, post_id):
    """
    The like_post function takes in a base_url, user, access_token and post_id.
    It then creates a url using the base url and post id. It also creates headers with the authorization token 
    and content type as json. The function then makes a POST request to that URL with those headers and logs an error if it fails.
    
    :param base_url: Specify the url of the server that we are trying to connect to
    :param user: Log the user that liked a post
    :param access_token: Authenticate the user
    :param post_id: Specify which post to like
    :return: A response object
    
    """
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
    """
    The like_posts function takes in a base_url, users, max_likes_per_user, user tokens and total posts.
    It then iterates through the users and generates a random number of likes per user between 1 and the max likes per user.
    Then it gets an access token for that specific user from the dictionary of access tokens. Then it loops through each like 
    and calls on like post to actually make those likes happen.
    
    :param base_url: Specify the base url of the website
    :param users: Get the user's access token
    :param max_likes_per_user: Determine how many likes each user will make
    :param user_tokens: Get the access token for a particular user
    :param total_posts: Specify the range of post ids that can be liked
    :return: Nothing
    
    """
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
    total_posts = number_of_users * (max_posts_per_user / 2)

    signup_users(base_url, number_of_users)

    time.sleep(2)
    users = [f'user_{user_id}' for user_id in range(1, number_of_users + 1)]
    user_tokens = login_users(base_url, users)

    create_posts(base_url, users, max_posts_per_user, user_tokens)
    like_posts(base_url, users, max_likes_per_user, user_tokens, total_posts)
