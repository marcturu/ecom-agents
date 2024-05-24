"""
Run the Flask application in debug mode.

This script is responsible for running the Flask application in debug mode.
It imports the Flask application from the `app` module and runs it using the
`app.run()` method.

Usage:
    python run.py

"""
from app import app

if __name__ == '__main__':
    app.run(debug=True)
