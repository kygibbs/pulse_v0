from apscheduler.schedulers.blocking import BlockingScheduler
import app
from app import db
from models import User, Rating, Message, Followers
import sqlalchemy
from sqlalchemy.sql.functions import Cast

sched = BlockingScheduler()
prev_time = 0

@sched.scheduled_job('interval', seconds=30)
def check_for_updates():
    time = int(Message.query.with_entities(Message.date).order_by(Message.id.desc()).first()[0])
    for username in User.query.with_entities(User.user).all():
        for follower in Follower.query.with_entities(Follower.followed_nickname).filter_by(Follower.user=username).all():
            user_id = User.query.with_entities(User.user).filter(User.name=follower).first()
            new_messages = Message.query.with_entities(Message.mes).filter(Cast(Message.date,sqlalchemy.BigInteger)>prev_time).all()
            for message in new_messages:
                app.send_message(username,str(follower+" said: "+message))
    prev_time = time

sched.start()
