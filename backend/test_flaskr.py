import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category
from config import DB_USER, DB_PASSWORD, QUESTIONS_PER_PAGE

def paginate_questions(selection):
    page = 1
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question for question in selection]
    current_questions = questions[start:end]

    return current_questions


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

    def test_get_categories(self):
        response = self.client.get('/categories')
        response_data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response_data['success'])

    def test_get_categories_not_found(self):
        response = self.client.get('/category')
        self.assertEqual(response.status_code, 404)

    def test_get_questions(self):
        response = self.client.get('/questions')
        response_data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response_data['success'])
        self.assertTrue(response_data['questions'])

    def test_get_questions_not_found(self):
        response = self.client.get('/question')
        self.assertEqual(response.status_code, 404)

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

    def test_add_question_bad_request(self):
        response = self.client.post('/questions', json={
            'question': 'What is the capital of Germany?',
            'category': '3',
        })
        self.assertEqual(response.status_code, 400)

    def test_delete_question(self):
        response = self.client.delete('/questions/18')
        response_data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response_data['success'])

    def test_delete_question_not_processable(self):
        response = self.client.delete('/questions/1000')
        self.assertEqual(response.status_code, 422)

    def test_search_questions(self):
        response = self.client.post('/questions/search', json={
            'searchTerm': 'Tim Burton'
        })
        response_data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response_data['success'])

    def test_search_questions_not_found(self):
        response = self.client.post('/question/search', json={
            'searchTerm': 'Tim Burton'
        })
        self.assertEqual(response.status_code, 404)

    def test_get_questions_by_category_not_found(self):
        response = self.client.get('/categories/1000/questions')
        self.assertEqual(response.status_code, 404)

    def test_quizzes(self):
        response = self.client.post('/quizzes', json={
            'previous_questions': [],
            'quiz_category': {'type': 'Science', 'id': '1'}
        })
        self.assertEqual(response.status_code, 200)

    def test_quizzes_not_found(self):
        response = self.client.post('/quizze', json={
            'previous_questions': [],
            'quiz_category': {'type': 'Science', 'id': 1000}
        })
        self.assertEqual(response.status_code, 404)

    def test_quizzes_fail(self):
        response = self.client.post('/quizzes', json={
            'previous_questions': [],
        })
        self.assertEqual(response.status_code, 400)

    def test_paginate_questions(self):
        response_data = {
            'questions': [
                {
                    'answer': 'Muhammad Ali', 'category': 4, 'difficulty': 1, 'id': 9, 'question': "What boxer's original name is Cassius Clay?"}, {
                    'answer': 'Tom Cruise', 'category': 5, 'difficulty': 4, 'id': 4, 'question': 'What actor did author Anne Rice first denounce, then praise in the role of her beloved Lestat?'}, {
                    'answer': 'Edward Scissorhands', 'category': 5, 'difficulty': 3, 'id': 6, 'question': 'What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages?'}, {
                        'answer': 'Brazil', 'category': 6, 'difficulty': 3, 'id': 10, 'question': 'Which is the only team to play in every soccer World Cup tournament?'}, {
                            'answer': 'Uruguay', 'category': 6, 'difficulty': 4, 'id': 11, 'question': 'Which country won the first ever soccer World Cup in 1930?'}, {
                                'answer': 'George Washington Carver', 'category': 4, 'difficulty': 2, 'id': 12, 'question': 'Who invented Peanut Butter?'}, {
                                    'answer': 'Lake Victoria', 'category': 3, 'difficulty': 2, 'id': 13, 'question': 'What is the largest lake in Africa?'}, {
                                        'answer': 'The Palace of Versailles', 'category': 3, 'difficulty': 3, 'id': 14, 'question': 'In which royal palace would you find the Hall of Mirrors?'}, {
                                            'answer': 'Agra', 'category': 3, 'difficulty': 2, 'id': 15, 'question': 'The Taj Mahal is located in which Indian city?'}, {
                                                'answer': 'Escher', 'category': 2, 'difficulty': 1, 'id': 16, 'question': 'Which Dutch graphic artist–initials M C was a creator of optical illusions?'}]}
        paginated_questions = paginate_questions(
            selection=response_data['questions']
        )
        self.assertEqual(len(paginated_questions), 10)

    def test_paginate_questions_fail(self):
        response_data = {
            'questions': [
                {
                    'answer': 'Muhammad Ali', 'category': 4, 'difficulty': 1, 'id': 9, 'question': "What boxer's original name is Cassius Clay?"}, {
                    'answer': 'Tom Cruise', 'category': 5, 'difficulty': 4, 'id': 4, 'question': 'What actor did author Anne Rice first denounce, then praise in the role of her beloved Lestat?'}, {
                    'answer': 'Edward Scissorhands', 'category': 5, 'difficulty': 3, 'id': 6, 'question': 'What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages?'}, {
                        'answer': 'Brazil', 'category': 6, 'difficulty': 3, 'id': 10, 'question': 'Which is the only team to play in every soccer World Cup tournament?'}, {
                            'answer': 'Uruguay', 'category': 6, 'difficulty': 4, 'id': 11, 'question': 'Which country won the first ever soccer World Cup in 1930?'}, {
                                'answer': 'George Washington Carver', 'category': 4, 'difficulty': 2, 'id': 12, 'question': 'Who invented Peanut Butter?'}, {
                                    'answer': 'Lake Victoria', 'category': 3, 'difficulty': 2, 'id': 13, 'question': 'What is the largest lake in Africa?'}, {
                                        'answer': 'The Palace of Versailles', 'category': 3, 'difficulty': 3, 'id': 14, 'question': 'In which royal palace would you find the Hall of Mirrors?'}, {
                                            'answer': 'Agra', 'category': 3, 'difficulty': 2, 'id': 15, 'question': 'The Taj Mahal is located in which Indian city?'}, {
                                                'answer': 'Escher', 'category': 2, 'difficulty': 1, 'id': 16, 'question': 'Which Dutch graphic artist–initials M C was a creator of optical illusions?'}]}
        paginated_questions = paginate_questions(
            selection=response_data['questions']
        )
        self.assertNotEqual(len(paginated_questions), 11)


if __name__ == "__main__":
    unittest.main()