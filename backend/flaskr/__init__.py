import os
from flask import Flask, request, abort, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def format_error(status_code, message):
    return jsonify({
        'success': False,
        'error': status_code,
        'message': message
    }), status_code


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allows-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allows-Methods', 'GET,POST,DELETE,OPTIONS')
        return response


    @app.route('/categories')
    def get_categories():
        categories = Category.query.order_by(Category.id).all()

        return jsonify({
            'categories': {category.id: category.type for category in categories},
            'success': True
        })


    @app.route('/questions')
    def get_questions():
        categories = Category.query.order_by(Category.id).all()
        questions = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, questions)

        if not current_questions:
          abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(questions),
            'categories': {category.id: category.type for category in categories},
            'current_category': None
        })


    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.get(question_id)
        if not question:
            abort(422)

        try:
            question.delete()
            
            return jsonify({
                'success': True,
                'question_id': question_id
            })
        except:
            abort(500)
        

    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()
        if not body:
            abort(400)
        
        question = body.get('question')
        answer = body.get('answer')
        difficulty = body.get('difficulty')
        category = body.get('category')
        if not (question and answer and difficulty and category):
            abort(422)

        try:
            obj_question = Question(
                question=question, answer=answer, category=category, difficulty=int(difficulty)
            )
            obj_question.insert()

            return jsonify({
                'success': True,
                'question_id': obj_question.id
            })
        except:
            abort(500)


    @app.route('/questions/search', methods=['POST'])
    def search_question_by_term():
        body = request.get_json()
        if not body:
            abort(400)

        search_term = body.get('searchTerm', '')
        if not search_term:
            abort(422)

        questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).order_by(Question.id).all()
        return jsonify({
            'success': True,
            'questions': [question.format() for question in questions],
            'total_questions': len(questions),
            'current_category': None
        })
      

    @app.route('/categories/<int:category_id>/questions')
    def get_questions_by_category(category_id):
        category = Category.query.get(category_id)
        if not category:
            abort(404)

        questions = Question.query.filter(Question.category == category_id).all()
        return jsonify({
            'success': True,
            'questions': [question.format() for question in questions],
            'total_questions': len(questions),
            'current_category': category_id
        })
      

    @app.route('/quizzes', methods=['POST'])
    def play_quizz():
        body = request.get_json()
        if not body:
            abort(400)
        
        quiz_category = body.get('quiz_category')
        previous_questions = body.get('previous_questions', [])
        if not (quiz_category):
            abort(422)

        print('BODY FRONT', body)
        try:
            category_id = quiz_category.get('id')
            if category_id:
                questions = Question.query.\
                    filter(Question.category == category_id).\
                    filter(Question.id.notin_(previous_questions)).all()
            else:
                questions = Question.query.\
                    filter(Question.id.notin_(previous_questions)).all()

            return jsonify({
                'success': True,
                'question': questions[random.randrange(0, len(questions))].format() if len(questions) else None
            })
        except:
            abort(500)


    @app.errorhandler(400)
    def bad_request(error):
        return format_error(400, 'Bad request')


    @app.errorhandler(404)
    def not_found(error):
        return format_error(404, 'Resource not found')


    @app.errorhandler(405)
    def method_not_allowed(error):
        return format_error(405, 'Method not allowed')


    @app.errorhandler(422)
    def unprocessable(error):
        return format_error(422, 'Unprocessable')


    @app.errorhandler(500)
    def server_error(error):
        return format_error(500, 'Internal server error')


    return app