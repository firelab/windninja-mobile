"""
Routes and views for the flask application.
"""
from flask import render_template

from windninjaweb.app import app


@app.route("/")
@app.route("/home")
def home():
    """Renders the home page."""
    return render_template("index.html", title="Home")


@app.route("/contact")
def contact():
    """Renders the contact page."""
    return render_template("contact.html", title="Contact")


@app.route("/about")
def about():
    """Renders the about page."""
    return render_template("about.html", title="About")
