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

@app.route("/home" , methods=["GET", "POST"])
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
        else:
            return render_template('index.html',message="Username Exists. Try Another.")
        return render_template("home.html" ,errors=["registered Successfully"])
    return render_template('home.html')
    # if request.method == 'POST':
    #     model.save()
    # if request.method == "GET":
    #     return redirect(url_for("index"))
    # c_name = request.form.get('name')
    # p_number = request.form.get('p_number')
    # error = {"errors":[]}
    # inputs = [c_name ,p_number]
    # values = ["name" , "phone number"]
    # if None in inputs:
    #     for a in range(len(inputs)):
    #         if inputs[a] is None:
    #             error["errors"].append(f"{values[a]} can not be empty")
    # else:
    #     if len(c_name.strip()) == 0:
    #         error["errors"].append("name can not be empty") 
    #     if len(p_number.strip()) == 0:
    #         error["errors"].append("Phone number can not be empty")
    #     elif len(p_number.strip()) > 15:
    #         error["errors"].append("Phone number can be not this long!!")
    #     if len(error["errors"]) == 0:
    #         db = get_db()
    #         res = db.execute("SELECT COUNT(*) FROM USERS WHERE u_id = :u_id" , {"u_id" : user_id}).fetchone()
    #         count =[x for x in res]
    #         if count[0] == 0:
    #             img = request.files.get("img")
    #             if  img:
    #                 file_path_name = os.path.join(current_app.config["UPLOAD_FOLDER "], c_name.strip() + "." + img.filename.rsplit(".", 1)[1])
    #                 img.save(file_path_name)
    #                 db.execute(
    #                     "INSERT INTO USERS(c_name,p_number, profile_url) VALUES( :u_name,:p_number, :profile_url )" , {
    #                         "u_name" :c_name.strip(),
    #                         "p_number": p_name.strip(),
    #                         "profile_url" : file_path_name.strip()
    #                     }
    #                 )
    #                 db.commit()
    #             else:
    #                 error["errors"].append("You have to upload profile picture")
    #             return render_template("home.html" ,errors=["registered Successfully"])
    #         else:
    #             return render_template("index.html" ,errors=error["errors"])
    #     else:
    #         return render_template("index.html" ,errors=error["errors"])
    
