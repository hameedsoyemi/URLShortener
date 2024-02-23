from flask import Flask, redirect, request, jsonify, render_template, json
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import URLSafeTimedSerializer
import validators

#CODE EXPLANATION

# First, we import the necessary modules:

# Flask is the web framework we'll be using to build the URL shortener.
# request is a module that provides access to the incoming request data.
# jsonify is a function that returns a JSON response.
# SQLAlchemy is a database toolkit and Object-Relational Mapping (ORM) system for Python.
# URLSafeTimedSerializer is a module that provides a way to serialize and deserialize data in a URL-safe way.
# validators is a module that provides a way to validate URLs.


# Next, we create a Flask app and configure it to use SQLite as the database. 

# We also define a ShortURL model that represents a shortened URL. 
# The ShortURL model has three attributes: id, url, and short_url. 
# The id attribute is an auto-incrementing integer that serves as the primary key. 
# The url attribute is the original URL that we want to shorten. 
# The short_url attribute is a short string that we'll use to represent the original URL.

# We define two routes:
# /shorten: This route handles POST requests that contain a JSON object with a single attribute, url. 
# It validates the URL using the validators module, creates a new ShortURL object, and saves it to the database.
# It then returns a JSON object containing the short URL.

# <short_url>: This route handles GET requests that contain a short URL. 
# It queries the database for a ShortURL object that matches the short URL, and if it finds one, it redirects the user to the original URL. 
# If it doesn't find a matching ShortURL object, it returns a JSON object containing an error message.

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shortener2.db'
db = SQLAlchemy(app)

class ShortURL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(200))
    short_url = db.Column(db.String(8), unique=True)

    def __init__(self, url):
        self.url = url
        self.short_url = self.generate_short_url()

    def generate_short_url(self):
        serializer = URLSafeTimedSerializer('my_secret_key')
        return serializer.dumps(self.url, salt='shorturl')

@app.route('/shorten', methods=['POST'])
def shorten():
    url = request.json['url']
    if not validators.url(url):
        return jsonify({'error': 'Invalid URL'}), 400
    short_url = ShortURL(url)
    db.session.add(short_url)
    db.session.commit()

    return  {"data" : f'shortUrl: http://localhost:5000/{short_url.short_url}'}

@app.route('/', methods=['GET'])
def showHomePage():
    return render_template("index.html")


@app.route('/<short_url>')
def redirect_to_short_url(short_url):
    short_url_obj = ShortURL.query.filter_by(short_url=short_url).first()
    if short_url_obj is None:
        return jsonify({'error': 'URL not found'}), 404
    return redirect(short_url_obj.url)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.run(debug=True)