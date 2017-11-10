from flask import Flask, request, redirect, render_template, session, flash
from twilio.twiml.messaging_response import MessagingResponse
import random
from twilio.rest import Client
import os
import schedule
import time
from datetime import datetime
from pytz import timezone
from model import connect_to_db, db, User, Cat
# Your Account SID from twilio.com/console
account_sid = os.environ.get("account_sid")
# Your Auth Token from twilio.com/console
auth_token = os.environ.get("auth_token")
client = Client(account_sid, auth_token)
phone_number = os.environ.get("phone_number")
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")
############################################################################

# CAT_INFO = {}

# CAT_INFO['dinner_time'] = "8:57"

@app.route("/")
def main():
    """Render main page"""

    return render_template("home.html")

@app.route("/login", methods=["GET"])
def attempt_login():
    """Show login page"""

    return render_template("home.html")


@app.route("/login", methods=["POST"])
def login():
    """Attempt to log the user in"""

    email = request.form.get("email")
    password = request.form.get("password")

    existing_email = User.query.filter_by(email=email).first()

    if existing_email is not None and existing_email.password == password:
        # add user to session
        session["user_id"] = existing_email.user_id

        flash("Successfully logged in!")
        return render_template("homepage.html")

    elif existing_email is None:
        flash("Incorrect email.")
        return redirect('/')
    else:
        flash("Incorrect password.")
        return redirect('/')

@app.route("/register", methods=["GET"])
def register():
    """Show registration form"""

    return render_template("register.html")

@app.route("/register", methods=["POST"])
def register_process():
    """Get information from registration form."""

    email = request.form.get("email")
    password = request.form.get("password")

    existing_email = User.query.filter_by(email=email).first()

    # check if the username is in use
    if existing_email is None:
        #check if the email is in use
        new_user = User(email=email, password=password)

        db.session.add(new_user)
        db.session.commit()

        flash("Successfully registered " + email + "!")
        return redirect("/")

    else:
        flash("Username or email already in use")
        # TODO probably handle this in AJAX on the form and be more specific
        # as to whether it was the username or email that failed

    return redirect("/")


@app.route("/sms", methods=['POST'])
def incoming_sms():
    """Send a dynamic reply to an incoming text message"""
    # Get the message the user sent our Twilio number
    body = request.values.get('Body', None)

    name = Cat.query.filter_by()

    toy1 = 'Can we play with my ' + CAT_INFO['cat_toy'] + '?'
    toy2 = "I think it's time for the " + CAT_INFO['cat_toy2'] + "!!!"
    snack = "I'm hungry!! I want " + CAT_INFO['cat_snack'] + "!"
    activity1 = "Whachu up to? I'm busy " + CAT_INFO['cat_activity'] + "..."
    activity2 = "Me? I'm just " + CAT_INFO['cat_activity2'] + "..."

    cat_responses = [toy1, toy2, snack, activity1, activity2]
    # Start our TwiML response
    resp = MessagingResponse()

    # Determine the right reply for this message
    if body == 'hey' or body == 'Hey':
        resp.message("Hi! Where's my " + CAT_INFO['cat_snack'] + "?!")
    elif body == 'bye' or body == 'Bye':
        resp.message("Bye? I'm just going to text you again later.")
    else:
        reply = random.choice(cat_responses)
        resp.message(reply)

    return str(resp)


@app.route("/welcome", methods=['GET', 'POST'])
def welcome():
    """Welcome to the user to Cat Texts"""

    # CAT_INFO['cat_name'] = request.args.get('cat-name')
    name = request.args.get('cat-name')
    # CAT_INFO['dinner_time'] = request.args.get('dinner-time')
    dinner_time = request.args.get('dinner-time')
    # CAT_INFO['cat_snack'] = request.args.get('cat-snack')
    snack = request.args.get('cat-snack')
    # CAT_INFO['cat_activity'] = request.args.get('cat-activity')
    activity1 = request.args.get('cat-activity')
    # CAT_INFO['cat_activity2'] = request.args.get('cat-activity2')
    activity2 = request.args.get('cat-activity2')
    # CAT_INFO['cat_toy'] = request.args.get('cat-toy')
    toy1 = request.args.get('cat-toy')
    # CAT_INFO['cat_toy2'] = request.args.get('cat-toy2')
    toy2 = request.args.get('cat-toy2')

    new_cat = Cat(name=name, dinner_time=dinner_time, snack=snack,
                  activity1=activity1, activity2=activity2, 
                  toy1=toy1, toy2=toy2)

    db.session.add(new_cat)
    db.session.commit()

    message = client.messages.create(
    to=phone_number, 
    from_="+14138486585",
    # media_url="https://static.pexels.com/photos/62321/kitten-cat-fluffy-cat-cute-62321.jpeg",
    body="Hi, it's " + name + ". I like " + snack + "! Feed me at " + dinner_time + "!")

    print(message.sid)

    return render_template("thanks.html")


def daily_text():

    message = client.messages.create(
    to=phone_number, 
    from_="+14138486585",
    # media_url="https://static.pexels.com/photos/62321/kitten-cat-fluffy-cat-cute-62321.jpeg",
    body="Hi, " + CAT_INFO['cat_name'] + " here. I'm pretty sure it's dinner time!")
    # body = "hi I'm working")

    print(message.sid)

# @app.route("/thanks")
# def schedule_text():
#     """This is a really janky workaround that requires the page being open forever"""

#     print "i'm here"
#     schedule.every().day.at(str(CAT_INFO['dinner_time'])).do(daily_text)
    # just testing functionality, comment out above line
    # schedule.every(5).seconds.do(daily_text) 

    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)

    # return render_template("thanks.html")

if __name__ == "__main__":

    from flask import Flask

    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)
    print "Connected to DB."

    app.run(port=5000, host='0.0.0.0')

    # runs every day at dinner time
    # schedule.every().day.at(str(CAT_INFO['dinner_time'])).do(daily_text)
    # # just testing functionality, comment out above line
    # # schedule.every(5).seconds.do(daily_text) 

    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)

    # having trouble here - I can only get the scheduled job to work if I put 
    # app.run at the end, however the CAT_INFO dictionary has no info in it yet
    # obviously, because the user hasn't entered it yet. 

    # Current time in UTC
    now_utc = datetime.now(timezone('UTC'))
    # Convert to US/Pacific time zone
    now_pacific = now_utc.astimezone(timezone('US/Pacific'))

