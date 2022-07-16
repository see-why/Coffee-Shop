import os
import sys
from flask import Flask, request, jsonify, abort
from sqlalchemy import desc, exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


@app.after_request
def after_request(response):
    response.headers.add(
        "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
    )
    response.headers.add(
        "Access-Control-Allow-Methods", "GET,POST,PATCH,DELETE,OPTIONS"
    )
    return response


'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
# db_drop_and_create_all()

# ROUTES


@app.route('/drinks')
def get_drinks():
    drinks = Drink.query.order_by(desc(Drink.id)).all()
    formatted_drinks = [drink.short() for drink in drinks]

    return jsonify({
        "success": True,
        "drinks": formatted_drinks
    })


@app.route('/drinks-detail')
@requires_auth("get:drinks-detail")
def get_drinks_details(payload):
    drinks = Drink.query.order_by(desc(Drink.id)).all()
    formatted_drinks = [drink.long() for drink in drinks]

    return jsonify({
        "success": True,
        "drinks": formatted_drinks
    })


@app.route("/drinks", methods=["POST"])
@requires_auth("post:drinks")
def create_drinks(payload):
    body = request.get_json()

    new_title = body.get("title", None)
    new_recipe = body.get("recipe", None)

    try:
        drink = Drink(title=new_title, recipe=json.dumps([new_recipe]))
        drink.insert()

        return jsonify(
            {
                "success": True,
                "drinks": [drink.long()]
            }
        )

    except BaseException:
        print(sys.exc_info())
        abort(422)


@app.route("/drinks/<int:id>", methods=["PATCH"])
@requires_auth("patch:drinks")
def update_drinks(payload, id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()

    if drink is None:
        abort(404)

    body = request.get_json()

    new_title = body.get("title", None)
    new_recipe = body.get("recipe", None)

    try:
        drink.title = drink.title if new_title is None else new_title
        drink.recipe = drink.recipe if new_recipe is None else new_recipe

        drink.update()

        return jsonify(
            {
                "success": True,
                "drinks": [drink.long()]
            }
        )

    except BaseException:
        print(sys.exc_info())
        abort(422)


@app.route("/drinks/<int:id>", methods=["DELETE"])
@requires_auth("delete:drinks")
def delete_drink(payload, id):
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()

        if drink is None:
            abort(404)

        drink.delete()

        return jsonify(
            {
                "success": True
            }
        )

    except BaseException:
        print(sys.exc_info())
        abort(422)


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Server Error"
    }), 500


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad request"
    }), 400


@app.errorhandler(405)
def not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "Method not allowed"
    }), 405


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Not found"
    }), 404


@app.errorhandler(AuthError)
def not_found(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), error.status_code
