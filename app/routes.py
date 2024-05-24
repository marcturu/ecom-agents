"""
Routes for the Flask application.

This module contains the routes for the Flask application.

"""

from flask import Blueprint

# Create a blueprint object
routes = Blueprint('routes', __name__)


@routes.route('/')
@routes.route('/index')
def index():
    """
    A route for the home page of the application.

    This route returns a simple "Hello, World!" message.

    Returns:
        str: The message "Hello, World!".

    """
    return "Hello, World!"
