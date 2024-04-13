from flask import Flask, render_template, redirect, url_for, jsonify, flash, abort, request

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
from wtforms import StringField, SubmitField, EmailField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Email, Length
from flask_ckeditor import CKEditor, CKEditorField

# Datetime management imports
import datetime as dt
from dateutil import parser as date_parser

# SMTP imports
import smtplib


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


### Forms
app.secret_key = os.environ.get("FLASK_SECRET_KEY")
ckeditor = CKEditor(app)

class ContactForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(min=3, max=25, message="Name should be between %(min)d and %(max)d characters long")])
    email = EmailField("Email", validators=[DataRequired(), Email(message='Please Enter a Valid Email Address')])
    message = TextAreaField("Message", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Functions
# Sending email function

def send_mail(name, email, message):
    EMAIL = "bhamdanieh@gmail.com"
    PASS  = os.environ.get("SMTP_PASS")
    # PASS  = "ykraneoczgiuhldg"
    smtp_server = "smtp.gmail.com"
    print(PASS)

    with smtplib.SMTP(smtp_server) as server:
            server.starttls()
            server.login(EMAIL, PASS)
            server.sendmail(from_addr= EMAIL,
                        to_addrs=EMAIL,
                        msg=f"Subject:Portfolio New Message\n\nName:{name}\nEmail: {email}\nMessage:{message}")



@app.route("/")
def homepage():
    articles = Article.query.all()
    return render_template("index.html", articles = articles)


@app.route('/articles')
def blogpage():
    articles = Article.query.all()
    return render_template("blog.html", articles = articles)

@app.route('/contact', methods=['GET', 'POST'])
def contactpage():
    contact_form = ContactForm()
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        send_mail(name=name, email=email, message=message)
        return jsonify({"success": True})

    return render_template("contact.html", contact_form=contact_form)

@app.route('/articles/<article_id>')
def single_article_page(article_id):
    recent_articles = Article.query.order_by(Article.id.desc()).limit(6).all()
    article = Article.query.filter(Article.id == article_id).one()
    return render_template("article.html", article=article, recent_articles=recent_articles)





if __name__ == "__main__":
    app.run(debug=True)