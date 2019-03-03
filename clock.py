from apscheduler.schedulers.blocking import BlockingScheduler
import app
from app import db
from models import User, Rating, Message, Followers

sched = BlockingScheduler()
prev_time = 0

@sched.scheduled_job('interval', seconds=30)
def check_for_updates():
    time = Message.query.with_entities(Message.date).max()
    for username in User.query.with_entities(User.user).all():
        for follower in Followers.followed_nickname.query.filter_by(user=username).all():
            user_id = User.query.with_entities(User.user).filter(name=follower).first()
            new_messages = Message.query.with_entities(Message.mes).filter(user=user_id).filter(date > prev_time).all()
            for message in new_messages:
                app.send_message(username,str(follower+" said: "+message))
    prev_time = time

sched.start()
