from flask import Flask, render_template, request, session, logging, url_for,redirect,flash

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")
