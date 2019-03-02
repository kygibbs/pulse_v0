#Python libraries that we need to import for our bot
import random
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from pymessenger.bot import Bot
import os

app = Flask(__name__)
ACCESS_TOKEN = 'EAAOTUZB2wuoYBAJgkPljxDaU2Vvwk1AjDS6LD7xiPfxe0MB1Ki7sBbPaaW1i4M4p1q1B34dMMNciPnuANlEi785Wvxe9e72HLz5fVQ2elZAEBLjZAbksGbyzm0G4XvY6gQ10C3IcUPAXgm54SKeZAgnhmvWmoi4MwkMRzHZBi7QZDZD'
VERIFY_TOKEN = 'TESTINGTOKEN'
bot = Bot(ACCESS_TOKEN)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://uhlfsytbmtlqdi:82d98d9f0a1f9ce38d3c0781a9941baf4f34f2ed52dbc4146ee75cffe42fc86d@ec2-46-137-170-51.eu-west-1.compute.amazonaws.com:5432/d3amnhpqd9452k'

db = SQLAlchemy(app)

from models import Message, User, Rating

#We will receive messages that Facebook sends our bot at this endpoint
@app.route("/", methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook."""
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
#     if the request was not get, it must be POST and we can just proceed with sending a message back to user
# check if the user has already provided a nickname

    # if str(request.get_json()['entry'][0]['messaging'][0]['sender']['id']) not in db.session.query(User.user).all():
    #     global update_user
    #     update_user=True
    #
    #     send_message(request.get_json()['entry'][0]['messaging'][0]['sender']['id'],'I do not believe we\'ve met - what is your nickname?')
    #
    # if update_user==True:
    #     #use input from last message as the nickname for the users table
    #     recipient_id = request.get_json()['entry'][0]['messaging'][0]['sender']['id']
    #     nickname = request.get_json()['entry'][0]['messaging'][0]['message']['text']
    #
    #     user_update = User(user=recipient_id,name=nickname)
    #
    #     #commit the nickname to the database
    #     db.session.add(user_update)
    #     db.session.commit()
    #
    #     global update_user
    #     update_user=False
    #
    #     #let the user know that the update was successful
    #     send_message(recipient_id, 'Love that name! I have taken note of it!')
    else:
       output = request.get_json()
       for event in output['entry']:
          messaging = event['messaging']
          for message in messaging:
            if message.get('message'):

                recipient_id = message['sender']['id']
                if message['message'].get('text'):
                    username = str(recipient_id)
                    datetime = str(message['timestamp'])
                    m = message['message']['text']

                    update_messages(username,m,datetime)

                    #check if message has rating and update rating db if so
                    check_rating(m)

                    #check if message is command
                    check_command(m,username)

                    response_sent_text = get_message()
                    send_message(recipient_id, response_sent_text)
                #if user sends us a GIF, photo,video, or any other non-text item
                if message['message'].get('attachments'):
                    username = str(recipient_id)
                    datetime = str(message['timestamp'])
                    m = message['message']['attachments']['payload']['url']

                    update_messages(username,m,datetime)

                    response_sent_nontext = get_message()
                    send_message(recipient_id, response_sent_nontext)
    return "Message Processed"


#checks if the message is a command
def check_command(message,username):
    length = len(message)
    if length > len('set name'):
        if message[:8]=='set name':
            nickname = message[9:]
            update_username(nickname,username)
            send_message(username,"Thanks, love that name!")
        else: pass
    else: pass

#update username in database
def update_username(nickname,username):
    user_update = User(user=username,name=nickname)

    db.session.add(user_update)
    db.session.commit()

#verify facebook token upon GET request
def verify_fb_token(token_sent):
    #take token sent by facebook and verify it matches the verify token you sent
    #if they match, allow the request, else return an error
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'

#updates rating in dataabse
def update_rating(username, rating, datetime):
    rating_update = Rating(user=username,rating=rating,date=datetime)

    db.session.add(rating_update)
    db.session.commit()

#updates messages in database
def update_messages(username, mes, datetime):
    message_to_commit = Message(user=username,mes=mes,date=datetime)

    db.session.add(message_to_commit)
    db.session.commit()

#check if message is rating
def check_rating(message):
    rating = 'null'
    if (len(message) >= 3):
        if (message[0].isdigit()) & (message[1]=='.') & (message[2].isdigit()):
            rating = float(message[:3])
    elif message[0].isdigit():
        rating = float(message[0])
    else:
        rating = rating
    if rating != 'null':
        update_rating(username, rating, datetime)

#chooses a random message to send to the user
def get_message():
    return "Thanks for sharing, let me know how you are doing later"

#uses PyMessenger to send response to user
def send_message(recipient_id, response):
    #sends user the text message provided via input response parameter
    bot.send_text_message(recipient_id, response)
    return "success"

if __name__ == "__main__":
    app.run()
