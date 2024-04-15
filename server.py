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
from wtforms import StringField, SubmitField, EmailField, PasswordField, TextAreaField, FileField
from wtforms.validators import DataRequired, EqualTo, Email, Length
from flask_ckeditor import CKEditor, CKEditorField

# Datetime management imports
import datetime as dt
from dateutil import parser as date_parser

# SMTP imports
import smtplib

from werkzeug.utils import secure_filename

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

class Project(db.Model):
    __tablename__ = "projects"
    id: Mapped[int] =mapped_column(Integer, primary_key=True)
    excerpt: Mapped[str] = mapped_column(String, nullable=False)
    img_url: Mapped[str] = mapped_column(String, nullable=False)
    web_url: Mapped[str] = mapped_column(String, nullable=False)

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


class CreatePostForm(FlaskForm):
    title    = StringField("Article Title", validators=[DataRequired()])
    subtitle = StringField("Article Subtitle", validators=[DataRequired()])
    img_url    = FileField("Article Featured Image", validators=[DataRequired()])
    img_url_edit    = FileField("Article Featured Image")
    body     = CKEditorField("Body", validators=[DataRequired()])
    submit   = SubmitField("Submit")
    submit_edit = SubmitField("Submit")


class AddProjectForm(FlaskForm):
    excerpt     = StringField("Project Excerpt/Description", validators=[DataRequired()])
    image       = FileField("Project Featured Image", validators=[DataRequired()])
    img_url_edit    = FileField("Article Featured Image")
    web_url     = StringField("Project URL", validators=[DataRequired()])
    submit      = SubmitField("Submit")



# Functions
# Sending email function

def send_mail(name, email, message):
    EMAIL = "bhamdanieh@gmail.com"
    PASS  = os.environ.get("SMTP_PASS")
    smtp_server = "smtp.gmail.com"

    with smtplib.SMTP(smtp_server) as server:
            server.starttls()
            server.login(EMAIL, PASS)
            server.sendmail(from_addr= EMAIL,
                        to_addrs=EMAIL,
                        msg=f"Subject:Portfolio New Message\n\nName:{name}\nEmail: {email}\nMessage:{message}")



@app.route("/")
def homepage():
    articles = Article.query.all()
    projects = Project.query.all()
    return render_template("index.html", articles = articles, projects=projects)


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

@app.route('/add-article', methods=['GET', 'POST'])
def add_article_page():
    add_article_form = CreatePostForm()
    today_date = dt.datetime.today().strftime('%B %d, %Y')

    if add_article_form.validate_on_submit():
        if request.method == 'POST':
            image_file = request.files['img_url']
            filename = secure_filename(image_file.filename)
            path = f'static/images/uploads/{filename}'
            image_file.save(path)

            
            title = request.form['title']
            subtitle = request.form['subtitle']
            body = add_article_form.body.data
        
            new_article = Article(title=title, subtitle=subtitle, img_url=path, body=body, date=today_date)
            db.session.add(new_article)
            db.session.commit()
        
            flash("Article Added Successfully", "post_added")
            return redirect(url_for('add_article_page'))

    return render_template("add-article.html", form=add_article_form)


@app.route('/edit-article', methods=['GET', 'POST'])
def edit_article_page():
    articles = Article.query.all()
    return render_template("edit-article.html", articles = articles)


@app.route('/edit-article-form/<article_id>', methods=['GET', 'POST'])
def edit_article_form_page(article_id):
    article = Article.query.filter(Article.id == article_id).one()
    edit_article_form = CreatePostForm(title=article.title, img_url=article.img_url,subtitle=article.subtitle, body=article.body) 

    if edit_article_form.validate_on_submit():
        if request.method == 'POST':

            image_file = request.files['img_url_edit']
            if image_file:
                filename = secure_filename(image_file.filename)
                path = f'static/images/uploads/{filename}'
                image_file.save(path)
                article.img_url = path
            else:
                article.img_url = article.img_url


            article.title = request.form['title']
            article.subtitle = request.form['subtitle']
            article.body = request.form['body']
            article.date = article.date
            db.session.commit()
            flash("Article Edited Successfully", "post_edited")
            return redirect(url_for('edit_article_form_page', article_id=article.id))
        
    return render_template('edit-article-form.html', form=edit_article_form, article=article, article_id=article.id)


@app.route('/delete-article/<article_id>', methods=['GET', 'POST'])
def delete_article(article_id):
    article = Article.query.filter(Article.id == article_id).one()

    if article:
        db.session.delete(article)
        db.session.commit()
        flash("Article Deleted Successfully", "post_deleted")
        return redirect(url_for('edit_article_page'))
    
    return jsonify(error= 'Article Not Found'), 404
        

@app.route('/add-project', methods=['GET', 'POST'])
def add_project_page():
    form = AddProjectForm()

    if form.validate_on_submit():
        if request.method == "POST":
            image_file = request.files['image']
            filename = secure_filename(image_file.filename)
            path = f'static/images/uploads/{filename}'
            image_file.save(path)
            print(f"File saved as {filename}")
            
            
            new_project = Project(excerpt=form.excerpt.data, img_url=path, web_url=form.web_url.data)
            db.session.add(new_project)
            db.session.commit()

            flash("Project Added Successfully", "project_added")
            return redirect(url_for('add_project_page'))
        
    return render_template('add_project.html', form=form)

@app.route('/edit-project')
def edit_project_page():
    projects = Project.query.all()
    return render_template('edit_project.html', projects=projects)

@app.route('/delete-project/<project_id>', methods=['GET', 'POST'])
def delete_project(project_id):
    project = Project.query.filter(Project.id == project_id).one()

    if project:
        db.session.delete(project)
        db.session.commit()
        flash("Project Deleted Successfully", "project_deleted")
        return redirect(url_for('edit_project_page'))
    
    return jsonify(error= 'Project Not Found'), 404

@app.route('/edit-project-form/<project_id>', methods=['GET', 'POST'])
def edit_project_form_page(project_id):
    project = Project.query.filter(Project.id == project_id).one()
    edit_project_form = AddProjectForm(excerpt=project.excerpt, image=project.img_url, web_url=project.web_url) 

    if edit_project_form.validate_on_submit():
        if request.method == 'POST':

            image_file = request.files['img_url_edit']
            if image_file:
                filename = secure_filename(image_file.filename)
                path = f'static/images/uploads/{filename}'
                image_file.save(path)
                project.img_url = path
            else:
                project.img_url = project.img_url


            project.excerpt = request.form['excerpt']
            project.web_url = request.form['web_url']

            db.session.commit()
            flash("Project Edited Successfully", "project_edited")
            return redirect(url_for('edit_project_form_page', project_id=project.id))
        
    return render_template('edit_project_form.html', form=edit_project_form, project=project, project_id=project.id)

if __name__ == "__main__":
    app.run(debug=True, port=5000)