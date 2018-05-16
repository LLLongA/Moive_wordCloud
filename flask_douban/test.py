#coding:utf-8

from flask import Flask, render_template,request,redirect,url_for
import Spider1
import time
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('wel.html')

@app.route('/getPicture/', methods=['GET', 'POST'])
def getPicture():
    name = request.args.get("name")
    print("电影名称:", name)
    Spider1.save_picture(name)
    return name

if __name__ == '__main__':
    app.run(debug = True, threaded = True)