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
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
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


    def new_question(self):
        return {
            'question': 'Who discovered the Atom?',
            'answer': 'Democritus',
            'difficulty': 3,
            'category': 1
        }


    def check_status_code_400(self, status_code, data):
        self.assertEqual(status_code, 400)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'].lower(), 'bad request')


    def check_status_code_404(self, status_code, data):
        self.assertEqual(status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'].lower(), 'resource not found')


    def check_status_code_405(self, status_code, data):
        self.assertEqual(status_code, 405)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'].lower(), 'method not allowed')


    def check_status_code_422(self, status_code, data):
        self.assertEqual(status_code, 422)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'].lower(), 'unprocessable')


    # ---------- Testes ---------- #

    def test_get_categories(self):
        res = self.client().get('categories')
        data = json.loads(res.data)

        self.assertEquals(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['categories']))
        
    
    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['totalQuestions'])
        self.assertTrue(len(data['categories']))
        self.assertFalse(data['currentCategory'])
        

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.check_status_code_404(res.status_code, data)

    
    def test_get_quetions_per_category(self):
        id_category = 1 # Science
        res = self.client().get(f'/categories/{id_category}/questions')
        
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['totalQuestions'])
        self.assertEqual(data['currentCategory'], id_category)
        

    def test_404_get_quetions_per_category_non_existent(self):
        id_category = 100
        res = self.client().get(f'/categories/{id_category}/questions')

        self.check_status_code_404(res.status_code, data)


    def test_search_questions_per_term(self):
        search_term = 'peanut'
        res = self.client().post('/questions/search', json={'searchTerm': search_term})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['totalQuestions'])
        self.assertFalse(data['currentCategory'])


    def test_400_fail_searching_questions_without_body(self):
        res = self.client().post('/questions/search')
        data = json.loads(res.data) 

        self.check_status_code_400(res.status_code, data)


    def test_404_search_questions_per_term_non_existent(self):
        search_term = '#%$^&!abc'
        res = self.client().post('/questions/search', json={'searchTerm': search_term})
        data = json.loads(res.data) 

        self.check_status_code_404(res.status_code, data)


    def test_create_new_question(self):
        total_questions = len(Question.query.all())
    
        question = self.new_question()
        res = self.client().post('/questions', json=question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['questions']))
        self.assertEqual(data['totalQuestions'], total_questions + 1)
        self.assertEqual(data['currentCategory'], question['category'])


    def test_400_fail_creating_new_question_without_body(self):
        res = self.client().post('/questions')
        data = json.loads(res.data)

        self.check_status_code_400(res.status_code, data)


    def test_405_if_question_creation_not_allowed(self):
        res = self.client().post('/questions/1', json=self.new_question())
        data = json.loads(res.data)

        self.check_status_code_405(res.status_code, data)


    def test_delete_question(self):
        id_question = 5
        question_category = 4
        total_questions = len(Question.query.all())

        res = self.client().delete(f'/questions/{id_question}')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == id).one_or_none()

        self.assertEquals(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['questions']))
        self.assertEqual(data['totalQuestions'], total_questions - 1)
        self.assertEqual(data['currentCategory'], question_category)
        self.assertEquals(question, None)


    def test_422_if_question_to_delete_does_not_exist(self):
        id_question = 10000
        res = self.client().delete(f'/questions/{id_question}')
        data = json.loads(res.data)

        self.check_status_code_422(res.status_code, data)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()