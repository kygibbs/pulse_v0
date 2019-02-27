#Python libraries that we need to import for our bot
import random
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from pymessenger.bot import Bot
import os

app = Flask(__name__)
ACCESS_TOKEN = 'EAAESRJliwPcBAJKIOMg1WKY437OoQNWYYoD9AJompasaK2FTm5WoB2XvfyidU2ZCJKBG7SC8vCAk4DtZBX98GVX7ZBF6V4eDTf48DzD9RdgTZA7TRmT6sR4vE3m0Ye43VvLtW6vaGyR3btsVssxkCZA5dsZB9oFBhoF5GxvKHghwZDZD'
VERIFY_TOKEN = 'TESTINGTOKEN'
bot = Bot(ACCESS_TOKEN)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://jqxqtdeefghkxi:227dc3f7e5dcfcb1c85013de0645a5038e9dd31352935aab2b55bc410db2dbb3@ec2-54-228-212-134.eu-west-1.compute.amazonaws.com:5432/detdqgb26rpvc1'

db = SQLAlchemy(app)

from models import Message


#We will receive messages that Facebook sends our bot at this endpoint
@app.route("/", methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook."""
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    #if the request was not get, it must be POST and we can just proceed with sending a message back to user
    else:
        # get whatever message a user sent the bot
       output = request.get_json()
       for event in output['entry']:
          messaging = event['messaging']
          for message in messaging:
            if message.get('message'):
                #Facebook Messenger ID for user so we know where to send response back to
                recipient_id = message['sender']['id']
                if message['message'].get('text'):
                    username = str(message['sender']['id'])
                    datetime = str(message['timestamp'])
                    m = message['message']['text']
                    mes_db_text = Message(user=username,mes=m,date=datetime)

                    db.session.add(mes_db_text)
                    db.session.commit()

                    response_sent_text = get_message()
                    send_message(recipient_id, response_sent_text)
                #if user sends us a GIF, photo,video, or any other non-text item
                if message['message'].get('attachments'):
                    username = str(message['sender']['id'])
                    datetime = str(message['timestamp'])
                    m = message['message']['attachments']['payload']['url']
                    mes_db_attach = Message(user=user,mes=m,date=datetime)

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
    sample_responses = ["You are stunning!", "We're proud of you.", "Keep on being you!", "We're greatful to know you :)"]
    # return selected item to the user
    return random.choice(sample_responses)

#uses PyMessenger to send response to user
def send_message(recipient_id, response):
    #sends user the text message provided via input response parameter
    bot.send_text_message(recipient_id, response)
    return "success"

if __name__ == "__main__":
    app.run()
