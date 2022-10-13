# Objective: Save data from html form to Mysql using python
# Flask - is apython library/framework used to develop web applications
# Flask uses HTML/CSS/Python/SQL

import pymysql
from flask import *

# Build a Flask app
# __name__ gives an app a default name

app=Flask(__name__)

# routing concept
# to run a flask app you specify base URL http://127.0.0.1:5000/your route
@app.route('/home')
def home():
    return 'This is my good homepage.'

@app.route('/')
def index():
    return render_template('index.html')
# this route receives 5 values from the form, depart,destination,amount,date,time
@app.route('/book',methods=['POST','GET'])
def book():
    if request.method=='POST':  # this works if submit button was clicked
        # capture all form inputs
        depart=request.form['depart']
        destination=request.form['destination']
        date=request.form['date']
        time=request.form['time']
        amount=request.form['amount']

        connection=pymysql.connect(host='localhost',user='root',password='',database='Bendb')
        sql="insert into bookings(depart,destination,date,time,amount) VALUES(%s,%s,%s,%s,%s)"
        cursor=connection.cursor()
        cursor.execute(sql,(depart,destination,date,time,amount))
        connection.commit()
        return render_template('book.html',message="Booking Successful")
    else: # works if submit button is not clicked
        return render_template('book.html')
@app.route('/register',methods=['POST','GET'])
def register():
    if request.method=='POST':
        firstname=request.form['firstname']
        lastname=request.form['lastname']
        email=request.form['email']
        password1=request.form['password1']
        password2=request.form['password2']
        phone=request.form['phone']

        if len(password1) < 8:
            return render_template('register.html',message="Password must be 8 XTERS")
        elif password1 != password2:
            return render_template('register.html',message="Password do not match")
        else:
            connection=pymysql.connect(host='localhost',user='root',password='',database='Bendb')
            sql="insert into register(firstname,lastname,email,password,phone) VALUES(%s,%s,%s,%s,%s)"
            cursor=connection.cursor()
            cursor.execute(sql,(firstname,lastname,email,password2,phone))
            connection.commit()
            return render_template('register.html',message="Account Created Successful")
    else:
        return render_template('register.html')
@app.route('/login',methods =['POST','GET'])
def login():
    if request.method=='POST': # works if users post 
        email=request.form['email']
        password=request.form['password']
        connection=pymysql.connect(host='localhost',user='root',password='',database='Bendb')
        sql='select * from register where email =%s and password =%s'
        # create a cursor 
        cursor=connection.cursor()
        # execute sql replacing the placeholders with real values
        cursor.execute(sql,(email,password))

        # use cursor to check what sql found on the table, count rows returned

        if cursor.rowcount == 0:
            return render_template('login.html',message="Wrong Credentials,Try Again")
        elif cursor.rowcount==1:
            #return render_template('login.html',message="Welcome,Login Successful")
            return redirect('/book') # after success login,you route to /book
        else:
            return render_template('login.html',message="Something went wrong,Contact Admin")
    else:
        return render_template('login.html') # shows the form to the users to post/fill in details

# objective: Retrieve all bookings made in table, put them in html
@app.route('/view')
def view():
     connection=pymysql.connect(host='localhost',user='root',password='',database='Bendb')
     sql='select*from bookings order by date desc'
     cursor=connection.cursor()
     cursor.execute(sql)

     # check if there is any bookings on the table
     if cursor.rowcount==0:
         return render_template('view.html',message='No Bookings Found')
     else:
         rows=cursor.fetchall()
         return render_template('view.html',data=rows) # return rows as data


@app.route('/savedriver',methods=['POST','GET'])
def savedriver():
    if request.method=='POST': 
        driver_name=request.form['driver_name']
        driver_phone=request.form['driver_phone']
        idnumber=request.form['idnumber']
        car_assigned=request.form['car_assigned']
       
        connection=pymysql.connect(host='localhost',user='root',password='',database='Bendb')
        sql="insert into driver(driver_name,driver_phone,idnumber,car_assigned) VALUES(%s,%s,%s,%s)"
        cursor=connection.cursor()
        cursor.execute(sql,(driver_name,driver_phone,idnumber,car_assigned))
        connection.commit()
        return render_template('savedriver.html',message="Saving Successful")
    else:
        return render_template('savedriver.html')


