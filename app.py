import logging
import re
from flask import Flask , render_template, request, url_for, redirect,flash,session
logging.basicConfig(filename='validation_errors.log')
logger=logging.getLogger
from bson.objectid import ObjectId
from pymongo import MongoClient



app=Flask(__name__)
app.secret_key="secretkey"

client=MongoClient("mongodb://localhost:27017")



db = client['ott-database']  #  create database


userc = db['ott-collection']    # creating the collection
adminc = db['admin-collection'] 
videoc=db['videos_collection']

name_pattern = r'^[A-Za-z\s]{2,50}$'
email_pattern = r'^[\w\.-]+@[\w\.-]+$'
password_pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$'
card_number_pattern = r'^\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}$'
expiry_date_pattern = r'^(0[1-9]|1[0-2])/(2[0-9])$'
cvc_pattern = r'^\d{3,4}$'

@app.route('/')
def home():
    return render_template('home.html')

@app.route("/register", methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        name = request.form['fullname']
        email = request.form['email']
        pw = request.form['password']
        card_name = request.form['cardName']
        card_number = request.form['cardNumber']
        expiry_date = request.form['expiryDate']
        cvc = request.form['cvc']

        # Validate the data using regex
        if not re.match(name_pattern, name):
            # Log the error
            logging.error(f"Invalid name: {name}")
            # Handle invalid name
        elif not re.match(email_pattern, email):
            # Log the error
            logging.error(f"Invalid email: {email}")
            # Handle invalid email
        elif not re.match(password_pattern, pw):
            # Log the error
            logging.error("Invalid password")
            # Handle invalid password
        elif not re.match(card_number_pattern, card_number):
            # Log the error
            logging.error(f"Invalid card number: {card_number}")
            # Handle invalid card number
        elif not re.match(expiry_date_pattern, expiry_date):
            # Log the error
            logging.error(f"Invalid expiry date: {expiry_date}")
            # Handle invalid expiry date
        elif not re.match(cvc_pattern, cvc):
            # Log the error
            logging.error(f"Invalid CVC: {cvc}")
            # Handle invalid CVC
        else:
            # All data is valid, you can proceed with registration
            data = {
                    'name': name,
                    'email': email,
                    'password': pw,
                    'card_name': card_name,
                    'card_number': card_number,
                    'expiry date': expiry_date,
                    'cvc': cvc
                }
                # Perform registration logic here
            return render_template('login.html')
    else:
        return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # check if the user exists in the database and the password matches
        admin = adminc.find_one({'email': email, 'password': password}) 
        user = userc.find_one({'email': email, 'password': password})

        
        if admin:
            # redirect to videos.html if credentials are correct
            session['email']=email
            return redirect('/addvideo')
        
        elif user:
            return redirect('/videos')

        else:
            # throw an error if credentials are incorrect
            error = 'Incorrect email or password'
            app.logger.warning(error)
            return render_template('login.html', error=error)
            
    
    # if request.method is GET, return the login form
    return render_template('login.html')



@app.route('/videos', methods=['GET','POST'])
def videos():
    videos = videoc.find({})
    return render_template('videos.html', videos=videos)

@app.route('/search', methods=['GET','POST'])
def search():
    search_text = request.form['query']
    search_result = db.videos_collection.find_one({'title': search_text})
    if search_result:
        return render_template('results.html',video=search_result)
    else:
        flash("not found.")
        return "No results found."


@app.route('/addvideo', methods=['GET', 'POST'])
def addvideos():
    if request.method == 'POST':
        link = request.form.get('link')
        title = request.form.get('title')

        

        db.videos_collection.insert_one({'link': link, 'title': title})
        return redirect(url_for('addvideo'))
    return render_template('addvideo.html')

if __name__ == '__main__':
    app.run(debug=True)
