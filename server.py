from flask import Flask, render_template, redirect, url_for, jsonify, flash, abort

# SQL Alchemy imports 
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Boolean, ForeignKey
from sqlalchemy.exc import NoResultFound

# Flask Login imports
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
import hashlib

# system imports for secret keys
import os

# Flask WTForms imports
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, PasswordField
from wtforms.validators import DataRequired, EqualTo, Email, Length
from flask_ckeditor import CKEditor, CKEditorField

# Datetime management imports
import datetime as dt
from dateutil import parser as date_parser


app = Flask(__name__)



### SQL Alchemy Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
### Database Tables Initialization
class Base(DeclarativeBase):
    pass
db = SQLAlchemy(model_class=Base)
db.init_app(app)
### Tables Creation
class Article(db.Model):
    __tablename__ = "articles"
    id: Mapped[int] =mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    subtitle: Mapped[str] = mapped_column(String, nullable=False)
    date: Mapped[str] = mapped_column(String, nullable=False)
    body: Mapped[str] = mapped_column(String, nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)

with app.app_context():
    db.create_all()
    # article3 = Article(title='Embrace the Fun: Exploring the Joy of Learning CSS and HTML',
    #                    subtitle=" Embarking on a Journey of Creativity and Expression: Unveiling the Joy of Learning HTML and CSS",
    #                    date = '4/13/2024',
    #                    body= "HTML serves as the skeleton of web pages, defining the structure and content. With its simple yet powerful tags, you can create headings, paragraphs, lists, images, and more. It's the blueprint upon which the web is built, providing the foundation for everything you see and interact with online.",
    #                    img_url= 'https://img.freepik.com/free-vector/programmers-concept-with-flat-design_23-2147852753.jpg?t=st=1712997608~exp=1713001208~hmac=0c830db79897932dd53924a29dd4ace0208deb0641d99c5824e5de67ffa9959e&w=826')
    # db.session.add(article3)
    # db.session.commit()



@app.route("/")
def homepage():
    articles = Article.query.all()
    return render_template("index.html", articles = articles)


@app.route('/articles')
def blogpage():
    return render_template("blog.html")

@app.route('/contact')
def contactpage():
    return render_template("contact.html")






if __name__ == "__main__":
    app.run(debug=True)