@app.route('/retrieve')
def retrieve():
    connection=pymysql.connect(host='localhost',user='root',password='',database='Bendb')
    sql='select*from driver order by driver_id asc'
    cursor=connection.cursor()
    cursor.execute(sql)

    if cursor.rowcount ==0:
        return render_template('retrieve.html',message='No Driver Saved')
    else:
        rows=cursor.fetchall()
        return render_template('retrieve.html',data=rows) 


@app.route('/hire')
def hire():
    connection=pymysql.connect(host='localhost',user='root',password='',database='Bendb')
    sql="select*from hire where status ='Yes' "
    cursor=connection.cursor()
    cursor.execute(sql)

    if cursor.rowcount ==0:
        return render_template('hire.html',message='No Vehicles, Try Again Later.')
    else:
        rows=cursor.fetchall()
        return render_template('hire.html',data=rows) 

@app.route('/single/<reg_no>')
def single(reg_no):
    # this route receices the reg_no of the selected car
    # we do a sql to retrieve the details of the car
    connection=pymysql.connect(host='localhost',user='root',password='',database='Bendb')
    sql="select*from hire where reg_no= %s "
    cursor=connection.cursor()
    cursor.execute(sql,(reg_no)) #replace placeholder %s with reg_no

    # get the row holding the car details 
    row=cursor.fetchone()
     # we return the data holding one row to single.html
    return render_template('single.html',data=row)


# Mpesa route
import requests # to post requests to safaricom urls
import datetime # get current time needed for transaction purposes
import base64 # its encoding scheme to encode data to be sent to url
from requests.auth import HTTPBasicAuth # for developer authentification

@app.route('/mpesa', methods = ['POST','GET'])
def mpesa_payment():
        if request.method == 'POST':
            # receive the phone and the amount
            phone = str(request.form['phone'])
            amount = str(request.form['amount'])
            # GENERATING THE ACCESS TOKEN
            # you get them from daraja portal
            consumer_key = "GTWADFxIpUfDoNikNGqq1C3023evM6UH"
            consumer_secret = "amFbAoUByPV2rM5A"

            # we use the above credentials to authenticate to the

            api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials" #AUTH URL
            r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))

            # get an access token
            data = r.json()
            access_token = "Bearer" + ' ' + data['access_token']

            #  GETTING THE PASSWORD
            # get current time from your comp
            timestamp = datetime.datetime.today().strftime('%Y%m%d%H%M%S')
            # pass the paybill pass key
            passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
            business_short_code = "174379" # This is Daraja test paybill
            data = business_short_code + passkey + timestamp
            encoded = base64.b64encode(data.encode())
            password = encoded.decode('utf-8')
            print(password)


            # BODY OR PAYLOAD
            payload = {
                "BusinessShortCode": "174379",
                "Password": "{}".format(password),
                "Timestamp": "{}".format(timestamp),
                "TransactionType": "CustomerPayBillOnline",
                "Amount": amount,  # use 1 when testing
                "PartyA": phone,  # change to your number
                "PartyB": "174379",
                "PhoneNumber": phone,
                "CallBackURL": "https://modcom.co.ke/job/confirmation.php",
                "AccountReference": "account",
                "TransactionDesc": "account"
            }

            # POPULAING THE HTTP HEADER
            headers = {
                "Authorization": access_token,
                "Content-Type": "application/json"
            }

            url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest" #C2B URL
 
            response = requests.post(url, json=payload, headers=headers)
            print (response.text)
            return 'Please Complete Payment in Your Phone'
        else:
            return redirect('/hire')


app.run(debug=True)
