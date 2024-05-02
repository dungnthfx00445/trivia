import os
from config import SQLALCHEMY_DATABASE_URI
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from sqlalchemy.orm import load_only
from sqlalchemy import cast, Integer

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10

def pagination_questions(request, selection):
    page = request.args.get("page", 1, type = int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    return current_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)

    if test_config is None:
        setup_db(app)  
    else:
        setup_db(app, SQLALCHEMY_DATABASE_URI)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        response.headers.add(
            "Access-Control-Allow-Origin", "*"
        )
        return response

    @app.route("/categories", methods=["GET"])
    def categories():
        try:
            categories = db.session.query(Category).order_by(Category.id).all()
            return jsonify({
                'categories': {
                    category.id: category.type for category in categories
                },
                'success': True
            })
        except:
            abort(422)
        
        
    @app.route("/questions", methods=["GET"])
    def questions():
        selection = db.session.query(Question).options(load_only(Question.question, Question.category)).order_by(Question.id)
        categories = Category.query.all()
        questions = Question.query.all()
        paginate_questions = pagination_questions(request, selection)

        if len(paginate_questions) == 0:
            abort(404)

        return jsonify({
            "questions": list(paginate_questions),
            "total_questions": len(questions),
            "current_category": "sten",
            "categories": {
                category.id: category.type for category in categories
            },
            "success": True
        })

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        try:
            question = Question.query.get(question_id)

            if question is None:
                abort(404)
            question.delete()
            return jsonify({
                "deleted": question_id,
                "success": True
            })
        except:
            abort(422)

    @app.route("/questions", methods = ["POST"])
    def add_question():
        payload = request.get_json()
        new_question = payload.get("question")
        new_answer = payload.get("answer")
        new_category = payload.get("category")
        new_difficulty = payload.get("difficulty")

        if (payload, new_question, new_answer, new_category, new_difficulty) == None:
            abort(400)
        try:
            question = Question(
                question=new_question,
                answer=new_answer,
                category=new_category,
                difficulty=new_difficulty
            )
            question.insert()
            return jsonify({
                "created": question.id,
                "success": True
            })
        except:
            abort(422)

    @app.route("/questions/search",  methods = ["POST"])
    def search_questions():
        search_term = request.get_json().get("searchTerm")
        selection = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()

        if search_term is None:
            abort(404)
        search_questions = pagination_questions(request, selection)
        return jsonify({
            "questions": list(search_questions),
            "total_questions": len(selection),
            "success": True
        })
        
    @app.route("/categories/<int:category_id>/questions", methods=["GET"])
    def get_list_questions_by_category(category_id):
        category = Category.query.get(category_id)

        if category is None:
            abort(404)
        
        questions = Question.query.filter(cast(Question.category, Integer) == category_id).all()
        if len(questions) == 0:
            return abort(404)
        format_questions = [question.format() for question in questions]
        return jsonify({
            "questions": format_questions,
            "total_questions": len(format_questions),
            "current_category": category.type,
            "success": True
        })
 
    @app.route("/quizzes", methods = ["POST"])
    def play_quiz():
        payload = request.get_json()
        previous_questions = payload.get("previous_questions")
        quiz_category = payload.get("quiz_category")

        if not quiz_category:
            abort(400)
        category_id = quiz_category.get("id")
        if category_id == 0:
            questions = Question.query.all()
        else:
            questions = Question.query.filter(Question.category == category_id).all()
        format_questions = [ question.format() for question in questions]
        if previous_questions:
            format_questions = [question for question in format_questions if question.get("id") not in previous_questions]
        if len(format_questions) == 0:
            return jsonify({
                "success": False
            })
        question = random.choice(format_questions)
        return jsonify({
            "question": question,
            "success": True
        })
   
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Not found"
        }), 404
    
    @app.errorhandler(422)
    def not_processable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Not processable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad request"
        }), 400

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Internal server error"
        }), 500

    return app

