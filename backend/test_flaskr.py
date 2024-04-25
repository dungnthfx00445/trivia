import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.database_name = "trivia_test"
        self.database_path = 'postgresql://{}:{}@{}/{}'.format('postgres','123456','localhost:5432',self.database_name)
        
        self.app = create_app({
            "SQLALCHEMY_DATABASE_URI": self.database_path
        })

        self.client = self.app.test_client

    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_categories(self):
        response = self.client.get('/categories')
        response_data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response_data["success"])
        self.assertEqual(
            list(response_data["categories"].values()),
            ["Sports", "Art", "Entertainment", "Science", "History"]
        )
    
    def test_add_question(self):
        response = self.client.post('/questions', json={
            'question': 'What is the capital of Germany?',
            'answer': 'Berlin',
            'category': '3',
            'difficulty': 1
        })
        response_data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response_data['success'])
    
    def test_delete_question_not_found(self):
        response = self.client.delete('/questions/1000')
        self.assertEqual(response.status_code, 404)
    
    def test_search_questions_not_found(self):
        response = self.client.post('/question/search', json={
            'search': 'Tim Burton'
        })
        self.assertEqual(response.status_code, 404)

    def test_get_question_by_category(self):
        response = self.client().get('/categories/2/questions')
        response_data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['success'], True)
        self.assertTrue(response_data['questions'])
        self.assertTrue(response_data['total_questions'])
        self.assertTrue(response_data['current_category'])

    def test_quizzes_bad_request(self):
        response = self.client.post('/quizzes', json={
            'previous_questions': [],
        })
        self.assertEqual(response.status_code, 400)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()