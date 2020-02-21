import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate(request, selection):
  page = request.args.get('page', 1 ,type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE
  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions



#psql -U postgres -d trivia -1 -f trivia.sql
def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app)

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
# CORS Headers 
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response
  
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''

  #curl http://localhost:5000/categories
  @app.route('/categories', methods=['GET'])
  def getCategories():
    selection = Category.query.order_by(Category.id).all()
    categories = {}
    for i in range(len(selection)):
      categories[selection[i].id] = selection[i].type

    if len(selection) == 0:
      abort(404)

    return jsonify({
      'categories': categories
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

  #curl http://localhost:5000/questions?page=1
  @app.route('/questions', methods=['GET'])
  def getQuestions():
    print(request)

    selection_categories = Category.query.order_by(Category.id).all()

    categories = {}
    for i in range(len(selection_categories)):
      categories[selection_categories[i].id] = selection_categories[i].type

    selection_question = Question.query.order_by(Question.id).all()
    current_questions = paginate(request, selection_question)
    length = len(selection_question)
    if len(current_questions) == 0:
      abort(404)

    
    return jsonify({
      'questions': current_questions,
      'totalQuestions': length,
      'categories': categories,
      'currentCategory': None
      })

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  #curl http://localhost:5000/questions/24 -X DELETE
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()

      if question is None:
        abort(404)

      question.delete()

      return jsonify({
        'deleted': question.id,
        })
    except:
      abort(422)


  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  #curl -X POST -H "Content-Type: application/json" -d '{"question": "How tall is Lebron James?", "answer": "6-9","category":"6","difficulty": "1"}' http://localhost:5000/questions
  @app.route('/questions', methods=['POST'])
  def create_question():

    body = request.get_json()

    new_question = body.get('question')
    new_answer = body.get('answer')
    new_category = body.get('category')
    new_difficulty = body.get('difficulty')

    if not new_question or not new_answer or not new_category or not new_difficulty:
      abort(422)
    try:
      question= Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
      question.insert()

      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate(request, selection)

      return jsonify({
        'created': question.id,
        'questions': current_questions,
        'totalQuestions': len(Question.query.all())
        })
    except:
      abort(422)
  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  #curl -X POST -H "Content-Type: application/json" -d '{"searchTerm": "LLebron"}' http://localhost:5000/questions/search
  @app.route('/questions/search', methods=['POST'])
  def retrieve_questions_based_on_search():
    body = request.get_json()
    new_search = body.get('searchTerm', None)
    try:
      selection = Question.query.filter(Question.question.contains(new_search)).all()
      #current_questions = [question.format() for question in selection]
      current_questions = paginate(request, selection)
      if not current_questions:
      	abort(422)
      return jsonify({
        'questions': current_questions,
        'totalQuestions': len(current_questions),
        'currentCategory': None
        })
    except:
      abort(422)

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  #curl http://localhost:5000/category/2/questions
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def retrieve_questions_based_on_category(category_id):
    selection = Question.query.order_by(Question.id).filter_by(category=category_id).all()
    current_questions = paginate(request, selection)

    if len(current_questions) == 0:
      abort(404)

    return jsonify({
      'questions': current_questions,
      'totalQuestions': len(current_questions)
      })

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


  #curl -X POST -H "Content-Type: application/json" -d '{"previous_questions": [21,22], "quiz_category": {"type": "Science", "id": 1}}' http://localhost:5000/quizzes
  @app.route('/quizzes', methods=['POST'])
  def play():
    body = request.get_json()
    new_previous_questions = body.get('previous_questions', None)
    new_quiz_category = body.get('quiz_category', None)
    selection = ''
    wentThrough = False
    try:
      if not new_previous_questions and new_quiz_category['id']==0:
        selection = Question.query.all()
        wentThrough = True
        
      elif not new_previous_questions and new_quiz_category['id']:
        selection = Question.query.filter_by(category=new_quiz_category['id']).all()
        wentThrough = True
        
      elif new_previous_questions and new_quiz_category['id']==0:
        selection = Question.query.filter(~Question.id.in_(new_previous_questions)).all()
        wentThrough = True
   
      elif new_previous_questions and new_quiz_category['id']:
        selection = Question.query.filter(~Question.id.in_(new_previous_questions)).filter_by(category=new_quiz_category['id']).all()
        wentThrough = True

      else:
        abort(500)

      if not selection and wentThrough:
        final_question = ''

      elif selection and wentThrough:
      	final_question = random.choice(selection).format()

      else:
        abort(500)

      return jsonify({
        'question': final_question,
      })
    except:
      abort(422)


  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'error': 404,
      'message': 'resource not found'
      }), 404

  @app.errorhandler(422)
  def not_found(error):
    return jsonify({
      'error': 422,
      'message': 'unprocessable'
      }), 422

  @app.errorhandler(400)
  def not_found(error):
    return jsonify({
      'error': 400,
      'message': 'bad request'
      }), 400  

  @app.errorhandler(500)
  def not_found(error):
    return jsonify({
      'error': 500,
      'message': 'internal server error'
      }), 500
  
  return app

    