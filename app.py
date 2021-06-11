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




app.config["UPLOAD_FOLDER "] = os.path.join('static' , 'images')

'''
    Database Related methods for creating te instance and tearing down the connection
'''
def get_db():
    if 'db' not in g:
        engine = create_engine("postgresql://postgres:linge531@localhost:5432/fire-fight-app")
        db=scoped_session(sessionmaker(bind=engine))
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
    login and logout required directives
'''
# def logout_required(view):
# 	@functools.wraps(view)
# 	def wrapped_view(**kwargs):
# 		if g.user:
# 			return redirect(url_for("profile"))
# 		return view(**kwargs)
# 	return wrapped_view

# def login_required(view):
# 	@functools.wraps(view)
# 	def wrapped_view(**kwargs):
# 		if g.user is None:
# 			return redirect(url_for("login"))
# 		return view(**kwargs)
# 	return wrapped_view


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

# @app.route('/home' , methods=["GET", "POST"])
# def register():

#     if request.method == 'POST':
#         c_name = request.form.get('c_name')
#         p_number = request.form.get('p_number')
#         img = request.files.get("img")
#         if  img:
#             file_path_name = os.path.join(current_app.config["UPLOAD_FOLDER "], c_name.strip() + "." + img.filename.rsplit(".", 1)[1])
#             img.save(file_path_name)
#             USERS = db.execute(
#                      "INSERT INTO USERS(c_name,p_number, profile_url) VALUES( :u_name,:p_number, :profile_url )" , {
#                          "u_name" :c_name.strip(),
#                          "p_number": p_number.strip(),
#                          "profile_url" : file_path_name.strip()
#                          }
#                      )
#             db.commit()
#             session['logged_in'] = True
#             session['c_name'] = c_name
#         else:
#             return render_template('index.html',message="Username Exists. Try Another.")
#         return render_template("home.html" ,errors=["Registered Successfully"])
#     return render_template('home.html')

# ######## LOGIN ##########
# @app.route('/home', methods=["GET", "POST"])
# def login():
#     if request.method == 'POST':
#         c_name = request.form.get('c_name')
#         p_number = request.form.get('p_number')
#         error = {"errors" : []} 
#         if c_name is None or len(c_name) == 0:
#             error["errors"].append("name is required")
#         elif p_number is None:
#             error["errors"].append("phone number is required")
#         user = db.execute("select * from USERS where c_name=:c_name and p_number=:p_number;",{'c_name':c_name,'p_number':p_number})
#         if user.rowcount == 0:
#             return render_template('index.html',message="Wrong Username")
#         session['logged_in'] = True
#         session['c_name'] = request.form['c_name']
#         return render_template('home.html')
#     return render_template('index.html')



@app.route('/auth/login', methods=[ "POST" , "GET"])
# @logout_required
def login():
    if request.method == "POST":
        username=request.form.get('u_name')
        password=request.form.get("password")
        error = {"errors" : []} 
        if username is None or len(username) == 0:
            error["errors"].append("username is required")
        elif password is None:
            error["errors"].append("password is required")
        elif len(password) < 6:
            error["errors"].append("password is to short")
        # try:
        db = get_db()
        if len(error["errors"]) == 0:
            user = db.execute("SELECT * FROM users where u_name = :uname;" , {"uname" : username}).fetchone()
            if not user:
                error["errors"].append("username or password not correct!")
                error["success"] = False
                return render_template("index.html" , errors = ["username or password not correct"])
            if check_password_hash(user["password"],password):
                session.clear()
                if user["profile_url"] is not None:
                    img_url = user['profile_url'].split('\\')[-1]
                    img_ext =img_url[img_url.index(".")+ 1 :]
                    session["profile_url"] = url_for("static" , filename = f"images/{user['u_name'] + '.' + img_ext}")
                else:
                    session["profile_url"] = url_for('static' ,filename = "images/default.png")
                session["username"] = user["u_name"]
                # session["b_date"] = user["b_date"]
                session["name"] = user["f_name"] + " " + user["l_name"]
                message = {}
                message["success"] = True
                message["message"] = "Successfully Logedin"
                return redirect(url_for("home"))
            error["success"] = False
            error["errors"].append("username or password incorrect!")
            return render_template("index.html" ,errors = error["errors"])
        else:
            error["success"] = False
            error["errors"].append("username or password incorrect!")
            return render_template("index.html" , errors=error["errors"])
    return redirect(url_for("index"))

@app.route('/auth/register',methods=["POST" , "GET"])
# @logout_required
def register():
    if request.method == "GET":
        return redirect(url_for("index"))
    f_name = request.form.get('f_name')
    l_name = request.form.get('l_name')
    username = request.form.get('u_name')
    password = request.form.get('password')
    password_confirmation = request.form.get('password_confirm')
    error = {"errors":[]}
    inputs = [f_name , l_name, username, password, password_confirmation]
    values = ["first name" , "last name", "username","password", "password_confirmation"]
    if None in inputs:
        for a in range(len(inputs)):
            if inputs[a] is None:
                error["errors"].append(f"{values[a]} can not be empty")
    else:
        # if not (b_date):
        #     error["errors"].append("birth date is required for the recommendation ML engine!")
        # if utils.num_there(f_name.strip()):
        #         error["errors"].append('Invalid character in first name')
        if len(f_name.strip()) == 0:
            error["errors"].append("name can not be empty")
        elif len(f_name.strip()) >20:
            error["errors"].append("first name can not this long!!")
        if len(l_name.strip()) == 0:
            error["errors"].append("name can not be empty")
        elif len(l_name.strip()) > 20:
            error["errors"].append("last name can not this long!!")

        # if utils.num_there(l_name.strip()):
        #     error["errors"].append('Invalid character in last name')
        if len(username.strip()) == 0:
            error["errors"].append("username can not be empty")
        elif not username.strip().isalnum():
            error["errors"].append("username can only contain numbers 0-9, underscore and alphabets Aa-Zz")
        if len(username.strip()) > 15:
            error["errors"].append("username cannot be longer than 15 characters")
        
        if len(password) < 6:
            error["errors"].append("password length too short")
        if  len(password_confirmation.strip()) < 6:
            error["errors"].append("password mismatch and confirmation length too short!!")
        elif password.strip() != password_confirmation.strip():
            error["errors"].append('password mismatch')
        if len(error["errors"]) == 0:
            # age = calc_age(b_date)
            db = get_db()
            res = db.execute("SELECT COUNT(*) FROM USERS WHERE u_name = :u_name" , {"u_name" : username}).fetchone()
            count =[x for x in res]
            if count[0] == 0:
                img = request.files.get("img")
                if  img:
                    file_path_name = os.path.join(current_app.config["UPLOAD_FOLDER "], username.strip() + "." + img.filename.rsplit(".", 1)[1])
                    img.save(file_path_name)
                    db.execute(
                        "INSERT INTO USERS(f_name,l_name,u_name,password,profile_url) VALUES( :f_name,:l_name,:u_name,:password,:profile_url )" , {
                            "f_name" :f_name.strip(),
                            "l_name": l_name.strip(),
                            "u_name" : username.strip(),
                            # "b_date" : b_date.strip(),
                            "password": generate_password_hash(password.strip()),
                            "profile_url" : file_path_name.strip()
                        }
                    )
                    db.commit()
                else:
                    db.execute(
                        "INSERT INTO USERS(f_name,l_name,u_name,password) VALUES( :f_name,:l_name,:u_name,:password)" , {
                            "f_name" :f_name.strip(),
                            "l_name": l_name.strip(),
                            "u_name" : username.strip(),
                            "password": generate_password_hash(password),
                            
                        }
                    )
                    db.commit()
                return render_template("home.html" ,errors=["registered Successfully"])
            else:
                error["errors"].append("Username already in use!")
                return render_template("home.html" ,errors=error["errors"])
            # except :
            #     error["errors"].append("Something went wrong in the server! ")
            #     error["success"] = False
            #     return jsonify(error)
        else:
            return render_template("home.html" ,errors=error["errors"])
    




    
if __name__ == "__main__":
    app.run(debug = True)
