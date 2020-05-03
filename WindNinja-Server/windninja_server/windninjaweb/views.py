"""
Routes and views for the flask application.
"""
from flask import render_template, Blueprint

main = Blueprint('main_blueprint', 'main')


@main.route("/")
@main.route("/home")
def home():
    """Renders the home page."""
    return render_template("index.html", title="Home")


@main.route("/contact")
def contact():
    """Renders the contact page."""
    return render_template("contact.html", title="Contact")


@main.route("/about")
def about():
    """Renders the about page."""
    return render_template("about.html", title="About")
