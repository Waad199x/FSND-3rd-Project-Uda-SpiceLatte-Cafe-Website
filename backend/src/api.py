import os
from flask import Flask, request, jsonify, abort, Response
from sqlalchemy import exc
import json
from flask_cors import CORS
from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth
from typing import Dict
app = Flask(__name__)
setup_db(app)
CORS(app)

# 9/9  DONE

'''
    Barista should get 403 error for all actions
            except short and long drink requests

    Public users should get 401 error for all actions
            except short drink request

    Manager should get all actions as 200

    The URL to access the frontend is http://localhost:4200/
'''

'''
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()


'''
    GET /drinks (Public endpoint)
    for getting the drinks without the recipe
'''


@app.route('/drinks')
def Display_Drinks():

    drinks = []
    drink = Drink.query.all()
    for d in drink:
        drinks.append(d.short())

    if len(drinks) == 0:
        abort(404)

    else:
        return jsonify({
            "success": True,
            "drinks": drinks}), 200


'''
    GET /drinks-detail
        (Private endpoint) for the Baristas and the managers only
'''


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def Display_full_Drinks(payload):

    drinks = []
    drink = Drink.query.all()
    for d in drink:
        drinks.append(d.long())

    return jsonify({
            "success": True,
            "drinks": drinks}), 200


'''
    POST /drinks
        (Exclusive endpoint for the managers only)
                Used to Add new drinks to the website

'''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def Create_full_Drinks(payload):

    data = request.get_json()

    drink_title = data['title']
    recipe = data['recipe']
    drink_recipe = json.dumps(recipe)

    new_drink = Drink(
        title=drink_title, recipe=drink_recipe)

    new_drink.insert()

    return jsonify({
        "success": True,
        "drinks": [new_drink.long()]}), 200


'''
    PATCH /drinks/<id>
        (Exclusive endpoint for the managers only)
                Used to update changes on existing drinks
'''


@app.route('/drinks/<int:id>', methods=['Patch'])
@requires_auth('patch:drinks')
def Update_Drink(payload, id):

    drink = Drink.query.filter(Drink.id == id).one_or_none()

    body = request.get_json()

    if 'title' in body:
        drink.title = body['title']

    if 'recipe' in body:
        drink.recipe = json.dumps(body['recipe'])

    drink.update()

    return jsonify({
        "success": True,
        "drinks": [drink.long()]}), 200


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        (Exclusive endpoint for the managers only)
                Used to delete existing drink
                returns error if the drink dowsn't exist
'''


@app.route('/drinks/<int:id>', methods=['Delete'])
@requires_auth('delete:drinks')
def Delete_Drink(payload, id):

    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()

        if drink is None:
            abort(404)
        else:
            drink.delete()

        return jsonify({
            "status": 200,
            "success": True,
            "delete": id})

    except AuthError:
        return jsonify({
            "status": 400,
            "success": False}), 200


'''
The following are Error handlers for unprocessable entities
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def not_found(error):  # Usualy when there is a problem in the url
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
        }), 404


@app.errorhandler(400)
def AuthError(error):
    return jsonify({
        'code': 'invalid_access_attempt',
        'description': 'Unable to find the appropriate permission.'
    }, 400)


class AuthError(Exception):
    """
    An AuthError is raised whenever the authentication failed.
    """
    def __init__(self, error: Dict[str, str], status_code: int):
        super().__init__()
        self.error = error
        self.status_code = status_code


@app.errorhandler(AuthError)
def handle_auth_error(ex: AuthError) -> Response:
    '''
    This error handler capture the error
    so it don't give 500 server error
    '''
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response
