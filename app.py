#Python libraries that we need to import for our bot
import random
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from pymessenger.bot import Bot
import os

app = Flask(__name__)
ACCESS_TOKEN = 'EAAOTUZB2wuoYBACxcMXmeBYvskTCRZCdTxxMkuBlBiABbX3RyuFQCWXH4jjfBDVftJ1dnp5e7pAjrYMjTOa9cxdqatiWboq0GF3xpMZBL7DE9HgM5joSZCnH2SecFaa5bk6HKSZCQGqSBH28gULUrC4umWBJGK9EpVcZCRCmyhNQZDZD'
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
                    mes_db_text = Message(user=username,mes=m,date=datetime)

                    db.session.add(mes_db_text)
                    db.session.commit()

                    # if (m[0].isdigit()) & (m[1]=='.') & (m[2].isdigit()):
                    #     rating = float(m[:3])
                    # elif m[0].isdigit():
                    #     rating = float(m[0])
                    #
                    # rating_update = Rating(user=username,rating=rating,date=datetime)
                    #
                    # db.session.add(rating_update)
                    # db.session.commit()

                    response_sent_text = get_message()
                    send_message(recipient_id, response_sent_text)
                #if user sends us a GIF, photo,video, or any other non-text item
                if message['message'].get('attachments'):
                    username = str(recipient_id)
                    datetime = str(message['timestamp'])
                    m = message['message']['attachments']['payload']['url']
                    mes_db_attach = Message(user=username,mes=m,date=datetime)

                    db.session.add(mes_db_attach)
                    db.session.commit()

                    response_sent_nontext = get_message()
                    send_message(recipient_id, response_sent_nontext)
    return "Message Processed"



def verify_fb_token(token_sent):
    #take token sent by facebook and verify it matches the verify token you sent
    #if they match, allow the request, else return an error
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'


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
