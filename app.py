from flask import Flask, jsonify, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event, DDL
from name_parser import get_names_from_file
import os
import uuid
import logging
import chardet

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'super-secret-key'

db = SQLAlchemy(app)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), unique=True)
    table_name = db.Column(db.String(100), unique=True)

def create_character_model(table_name):
    class Character(db.Model):
        __tablename__ = table_name
        __table_args__ = {'extend_existing': True}

        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), nullable=False)
        description = db.Column(db.Text)

    return Character

@app.route('/books/<int:book_id>/characters/<int:character_id>')
def character_page(book_id, character_id):
    try:
        book = Book.query.get_or_404(book_id)
        Character = create_character_model(book.table_name)
        character = db.session.query(Character).filter_by(id=character_id).first_or_404()
        return render_template('character.html', character=character, book=book)
    except Exception as e:
        logger.error(f"Error loading character page: {str(e)}")
        return "Internal Server Error", 500

@app.route('/')
def index():
    try:
        books = Book.query.all()
        return render_template('index.html', books=books)
    except Exception as e:
        logger.error(f"Error loading index: {str(e)}")
        return "Internal Server Error", 500

@app.route('/books/<int:book_id>')
def book_page(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('book.html', book=book)

@app.route('/books/<int:book_id>/characters', methods=['GET'])
def get_characters(book_id):
    try:
        book = Book.query.get_or_404(book_id)
        Character = create_character_model(book.table_name)
        characters = Character.query.all()
        return jsonify([{ 'id': c.id, 'name': c.name, 'description': c.description } for c in characters])
    except Exception as e:
        logger.error(f"Error getting characters: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
