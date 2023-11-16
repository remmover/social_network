# Social Network

Welcome to the Social Network project! This repository hosts the code for a comprehensive social networking application, designed to facilitate user interactions, content sharing, and community building.

## Features

- **User Management**: Users can sign up, log in, and manage their profiles. User data includes username, email, and password, with additional fields for account status and activity tracking.
- **Post Creation and Interaction**: Users can create posts, and react to them with likes or dislikes. Each post is associated with its creator and maintains a count of likes and dislikes.
- **Commenting System**: Users can comment on posts, fostering discussions and interactions within the community.
- **Analytics**: The application provides analytics for posts, tracking likes and dislikes over time.
- **Email Integration**: The system integrates email functionality for notifications and user communication.
- **Automated Bot**: An automated bot script is included for simulation and testing purposes.

## Technologies

- **Python**: The primary programming language.
- **FastAPI**: A modern, fast web framework for building APIs with Python.
- **PostgreSQL**: The database system for storing user and post data.
- **Redis**: Used for caching and rate limiting.
- **Docker**: Containerization of the application and its dependencies.

## Installation and Setup

1. **Clone the Repository**:
   ```
   git clone https://github.com/remmover/social_network.git
   ```
2. **Navigate to the Directory**:
   ```
   cd social_network
   ```
3. **Install packages**:
   ```
   poetry install
   ```
4. **Start the Application with Docker Compose**:
   ```
   docker compose up
   ```

5. **Create a migration with alembic**:
   ```
   alembic revision --autogenerate -m 'Init'
   ```
6. **Initialise the tables in the database**:
   ```
   alembic upgrade head
   ```

## Configuration

- **Application Settings**: Configure in `src/conf/config.py`. This includes secret keys, database, Redis, and email settings.
- **Environment Variables**: Set up for database access, Redis configuration, and email settings.
- **Database Models**: Defined in `src/database/models.py`, including User, Post, PostReaction, and Comment models.
- **API Schemas**: Located in `src/schemas.py`, defining the data structure for various operations.

## Usage

After starting the application, interact with the API endpoints using tools like Postman or a frontend interface.

## Contributing

Contributions are welcome! Please adhere to standard open-source contribution guidelines.

## License

This project is licensed under the [MIT License](LICENSE).
