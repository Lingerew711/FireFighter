import os
import re
import click
import random
import joblib
import functools
from flask_session import Session
from datetime import datetime, date
from flask.cli import with_appcontext
from sqlalchemy import create_engine,text
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash,generate_password_hash
from flask import flash, Flask, session, current_app, Blueprint,flash,g,redirect,render_template,request,session,url_for,json,send_file, jsonify,abort


app = Flask(__name__)

app.secret_key="1234567lingebookstore"

engine = create_engine("postgresql://postgres:linge531@localhost:5432/fire-fight-app")
db=scoped_session(sessionmaker(bind=engine))


app.config["UPLOAD_FOLDER "] = os.path.join('static' , 'images')

'''
    Database Related methods for creating te instance and tearing down the connection
'''
def get_db():
    if 'db' not in g:
        engine = create_engine(os.environ.get("DATABASE_URL"))
        db = scoped_session(sessionmaker(bind=engine))
        g.db = db
    return g.db

def close_db(e=None):
    db = g.pop('db',None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    with current_app.open_resource("schema.sql") as f:
        query = text(f.read().decode('utf8'))
        db.execute(query)
        db.commit()

'''
    A flask command for building the database 
'''

@click.command(name="build-db")
@with_appcontext
def execute_command():
    init_db()
    click.echo("database schema built!")

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(execute_command)




@app.route('/')
def index():
    return render_template("index.html")
@app.route("/home")
def home():
    return render_template('index.html')

######### REGISTER #############

@app.route('/home' , methods=["GET", "POST"])
def register():

    if request.method == 'POST':
        c_name = request.form.get('c_name')
        p_number = request.form.get('p_number')
        img = request.files.get("img")
        if  img:
            file_path_name = os.path.join(current_app.config["UPLOAD_FOLDER "], c_name.strip() + "." + img.filename.rsplit(".", 1)[1])
            img.save(file_path_name)
            USERS = db.execute(
                     "INSERT INTO USERS(c_name,p_number, profile_url) VALUES( :u_name,:p_number, :profile_url )" , {
                         "u_name" :c_name.strip(),
                         "p_number": p_number.strip(),
                         "profile_url" : file_path_name.strip()
                         }
                     )
            db.commit()
            session['logged_in'] = True
            session['c_name'] = c_name
        else:
            return render_template('index.html',message="Username Exists. Try Another.")
        return render_template("home.html" ,errors=["Registered Successfully"])
    return render_template('home.html')

######## LOGIN ##########
@app.route('/home', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        c_name = request.form.get('c_name')
        p_number = request.form.get('p_number')
        error = {"errors" : []} 
        if c_name is None or len(c_name) == 0:
            error["errors"].append("name is required")
        elif p_number is None:
            error["errors"].append("phone number is required")
        user = db.execute("select * from USERS where c_name=:c_name and p_number=:p_number;",{'c_name':c_name,'p_number':p_number})
        if user.rowcount == 0:
            return render_template('index.html',message="Wrong Username")
        session['logged_in'] = True
        session['c_name'] = request.form['c_name']
        return render_template('home.html')
    return render_template('index.html')

    
if __name__ == "__main__":
    app.run(debug = True)
