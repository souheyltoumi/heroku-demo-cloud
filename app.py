from flask import Flask,request,jsonify,redirect
from flask_pymongo import PyMongo
import hashlib, binascii, os
import json
from flask_cors import CORS

import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sklearn 
import pandas as pd
import numpy as np
import random
import string
import pickle
app=Flask(__name__)

app.config["MONGO_DBNAME"]="users"
app.config["MONGO_URI"]="mongodb://******:*******@souheil-shard-00-00-kqdwl.mongodb.net:27017,souheil-shard-00-01-kqdwl.mongodb.net:27017,souheil-shard-00-02-kqdwl.mongodb.net:27017/test?ssl=true&replicaSet=souheil-shard-0&authSource=admin&retryWrites=true&w=majority"
mongo=PyMongo(app)
CORS(app)

def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

def hash_password(password):
    """Hash a password for storing."""
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), 
                                salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')

def verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by user"""
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512', 
                                  provided_password.encode('utf-8'), 
                                  salt.encode('ascii'), 
                                  100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password
def sendVerficationMail(receiver_email,password2):
    sender_email = "******************@gmail.com"
    password ="****************"

    message = MIMEMultipart("alternative")
    message["Subject"] = "Register Password"
    message["From"] = sender_email
    message["To"] = receiver_email

    text = """\
    Hi,
    How are you?
    Real Python has many great tutorials:
    www.realpython.com"""
    html = """\
    <html>
    <body>
        <p>Hi,<br>
         How are you hAPPY user?<br>
         <a href="http://www.realpython.com">Real Python</a> 
        here is your Password :"""+password2+"""
     </p>
    </body>
    </html>
    """

    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    message.attach(part1)
    message.attach(part2)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )
@app.route('/viewUsers', methods=['GET']) 
def get_bucketList():
	bucketList = mongo.db.users
	users = []
	goal = bucketList.find()
	for j in goal:
		j.pop('_id')
		users.append(j)
	return jsonify(users)	
@app.route("/regiser", methods=['POST'])  
def register ():  
    bucketList = mongo.db.users
    username=request.values.get("user")  
    password1=randomString() 
   # password=hash_password(password1)
    cin=request.values.get("cin")  
    email=request.values.get("email")  
    bucketList.insert({ "username":username, "password":password1, "cin":cin, "email":email})  
    sendVerficationMail(email,password1)
    return redirect("/viewUsers")  
@app.route("/login", methods=['POST'])  
def login ():  
    bucketList = mongo.db.users
    username=request.values.get("user")
    password=request.values.get("pass")
    user=bucketList.find({"username":username})
    if user.count() ==0:
        return "not found"
    else:
        users=[]
        for j in user:
            j.pop('_id')
            if (j['password']==password):
                users.append(j)
                return jsonify(users)
            else:
                return "Wrong Password"

@app.route("/predict", methods=['POST'])
def predict():
    print("I was here 1")
    if request.method == 'POST':
        print(request.values.get('NewYork'))
        NewYork = request.values.get('NewYork')
        California =request.values.get('California')
        Florida = request.values.get('Florida')
        if NewYork=="1":
            NewYork = np.float64(1)
            California =np.float64(0)
        elif California=="1":
            NewYork = np.float64(0)
            California =np.float64(1)   
        elif Florida=="1":
            NewYork = np.float64(0)
            California =np.float64(0)                 
    
        
        RnD_Spend = np.float64(request.values.get('RnD_Spend'))
        Admin_Spend = np.float64(request.values.get('Admin_Spend'))
        Market_Spend = np.float64(request.values.get('Market_Spend'))
        pred_args = [NewYork, California, RnD_Spend, Admin_Spend, Market_Spend]


        pred_args_arr = np.array(pred_args)
        pred_args_arr = pred_args_arr.reshape(1, -1)
      
        mul_reg = pickle.load(open('startups_model.sav', 'rb'))
        model_prediction = mul_reg.predict(pred_args_arr)
        model_prediction = round(float(model_prediction), 2)
 
    return str(model_prediction)
                
if __name__ =='__main__':
    app.run(debug=True)
