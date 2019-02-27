#Python libraries that we need to import for our bot
import random
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from pymessenger.bot import Bot
import os

global update_user
update_user = False

app = Flask(__name__)
ACCESS_TOKEN = 'EAAESRJliwPcBAJKIOMg1WKY437OoQNWYYoD9AJompasaK2FTm5WoB2XvfyidU2ZCJKBG7SC8vCAk4DtZBX98GVX7ZBF6V4eDTf48DzD9RdgTZA7TRmT6sR4vE3m0Ye43VvLtW6vaGyR3btsVssxkCZA5dsZB9oFBhoF5GxvKHghwZDZD'
VERIFY_TOKEN = 'TESTINGTOKEN'
bot = Bot(ACCESS_TOKEN)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://omytmjqkfbjiyv:30dcaab68234825cadbcbb4705f6b6f6281103217e1b5dd353196f33f54e3aa5@ec2-79-125-4-96.eu-west-1.compute.amazonaws.com:5432/d1ol0ntblihdgm'

db = SQLAlchemy(app)

from models import Message, User, Rating

#We will receive messages that Facebook sends our bot at this endpoint
@app.route("/", methods=['GET', 'POST'])
def receive_message(update=update_user):
    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook."""
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    #if the request was not get, it must be POST and we can just proceed with sending a message back to user
    if update_user==True:
        #use input from last message as the nickname for the users table
        recipient_id = request.get_json()['entry']['messaging']['sender']['id']
        nickname = recipient_id = request.get_json()['entry']['messaging']['message']['text']

        user_update = User(user=recipient_id,name=nickname)

        #commit the nickname to the database
        db.session.add(user_update)
        db.session.commit()

        update_user=False

        #let the user know that the update was successful
        send_message(recipient_id, 'Love that name! I have taken note of it!')

    else:
        #check if the user has already provided a nickname
        if request.get_json()['entry']['messaging']['sender']['id'] not in session.query(users.user).all():

            update_user=True

            send_message(request.get_json()['entry']['messaging']['sender']['id'],'I do not believe we\'ve met - what is your nickname?')

        elif request.get_json()['entry']['messaging']['message']['text']=='check in':

            query = session.query(ratings).filter(ratings.user==request.get_json()['entry']['messaging']['sender']['id']).order_by(ratings.date)
            rating_list = [i.rating for i in query.all()]

            send_message(request.get_json()['entry']['messaging']['sender']['id'],rating_list)

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

                        if (m[0].isdigit()) & (m[1]=='.') & (m[2].isdigit()):
                            rating = float(m[:3])
                        elif m[0].isdigit():
                            rating = float(m[0])

                        rating_update = Rating(user=username,rating=rating,date=datetime)

                        db.session.add(rating_update)
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
    return "Thanks for sharing, let me know how you are doing later"

#uses PyMessenger to send response to user
def send_message(recipient_id, response):
    #sends user the text message provided via input response parameter
    bot.send_text_message(recipient_id, response)
    return "success"

if __name__ == "__main__":
    app.run()
