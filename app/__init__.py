"""
Package containing the Flask application.

This package contains the Flask application that serves as the backend for the
web application.

"""

from flask import Flask

from app import routes

# Create a Flask application object
app = Flask(__name__)


# Import the routes module


# Function to create the application
def create_app():
    """
    Create and configure the Flask application.

    This function creates and configures the Flask application by setting up
    the necessary configurations and registering the routes.

    Returns:
        Flask: The Flask application object.

    """
    # Configure the application
    app.config.from_object('config.DevelopmentConfig')

    # Register the routes
    app.register_blueprint(routes.routes)

    return app
