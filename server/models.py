from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from sqlalchemy import event
import re

db = SQLAlchemy()

class Author(db.Model):
    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    phone_number = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    @validates('phone_number')
    def validate_phone_number(self, key, phone_number):
        if phone_number:
            digits = re.sub(r'\D', '', str(phone_number))
            if len(digits) != 10:
                raise ValueError("Phone number must be exactly 10 digits.")
        return phone_number

    def __repr__(self):
        return f'<Author {self.name}>'


# Use events for name validation (passes the tricky uniqueness test reliably)
@event.listens_for(Author, 'before_insert')
@event.listens_for(Author, 'before_update')
def validate_author_name(mapper, connection, target):
    if not target.name:
        raise ValueError("Name field is required.")

    query = """
        SELECT id FROM authors 
        WHERE name = :name 
        AND (:id IS NULL OR id != :id)
        LIMIT 1
    """
    result = connection.execute(
        db.text(query),
        {"name": target.name, "id": target.id}
    ).fetchone()

    if result:
        raise ValueError("Name must be unique.")


class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.String, nullable=False)
    summary = db.Column(db.String)
    category = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    @validates('content')
    def validate_content(self, key, content):
        if len(content) < 250:
            raise ValueError("Post content must be at least 250 characters long.")
        return content

    @validates('summary')
    def validate_summary(self, key, summary):
        if summary and len(summary) > 250:
            raise ValueError("Post summary must be a maximum of 250 characters.")
        return summary

    @validates('category')
    def validate_category(self, key, category):
        if category and category not in ['Fiction', 'Non-Fiction']:
            raise ValueError("Category must be either 'Fiction' or 'Non-Fiction'.")
        return category

    @validates('title')
    def validate_title(self, key, title):
        clickbait = ["Won't Believe", "Secret", "Top", "Guess"]
        if not any(phrase in title for phrase in clickbait):
            raise ValueError(
                "Title must contain one of: 'Won't Believe', 'Secret', 'Top', 'Guess'"
            )
        return title

    def __repr__(self):
        return f'<Post {self.title}>'