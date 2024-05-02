import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category
from config import DB_USER, DB_PASSWORD
import pytest
class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.database_name = "trivia_test"
        self.database_path = 'postgresql://{}:{}@{}/{}'.format(
            DB_USER,
            DB_PASSWORD,
            'localhost:5432',
            self.database_name
        )
        setup_db(app=self.app, database_path=self.database_path)

    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    @pytest.fixture
    def client(self):
        with self.app.test_client() as client:
            yield client

    def test_get_categories(self):
        response = self.client.get('/categories')
        response_data = json.loads(response.data)
        assert response.status_code == 200
        assert response_data['success']

    def test_get_questions(self):
        response = self.client.get('/questions')
        response_data = json.loads(response.data)
        assert response.status_code == 200
        assert response_data['success']
        assert response_data['questions']
    
    def test_add_question(self):
        response = self.client.post('/questions', json={
            'question': 'What is the capital of Germany?',
            'answer': 'Berlin',
            'category': '3',
            'difficulty': 1
        })
        response_data = json.loads(response.data)
        assert response.status_code == 200
        assert response_data['success']
    
    def test_delete_question_not_found(self):
        response = self.client.delete('/questions/1000')
        assert response.status_code == 422
    
    def test_search_questions_not_found(self):
        response = self.client.post('/question/search', json={
            'searchTerm': 'Tim Burton'
        })
        assert response.status_code == 404

    def test_get_list_questions_by_category(self):
        response = self.client.get('/categories/1000/questions')
        assert response.status_code == 404
        
    def test_quizzes_bad_request(self):
        response = self.client.post('/quizzes', json={
            'previous_questions': [],
        })
        assert response.status_code == 400


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()