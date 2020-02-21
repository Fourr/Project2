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
        self.database_path = "postgres://postgres/password".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            "question": "How tall is Lebron James?", 
            "answer": "6-9",
            "category":"6",
            "difficulty": "1"
            }
        self.new_bad_question = {
            "questions": "How tall is Lebron James?", 
            "answer": "6-9",
            "category":"6",
            "difficulty": "1"
            }
        self.new_search = {
            "searchTerm": "Lebron"
        }
        self.new_bad_search = {
            "searchTerm": "LLebron"
        }

        self.new_play = {
            "previous_questions": [],
            "quiz_category":
                {
                    "type": "Science",
                    "id": 1
                }
        }
        self.new_bad_play = {
            "previous_questions": [],
            "quiz_category":
                {
                    "type": "Science",
                    "idd": 7
                }
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
    def test_catgeories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertTrue(data['categories'])

    def test_catgeories_failure(self):
        res = self.client().get('/categories/')
        data = json.loads(res.data)
        self.assertEqual(res.status_code,404)
        self.assertEqual(data['message'],'resource not found')

    def test_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(data['totalQuestions'])
        self.assertTrue(data['categories'])
        #self.assertTrue(data['currentCategory'])

    def test_questions_failure(self):
        res = self.client().get('/questions?page=200')
        data = json.loads(res.data)
        self.assertEqual(res.status_code,404)
        self.assertEqual(data['message'],'resource not found')


    # def test_delete_question(self):
    #     res = self.client().delete('/questions/5')
    #     data = json.loads(res.data)
    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(data['deleted'],5)

    def test_delete_question_failure(self):
        res = self.client().delete('/questions/100')
        data = json.loads(res.data)
        self.assertEqual(res.status_code,422)
        self.assertEqual(data['message'],'unprocessable')

    def test_create_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['created'])
        self.assertTrue(data['questions'])
        self.assertTrue(data['totalQuestions'])

    def test_create_question_failure(self):
        res = self.client().post('/questions', json=self.new_bad_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['message'],'unprocessable')

    def test_search_question(self):
        res = self.client().post('/questions/search', json=self.new_search)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(data['questions'])
        self.assertTrue(data['totalQuestions'])

    def test_search_question_failure(self):
        res = self.client().post('/questions/search', json=self.new_bad_search)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['message'],'unprocessable')

    def test_question_catgeories(self):
        res = self.client().get('/categories/2/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertTrue(data['questions'])
        self.assertTrue(data['totalQuestions'])

    def test_question_catgeories_failure(self):
        res = self.client().get('/categories/7/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code,404)
        self.assertEqual(data['message'],'resource not found')


    def test_play(self):
        res = self.client().post('/quizzes', json=self.new_play)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question'])

    def test_play_failure(self):
        res = self.client().post('/quizzes', json=self.new_bad_play)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['message'],'unprocessable')
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()