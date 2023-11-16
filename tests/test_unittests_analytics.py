import unittest
from datetime import date
from unittest.mock import Mock

from fastapi import HTTPException
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import create_engine

from src.database.models import User, Post, PostReaction
from src.repository.analytics import get_post_analytics
from src.routes.analytics import get_post_likes_dislikes


class TestPostAnalytics(unittest.TestCase):

    def setUp(self):
        # Create an in-memory SQLite database for testing
        self.engine = create_engine('sqlite:///:memory:')
        Session = sessionmaker(self.engine, expire_on_commit=False)
        self.db = Session()

    def tearDown(self):
        # Close the database session and dispose of the engine
        self.db.close()
        self.engine.dispose()

    def test_get_post_likes_dislikes_valid_date_range(self):
        # Mock dependencies and set up test data
        mock_auth_service = Mock()
        mock_auth_service.get_current_user.return_value = User(id=1)  # Replace with appropriate user data
        post_id = 1
        start_date = date(2023, 1, 1)
        end_date = date(2023, 1, 31)

        # Create a test post and reactions
        test_post = Post(id=post_id, user_id=1)
        self.db.add(test_post)
        self.db.commit()

        test_reactions = [
            PostReaction(post_id=post_id, reaction='like', created_at=date(2023, 1, 5)),
            PostReaction(post_id=post_id, reaction='like', created_at=date(2023, 1, 10)),
            PostReaction(post_id=post_id, reaction='dislike', created_at=date(2023, 1, 15)),
        ]
        self.db.add_all(test_reactions)
        self.db.commit()

        # Call the route function with valid date range
        response = get_post_likes_dislikes(post_id, start_date, end_date, mock_auth_service, self.db)

        # Assert that the response contains expected data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "analytics_data": [
                {"date": "2023-01-05", "likes": 1, "dislikes": 0},
                {"date": "2023-01-10", "likes": 1, "dislikes": 0},
                {"date": "2023-01-15", "likes": 0, "dislikes": 1},
            ]
        })

    def test_get_post_likes_dislikes_invalid_date_range(self):
        # Mock dependencies
        mock_auth_service = Mock()
        mock_auth_service.get_current_user.return_value = User(id=1)  # Replace with appropriate user data
        post_id = 1
        start_date = date(2023, 2, 1)  # Invalid date range (start_date > end_date)
        end_date = date(2023, 1, 31)

        # Call the route function with invalid date range
        with self.assertRaises(HTTPException) as context:
            get_post_likes_dislikes(post_id, start_date, end_date, mock_auth_service, self.db)

        # Assert that a 400 HTTPException is raised with the appropriate detail message
        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, "Invalid date range")

    def test_get_post_analytics_valid_user(self):
        # Set up test data
        post_id = 1
        date_from = date(2023, 1, 1)
        date_to = date(2023, 1, 31)
        user = User(id=1)  # User has access to view analytics
        test_post = Post(id=post_id, user_id=1)
        self.db.add(test_post)
        self.db.commit()

        test_reactions = [
            PostReaction(post_id=post_id, reaction='like', created_at=date(2023, 1, 5)),
            PostReaction(post_id=post_id, reaction='like', created_at=date(2023, 1, 10)),
            PostReaction(post_id=post_id, reaction='dislike', created_at=date(2023, 1, 15)),
        ]
        self.db.add_all(test_reactions)
        self.db.commit()

        # Call the function with valid user
        analytics_data = get_post_analytics(post_id, date_from, date_to, user, self.db)

        # Assert that the analytics data is as expected
        expected_data = [
            {"date": date(2023, 1, 5), "likes": 1, "dislikes": 0},
            {"date": date(2023, 1, 10), "likes": 1, "dislikes": 0},
            {"date": date(2023, 1, 15), "likes": 0, "dislikes": 1},
        ]
        self.assertEqual(analytics_data, expected_data)

    def test_get_post_analytics_invalid_user(self):
        # Set up test data
        post_id = 1
        date_from = date(2023, 1, 1)
        date_to = date(2023, 1, 31)
        user = User(id=2)  # User does not have access to view analytics

        # Call the function with invalid user
        with self.assertRaises(HTTPException) as context:
            get_post_analytics(post_id, date_from, date_to, user, self.db)

        # Assert that a 400 HTTPException is raised with the appropriate detail message
        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, "Not authorized to access analytics")


if __name__ == '__main__':
    unittest.main()
