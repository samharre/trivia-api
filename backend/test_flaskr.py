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
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['categories']))


    def test_get_categories_by_id(self):
        res = self.client().get('/categories/1')
        data = json.loads(res.data)

        self.check_status_code_404(res.status_code, data)
        
    
    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['categories']))
        self.assertEqual(data['current_category'], None)
        

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.check_status_code_404(res.status_code, data)

    
    def test_get_quetions_by_category(self):
        category_id = 1 # Science
        res = self.client().get(f'/categories/{category_id}/questions')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['current_category'], category_id)
        

    def test_404_get_quetions_by_non_existent_category(self):
        category_id = 100
        res = self.client().get(f'/categories/{category_id}/questions')
        data = json.loads(res.data)

        self.check_status_code_404(res.status_code, data)


    def test_search_questions_by_term(self):
        search_term = 'title'
        res = self.client().post('/questions/search', json={'searchTerm': search_term})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['questions']))
        self.assertEqual(data['total_questions'], 2)
        self.assertEqual(data['current_category'], None)


    def test_search_questions_by_non_existent_term(self):
        search_term = 'test123'
        res = self.client().post('/questions/search', json={'searchTerm': search_term})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['questions']), 0)
        self.assertEqual(data['total_questions'], 0)
        self.assertEqual(data['current_category'], None)


    def test_400_fail_searching_questions_without_body(self):
        res = self.client().post('/questions/search')
        data = json.loads(res.data) 

        self.check_status_code_400(res.status_code, data)


    def test_422_search_questions_without_search_term(self):
        res = self.client().post('/questions/search', json={'test': '123'})
        data = json.loads(res.data) 

        self.check_status_code_422(res.status_code, data)


    def test_create_new_question(self):
        total_questions_prev = len(Question.query.all())
    
        question = self.new_question()
        res = self.client().post('/questions', json=question)
        data = json.loads(res.data)

        total_questions = len(Question.query.all())

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['question_id'])
        self.assertEqual(total_questions, total_questions_prev + 1)


    def test_400_fail_creating_question_without_body(self):
        res = self.client().post('/questions')
        data = json.loads(res.data)

        self.check_status_code_400(res.status_code, data)


    def test_405_if_question_creation_not_allowed(self):
        res = self.client().post('/questions/1', json=self.new_question())
        data = json.loads(res.data)

        self.check_status_code_405(res.status_code, data)


    def test_422_fail_creating_question_without_required_item(self):
        question = self.new_question()
        question.pop('answer')

        res = self.client().post('/questions', json=question)
        data = json.loads(res.data)

        self.check_status_code_422(res.status_code, data)    


    def test_delete_question(self):
        question_id = 23
        res = self.client().delete('/questions/{}'.format(question_id))
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == question_id).one_or_none()
        
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['question_id'], question_id)
        self.assertEqual(question, None)


    def test_422_if_question_to_delete_does_not_exist(self):
        question_id = 10000
        res = self.client().delete('/questions/{}'.format(question_id))
        data = json.loads(res.data)

        self.check_status_code_422(res.status_code, data)


    def test_play_quizz(self):
        body = {
            "quiz_category": {"type": "click", "id": 0}, 
            "previous_questions":[]
        }
        res = self.client().post('/quizzes', json=body)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['question']))


    def test_400_fail_play_quizz_without_body(self):
        res = self.client().post('/quizzes')
        data = json.loads(res.data)

        self.check_status_code_400(res.status_code, data)


    def test_404_fail_play_quizz_wrong_route(self):
        res = self.client().patch('/quizzes/5')
        data = json.loads(res.data)

        self.check_status_code_404(res.status_code, data)

    
    def test_422_fail_play_quizz_without_category(self):
        body = {"previous_questions":[5,9,2,4,6]}
        res = self.client().post('/quizzes', json={'test': '123'})
        data = json.loads(res.data) 

        self.check_status_code_422(res.status_code, data)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()