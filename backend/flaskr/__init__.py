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

  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app)

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allows-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allows-Methods', 'GET,POST,DELETE,OPTIONS')
    return response


  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def get_categories():
    categories = Category.query.order_by(Category.id).all()

    return jsonify({
      'categories': {category.id: category.type for category in categories},
      'success': True
    })


  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories.
  
  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
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


  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
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
      

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
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


  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_question_by_term():
    body = request.get_json()
    if not body:
      abort(400)

    search_term = body.get('searchTerm', '')
    if search_term:
      questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).order_by(Question.id).all()
    
      return jsonify({
        'success': True,
        'questions': [question.format() for question in questions],
        'total_questions': len(questions),
        'current_category': None
      })
    else:
      abort(422)


  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''


  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

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

    