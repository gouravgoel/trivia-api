import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

#-----------------------------------------------------------------------------#
# function_to_return_paginated_questions
#-----------------------------------------------------------------------------#

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page-1) * QUESTIONS_PER_PAGE
    end = start * QUESTIONS_PER_PAGE
    
    questions = [Question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

# -----------------------------------------------------------------------#
# cors-set-up. Allow '*' for origins
# -----------------------------------------------------------------------#

    cors = CORS(app, resources={r"/*": {"origins": "*"}})

# -----------------------------------------------------------------------#
# After_request decorator to set Access-Control-Allow
# -----------------------------------------------------------------------#

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 
                             'Content-Type, Authorization')
        response.headers.add('Access-Control_allow-Methods', 
                             'GET, POST, PATCH, DELETE, OPTIONS')
        return response

# -----------------------------------------------------------------------#
# Endpoint to handle GET requests
# for all available categories.
# -----------------------------------------------------------------------#

    @app.route('/categories')
    def retrieve_categories():
        selection = Category.query.order_by(Category.id).all()

        if len(selection) == 0:
            abort(404)

        categories = [Category.format() for category in selection]

        return jsonify({
            'success': True,
            'categories': categories
        })

# -----------------------------------------------------------------------#
# endpoint to handle GET requests for questions,
# including pagination (every 10 questions).
# This endpoint returns a list of questions,
# number of total questions, current category, categories.
# -----------------------------------------------------------------------#

    @app.route("/questions")
    def retrieve_questions():
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)
        categories = list(map(Category.format, Category.query.all()))

        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(Question.query.all()),
            'current_category': None,
            'categories': categories
        })

# -----------------------------------------------------------------------#
# Endpoint to DELETE question using a question ID.
# -----------------------------------------------------------------------#

    @app.route('/questions/<int:q_id>', methods=['DELETE'])
    def delete_question(q_id):
        try:
            question = Question.query.filter(Question.id == q_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'deleted': q_id
            })
        finally:
          abort(422)

# -----------------------------------------------------------------------#
# Endpoint to POST a new question,
# which will require the question and answer text,
# category, and difficulty score.
# -----------------------------------------------------------------------#

    @app.route('/questions', methods=['POST'])
    def post_question():
        body = request.get_json()

        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_category = body.get('category', None)
        new_difficulty = body.get('difficulty', None)

        try:
            question = Question(question=new_question, answer=new_answer, 
                                category=new_category, difficulty=new_difficulty)
            question.insert()

            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'created': question.id,
            })

        finally:
            abort(422)

# -----------------------------------------------------------------------#
# POST endpoint to get questions based on a search term.
# It returns any questions for whom the search term
# is a substring of the question.
# -----------------------------------------------------------------------#

    @app.route('/questions/search', methods=['POST'])
    def search_question():
        try:
            body = request.get_json()
            new_searchTerm = body.get('searchTerm', None)

            if new_searchTerm is not None:
                selection = Question.query.filter(Question.question
                            .ilike('%' + new_searchTerm + '%'))
                searched_questions = paginate_questions(request, selection)

                if len(searched_questions) > 0:
                    return jsonify({
                        'success': True,
                        'questions': searched_questions,
                        'total_questions': len(Question.query.all())
                    })

                else:
                    abort(404)

            else:
                abort(404)    

        finally:
            abort(422)

# -----------------------------------------------------------------------#
# GET endpoint to get questions based on category.
#-----------------------------------------------------------------------#

    @app.route('/categories/<int:category_id>/questions')
    def question(category_id):
        try:
            questions = Question.query.filter(Question.category == 
                                              str(category_id)).one_or_none()

            return jsonify({
                'success': True,
                'questions': [questions.format() for question in questions],
                'total_questions': len(questions),
                'current_category': category_id
            })

        finally:
            abort(404)

# -----------------------------------------------------------------------#
# POST endpoint to get questions to play the quiz.
# This endpoint should take category and previous question parameters
# and return a random questions within the given category,
# if provided, and that is not one of the previous questions.
# -----------------------------------------------------------------------#

    @app.route('/quizzes', methods=['POST'])
    def retrieve_quiz_questions():
        body = request.get_json()
        if (('quiz_category' in body
             and 'id' in body['quiz_category'])
             and 'previous_questions' in body):
            questions_query = Question.query.filter_by(
            category=body['quiz_category']['id']
            ).filter(
            Question.id.notin_(body["previous_questions"])
            ).all()
            length_of_available_question = len(questions_query)
            if length_of_available_question > 0:
                return jsonify({
                    "success": True,
                    "question": Question.format(
                                questions_query[random.randrange(
                                0,
                                length_of_available_question
                                )]
                                )
                 })
            else:
                return jsonify({
                    "success": False,
                    "question": None
                })

        abort(422)

# -----------------------------------------------------------------------#
# Error handlers
# -----------------------------------------------------------------------#

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'message': "Bad Request",
            'error': 400
        }), 400

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'message': 'Unprocessable Request',
            'error': 422
        }), 422

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'message': 'File Not Found',
            'error': 404
        }), 404

    return app
