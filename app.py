from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS

import os

app = Flask(__name__) # Instance of Flask
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "app.sqlite") # Specifying where the database is going
db = SQLAlchemy(app) # Instance of SQLAlchemy with Flask passed in
ma = Marshmallow(app) # Instance of Marshmallow with Flask passed in
CORS(app)


# Make a class for each table you'll have
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False, unique=True)
    author = db.Column(db.String, nullable=False)
    review = db.Column(db.String)

    def __init__(self, title, author, review):
        self.title = title
        self.author = author
        self.review = review


# Create Marshmallow Schema
class BookSchema(ma.Schema):
    class Meta:
        fields = ("id", "title", "author", "review")

# Create two instances of your Marshmallow Schema
book_schema = BookSchema()
multiple_book_schema = BookSchema(many=True)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password


class UserSchema(ma.Schema):
    class Meta:
        fields = ("id", "username")


user_schema = UserSchema()
multiple_user_schema = UserSchema(many=True)


# Endpoints

# Post endpoint to create data
@app.route("/book/add", methods=["POST"])
def add_book():
    if request.content_type != "application/json":
        return jsonify("Error: Data must be sent as JSON")

    post_data = request.get_json()
    title = post_data.get("title")
    author = post_data.get("author")
    review = post_data.get("review")

    if title == None:
        return jsonify("Error: Data must have a 'title' key")
    if author == None:
        return jsonify("Error: Data must have an 'author' key")

    new_record = Book(title, author, review)
    db.session.add(new_record)
    db.session.commit()

    return jsonify("Book added successfully")


@app.route("/book/get", methods=["GET"])
def get_books():
    records = db.session.query(Book).all()
    return jsonify(multiple_book_schema.dump(records))



@app.route("/book/get/id/<id>", methods=["GET"])
def get_book_by_id(id):
    record = db.session.query(Book).filter(Book.id == id).first()
    return jsonify(book_schema.dump(record))


@app.route("/book/get/title/<title>", methods=["GET"])
def get_book_by_title(title):
    record = db.session.query(Book).filter(Book.title == title).first()
    return jsonify(book_schema.dump(record))


@app.route("/book/get/author/<author>", methods=["GET"])
def get_books_by_author(author):
    records = db.session.query(Book).filter(Book.author == author).all()
    return jsonify(multiple_book_schema.dump(records))


@app.route("/book/get/title-author/<title>/<author>", methods=["GET"])
def get_book_by_title_and_author(title, author):
    record = db.session.query(Book).filter(Book.title == title).filter(Book.author == author)
    return jsonify(book_schema.dump(record))


@app.route("/book/update/<id>", methods=["PUT"])
def update_book_by_id(id):
    if request.content_type != "application/json":
        return jsonify("Error: Data must be sent as JSON")

    put_data = request.get_json()
    title = put_data.get("title")
    author = put_data.get("author")
    review = put_data.get("review")

    record = db.session.query(Book).filter(Book.id == id).first()

    if title != None:
        record.title = title
    if author != None:
        record.author = author
    if review != None:
        record.review = review

    db.session.commit()

    return jsonify("Book updated successfully")


@app.route("/book/delete/<id>", methods=["DELETE"])
def delete_book_by_id(id):
    record = db.session.query(Book).filter(Book.id == id).first()
    db.session.delete(record)
    db.session.commit()
    return jsonify("Book was successfully deleted")


@app.route("/user/add", methods=["POST"])
def add_user():
    if request.content_type != "application/json":
        return jsonify("Error: Data must be sent as JSON")
    
    post_data = request.get_json()
    username = post_data.get("username")
    password = post_data.get("password")

    new_record = User(username, password)
    db.session.add(new_record)
    db.session.commit()

    return jsonify("Data added successfully")


@app.route("/user/get", methods=["GET"])
def get_users():
    records = db.session.query(User).all()
    return jsonify(multiple_user_schema.dump(records))


# Start up your server
if __name__ == "__main__":
    app.run(debug=True)