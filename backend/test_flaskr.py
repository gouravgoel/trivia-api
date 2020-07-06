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
        self.database_path = "postgres://{}@{}/{}".format('postgres', 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    '''
    tests for each successful operation and for expected errors.
    '''

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_404_if_categories_not_present(self):
        res = self.client().get('/categories/1000')
        data = json.load(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'], 'File Not Found')

    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertEqual(len(data['books']))

    def test_404_sent_request_beyond_valid_page(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'File Not Found')

    def test_delete_book(self):
        res = self.client().delete('/questions/3')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 3).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 3)
        self.assertEqual(data['total_questions'])
        self.assertEqual(question, None)

    def test_404_if_question_does_not_exsist(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.satus_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable Request')

    def test_post_new_Questions(self):
        post_data = {
            'question': 'What is the udacity web address',
            'answer': 'udacity.com',
            'difficulty': 1,
            'category': 2
        }
        res = self.client().post('/questions', json = post_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_422_if_post_question_is_not_possible(self):
        post_data = {
            'question': 'What is the udacity web address',
            'answer': 'udacity.com',
            'difficulty': 1,
            'category': 2
        }
        res = self.client().post('/questions/44', json = post_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable Request')

    def test_search_new_question(self):
        post_data = {
            'searchTerm': 'udacity'
        }
        res = self.client().post('/questions/search', json = post_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_422_if_post_search_not_possibl(self):
         post_data = {
             'searchTerm': 'udacity'
         }
         res = self.client().post('/questions/search/5', json = post_data)
         data = json.loads(res.data)

         self.assertEqual(res.status_code, 422)
         self.assertEqual(data['success'], False)
         self.assertEqual(data['message'], 'Unprocessable Request')

    def test_404_if_post_search_term_is_none(self):
        post_data = {
            'searchTerm': ''
        }
        res = self.client().post('/questions/search', json = post_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'File Not Found')

    def test_404_if_searched_question_is_not_present(self):
        post_data = {
            'searchTerm': 'randomText'
        }
        res = self.client().post('/question/search', json = post_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'File Not Found')

    def test_get_category_wise_paginated_questions(self):
        res = self.client.get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_404_if_category_is_not_present(self):
        res = self.client.get('/categories/1000/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_play_quiz(self):
        new_quiz_round = {'previous_questions': [],
                          'quiz_category': 
                          {'type': 'Entertainment', 'id': 5}}

        res = self.client().post('/quizzes', json=new_quiz_round)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_422_play_quiz(self):
        new_quiz_round = {'previous_questions': []}
        res = self.client().post('/quizzes', json=new_quiz_round)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Unprocessable Request")

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
