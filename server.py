from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)

@app.route("/")
def homepage():
    return render_template("index.html")


@app.route('/articles')
def blogpage():
    return render_template("blog.html")

@app.route('/contact')
def contactpage():
    return render_template("contact.html")







if __name__ == "__main__":
    app.run(debug=True)