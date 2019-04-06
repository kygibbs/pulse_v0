#Python libraries that we need to import for our bot
import random
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from pymessenger.bot import Bot
import os

app = Flask(__name__)
ACCESS_TOKEN = 'EAAOTUZB2wuoYBAJFdgWTY7Jz2Bs0mvpJQATqW1aCzsZAZCR1zWE6hXiVINEeIbRvHbDkirZCorgq0H6ydh4aeDJBgt9rqNc2By9jUFbYkNOJ8kHxfL7uNqdobhgJ1bkXUpZCZBiEhBRrVMKZAfHbh4ehZBI2ra3hr3CFQykr3J6ApQZDZD'
VERIFY_TOKEN = 'TESTINGTOKEN'
bot = Bot(ACCESS_TOKEN)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://wrgfrthoobosxz:da8d915c0fafc5322c1f8c331acd269acbf4309bc7ff14af2f0a6797c0914655@ec2-54-228-212-134.eu-west-1.compute.amazonaws.com:5432/d1emremnjg5gsv'

db = SQLAlchemy(app)

from models import Message, User, Rating, Follower

#We will receive messages that Facebook sends our bot at this endpoint
@app.route("/", methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook."""
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
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
                    rating = check_rating(m,username,datetime)
                    command = check_command(m,username)

                    # key = check_key(rating,command)
                    if len(User.query.filter_by(user=str(recipient_id)).with_entities(User.name).first())>0:
                        Proliferate(recipient_id,m)
                    else:
                        bot.send_text_message(recipient_id,"please add a username with 'set name'")


                    # response_sent_text = get_message(key)
                    # send_message(recipient_id, response_sent_text)
                #if user sends us a GIF, photo,video, or any other non-text item
                if message['message'].get('attachments'):
                    username = str(recipient_id)
                    datetime = str(message['timestamp'])
                    for event in message['message']['attachments']:
                        m = event['payload']['url']
                        type = event['type']
                        update_messages(username,m,datetime)
                        if len(User.query.filter_by(user=str(recipient_id)).with_entities(User.name).first())>0:
                            Proliferate(recipient_id,m,type=type)
                        else:
                            bot.send_text_message(recipient_id,"please add a username with 'set name'")

                    # response_sent_nontext = get_message(4)
                    # send_message(recipient_id, response_sent_nontext)
    return "Message Processed"


#checks if the message is a command
def check_command(message,username):
    length = len(message)
    #self_name = User.query.filter_by(user=username).with_entities(User.name).first()[0]
    #SET NAME
    if length > len('set name'):
        if (message[:8]=='set name'):
            nickname = message[9:]
            update_username(nickname,username)
            return True
        else: pass
    #GET NAMES
    # if length > len('get names'):
    #     if (message[:9]=='get names'):
    #         users = User.query.with_entities(User.name).all()
    #         message = [str(str(user[0])+" | ") for user in users]
    #         bot.send_text_message(username,message)
    #     else: pass
    # #HOW ARE YOU?
    # if length > len('hay'):
    #     if (message[:3].lower()=='hay'):
    #         friend = message[4:]
    #         if len(User.query.filter_by(name=friend).all()) >0:
    #             friend_id = User.query.filter_by(name=friend).with_entities(User.user).first()[0]
    #             message = "{}: How are you?"
    #             bot.send_text_message(friend_id,message)
    #         else:
    #             pass
    #     else: pass
    # if length > len('tune in'):
    #     if (message[:7]=='tune in'):
    #         friend = message[8:]
    #         if (Follower.query.filter_by(user=username).filter_by(followed_nickname=friend).count()==0):
    #             update_followers(friend,username)
    #             return True
    #         else: pass
    #     else: pass
    else: pass
    return False

# #check which key to return
# def check_key(rating,command):
#     if rating == True:
#         return 1
#     if command == True:
#         return 3
#     else: return 2

#update username in database
def update_username(nickname,username):
    if len(User.query.filter_by(user=username).all())>0:
        User.query.filter_by(user=username).update(dict(name=nickname))
        db.session.commit()
    else:
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

#update Followers
def update_followers(friendname,username):

    new_follower = Follower(user=username,followed_nickname=friendname)

    db.session.add(new_follower)
    db.session.commit()

#check if message is rating
def check_rating(message,username,datetime):
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
        return True
    return False

#chooses a message to the user depending on what they sent before
# def get_message(key):
#     message_dict = {1:"Thanks for sharing", 2:"Interesting", 3:"Thanks! Love that name!",4:"Oh la la!"}
#     return message_dict[key]

def Proliferate(recipient_id,response,type=None):
    sender = User.query.filter_by(user=recipient_id).with_entities(User.name).first()
    for user in User.query.all():
        if user.user == recipient_id:
            if type == None:
                message = "{}: {}".format(sender,response)
                bot.send_text_message(user.user,message)
            else:
                message_1 = "{}: ".format(sender)
                bot.send_text_message(user.user,message_1)
                bot.send_attachment_url(user.user,type,response)


# #uses PyMessenger to send response to user
# def send_message(recipient_id, response):
#     if len(User.query.filter_by(user=recipient_id).with_entities(User.name).first()) >=1:
#         bot.send_text_message(recipient_id, response)
#         Proliferate(recipient_id,response)
#     else:
#
#     return "success"

if __name__ == "__main__":
    app.run()
