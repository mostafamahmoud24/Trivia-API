import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10

def paginate(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page -1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    return current_questions
  

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response   

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''

  @app.route('/api/categories/', methods=['GET'])
  def get_categories():
    categories = Category.query.all()
    formatted_categories = [category.format() for category in categories]
    new_categories = {}

    for i in formatted_categories:
      new_categories[i["id"]] = i["type"]

    if categories is None:
      abort(404)
    else:
      return jsonify({
      "success": True,
      "categories":new_categories
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

  @app.route('/api/questions/', methods=['GET'])
  def retrieve_questions():
    selection = Question.query.order_by(Question.id).all()
    current_questions = paginate(request, selection)

    categories = Category.query.all()
    formatted_categories = [category.format() for category in categories]
    new_categories = {}
    current_categories = []
    for i in formatted_categories:
      new_categories[i["id"]] = i["type"]
      current_categories.append(i["id"])

    if current_questions == []:
      abort(404)

    return jsonify({
      'success': True,
      'questions': current_questions,
      'categories': new_categories,
      'current_category': current_categories,
      'total_questions': len(Question.query.all())
      })

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

  @app.route('/api/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    question = Question.query.get(question_id)

    if question is None:
      abort(404)
    else:
      db.session.delete(question)
      db.session.commit()
      return jsonify({
      "success": True,
      "message": f'question with the id of {question_id} was deleted successfully'
    })

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

  @app.route('/api/questions/', methods=['POST'])
  def create_question():
    body = request.get_json()
    new_question = Question(body.get('question'), body.get('answer'), body.get('category'), int(body.get('difficulty')))

    

    if (body.get('question') == "" or body.get('answer') == "" or body.get('category') == "" or body.get('difficulty') == ""):
      abort(400)
    else:
      db.session.add(new_question)
      db.session.commit()
      return jsonify({
      "success": True,
      "message": "question created successfully"
      })  


  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

  @app.route('/api/questions/search/', methods=['POST'])
  def search_questions():

    body = request.get_json()
    search = body.get('searchTerm')
    questions = Question.query.filter(Question.question.ilike(f'%{search}%')).all()
    formatted_questions = [question.format() for question in questions] 

    categories = Category.query.all()
    formatted_categories = [category.format() for category in categories]
    new_categories = {}
    current_categories = []
    for i in formatted_categories:
      new_categories[i["id"]] = i["type"]
      current_categories.append(i["id"])

    if questions == [] or search == '':
      abort(404)
    else:
      return jsonify({
      'success': True,
      'questions': formatted_questions,
      'categories': new_categories,
      'current_category': current_categories,
      'total_questions': len(formatted_questions)
      })

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''

  @app.route('/api/categories/<int:category_id>/questions/', methods=['GET'])
  def get_category_questions(category_id):
    questions = Question.query.filter_by(category = int(category_id)).all()
    formatted_questions = [question.format() for question in questions]

    categories = Category.query.filter_by(id = category_id).all()
    formatted_categories = [category.format() for category in categories]
    new_categories = {}
    current_categories = []
    for i in formatted_categories:
      new_categories[i["id"]] = i["type"]
      current_categories.append(i["id"])

    if questions == []:
      abort(404)
    else:
      return jsonify({
      'success': True,
      'questions': formatted_questions,
      'categories': new_categories,
      'current_category': current_categories,
      'total_questions': len(formatted_questions)
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

  #The answer validate on the frontend is broken for answers with spaces
  @app.route('/api/quizzes/', methods=['POST'])
  def get_quiz_question():
    try:
      body = request.get_json()
      previous_questions = body.get("previous_questions")
      quiz_category = body.get("quiz_category")
      all_questions = Question.query.all()

      new_questions = []

      if quiz_category['id'] == 0:
        new_questions = all_questions
      else:
        for question in all_questions:
          if str(question.category) == str(quiz_category['id']):
            new_questions.append(question)


      if len(new_questions) >= 1:
        random_question = new_questions[random.randint(0, len(new_questions) - 1)].format()
      else:
        random_question = ""


      return jsonify({
        'success': True,
        'question': random_question,
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
        "success": False, 
        "error": 404,
        "message": "Not found"
        }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "message": "unprocessable",
      "error": 422,
      }), 422

  @app.errorhandler(400)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "message": "Bad Request",
      "error": 400,
      }), 400
  
  return app

    