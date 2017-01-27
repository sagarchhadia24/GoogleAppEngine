from flask import Flask, render_template, request, redirect,send_from_directory
from flask import flash, request, session, abort, url_for
import os
import base64
from pymongo import MongoClient
import datetime
import time


app = Flask(__name__)

# DataBase Connectin:
client = MongoClient('mongodb://130.211.162.94:27017')
db = client['photo']
collection = db.image
fileLimit = 15
sizeLimit = 1000000
comment_limit = 100
print "DB Connected Successfully"


@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['GET','POST'])
def do_admin_login():

    if request.method == 'GET':
        return render_template('login.html')
    global username
    User_Name = request.form['username']
    Passoword = request.form['password']
    query =db.Users.find({"username" : User_Name})
    username = User_Name
    for pass1 in query:
        if pass1['password'] == Passoword:
            data = username
            return render_template('index.html',  message = data)
        else:
            data = "Invalid username/password"
            return render_template('login.html', message = data)

@app.route('/uploadimage', methods=['POST', 'GET'])
def uploadimage():
    if request.method == 'POST':
        try:
            out = """Successfully upload"""
            currentTime1 = datetime.datetime.now().time()
            currentTime = str(currentTime1)
            print  currentTime
            file_name = request.files['file_upload'].filename
            content = request.files['file_upload'].read()
            sizeOfFile = os.path.getsize(file_name)
            Comments = request.form['Comments']
            count = collection.find({"username": username}).count()
            if count < fileLimit and sizeOfFile < sizeLimit and len(Comments)<= comment_limit:
                out = "Successfully uploaded"
                encoded_string=base64.b64encode(content)
                postimage = {
                    "username" : username,
                    "IMGBase64Data" : encoded_string,
                    "filename" : file_name,
                    "Time": currentTime,
                    #"description" : "First Image"
                    "description" : Comments
                    }
                post_id = collection.insert(postimage)
                return render_template("index.html", output=out, message=username)
            else:
                out = "Limit Exceeded\Too Large File"
                return render_template("index.html", output=out, message=username)
        except:
            out = "Upload failed"
        return render_template("index.html", output=out, message=username)

@app.route('/getmypictures', methods=['POST', 'GET'])
def getmypictures():
    if request.method == 'POST':
        try:
            query = collection.find({"username": username})
            returnString = ""
            for post in query:
                IMGData = post['IMGBase64Data']
                comments = post['description']
                user_name = post['username']
                File_name = post['filename']
                Current_Time = post['Time']
                picdata = "data:image/jpeg;base64," + IMGData
                appendString = '</br> <form id="/upload" action="../deletepicture" method="post"><input type="hidden" name= "username" value="' + user_name + '"><input type="hidden" name= "filename" value="' + File_name + '"><input type="submit" value="Delete" id="submit_file"></form>'
                CommentString1 = '<form id="/upload" action="../updateComment" method="post"><input type="hidden" name= "username" value="' + user_name + '"><input type="hidden" name= "filename" value="' + File_name + '"><input type="text" value=" " name="updatecomment"><input type="submit" value="UpdateComment" id="submit_file"></form>'
                returnString = '<img src={}>'.format(
                    picdata) + '<br>Comments:' + comments + '<br>File Name:' + File_name + '<br>Date Time:' + Current_Time + '<br>UserName:' + user_name + appendString + returnString + CommentString1
            return returnString
        except:
            out = "Fail to list images"
            return render_template("index.html", output=out, message=username)

@app.route('/removemypictures', methods=['POST', 'GET'])
def removemypictures():
    if request.method == 'POST':
        try:
            query = collection.remove({"username": username})
            out = "Deleted All Pictures"
            return render_template("index.html", output=out, message=username)
        except:
            out = "Fail to delete images"
            return render_template("index.html", output=out, message=username)

@app.route('/getallpictures', methods=['POST', 'GET'])
def getallpictures():
    if request.method == 'POST':
        try:
            query = collection.find({})
            returnString = ""
            for post in query:
                IMGData = post['IMGBase64Data']
                comments = post['description']
                user_name = post['username']
                File_name = post['filename']
                picdata = "data:image/jpeg;base64," + IMGData
                appendString = '</br> <form id="/upload" action="../deletepicture" method="post"><input type="hidden" name= "username" value="' + user_name + '"><input type="hidden" name= "filename" value="' + File_name + '"><input type="submit" value="Delete" id="submit_file"></form></br>'
                #returnString = '<img src={}>'.format(picdata) + appendString + returnString
                returnString = '<img src={}>'.format(
                    picdata) + '<br>Comments:' + comments + '<br>File Name:' + File_name + '<br>UserName:' + user_name + appendString + returnString
            return returnString
        except:
            out = "Fail to list images"
            return render_template("index.html", output=out, message=username)

@app.route('/deletepicture', methods=['POST', 'GET'])
def deletepicture():
    User_Name = request.form['username']
    File_Name = request.form['filename']
    try:
        if User_Name == username:
            query = collection.remove({"username": User_Name, "filename": File_Name})
            out = 'Picture Deleted'
            return render_template("index.html", output=out, message=username)
        else:
            out = 'Cannot delete picture of other user'
            return render_template("index.html", output=out, message=username)
    except:
        out = "Fail to delete image"
        return render_template("index.html", output=out, message=username)

@app.route('/updateComment', methods=['POST', 'GET'])
def updateComment():
    try:
        User_Name = request.form['username']
        File_Name = request.form['filename']
        Comment_Update = request.form['updatecomment']
        query = collection.update({"username": User_Name, "filename": File_Name},{"$set": {"description": Comment_Update}})
        out = """Comment Successfully Updated"""
    except:
        out = "Failed to update comment"
    return render_template("index.html", output=out)

if __name__ == "__main__":
    app.run(debug=True)