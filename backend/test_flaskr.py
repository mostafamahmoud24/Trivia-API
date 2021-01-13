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
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('postgres:postgres01@localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            "question": 'New Question',
            "answer": 'New Answer',
            "category": 1,
            "difficulty": 2,
        }

        self.bad_new_question = {
            "question": '',
            "answer": 'New Answer',
            "category": '1',
            "difficulty": '2',
        }

        self.new_question_search = {
            "searchTerm": "Bird"
        }

        self.new_quiz = {
            'previous_questions': [], 
            'quiz_category': {'type': 'Geography', 'id': '3'}
        }

        self.bad_new_quiz = {
            'previous_questions': [], 
            'quiz_category': {'type': 'Geography', 'id': ''}
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    
    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    # I cant test the 404 for this because the categories table is populated
    def test_get_all_categories(self):
        res = self.client().get('/api/categories/')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertTrue(len(data['categories']))


    # I cant test the 404 for this because the questions table is populated
    def test_get_paginated_questions(self):
        res = self.client().get('/api/questions/')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['current_category'])
        self.assertTrue(data['categories'])

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/api/questions/?page=500')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Not found")

    def test_delete_question_by_id(self):
        res = self.client().delete('/api/questions/5')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'], "question with the id of 5 was deleted successfully")

    def test_404_delete_question_by_id_that_doesnt_exist(self):
        res = self.client().delete('/api/questions/500')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Not found")

    def test_creating_question(self):
        res = self.client().post('/api/questions/', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'], "question created successfully")

    def test_400_for_failed_create(self):
        res = self.client().post('/api/questions/', json=self.bad_new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['error'], 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Bad Request")

    def test_get_searched_questions(self):
        res = self.client().post('/api/questions/search/', json=self.new_question_search)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['current_category'])
        self.assertTrue(data['categories'])

    def test_404_get_searched_questions(self):
        res = self.client().post('/api/questions/search/', json={'searchTerm': ''})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Not found")

    def test_get_questions_by_category_id(self):
        res = self.client().get('/api/categories/1/questions/')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['current_category'])
        self.assertTrue(data['categories'])

    def test_404_get_questions_by_category_id(self):
        res = self.client().get('/api/categories/40/questions/')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Not found")

    def test_get_quiz_question(self):
        res = self.client().post('/api/quizzes/', json=self.new_quiz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    def test_422_get_quiz_question(self):
        res = self.client().post('/api/quizzes/')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['error'], 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "unprocessable")






# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()