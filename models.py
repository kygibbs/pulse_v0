from manage import db,app

class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(240))
    mes = db.Column(db.String(240))
    date = db.Column(db.String(240))

    def __repr__(self):
        return '<Message %r>' % (self.user)

class Follower(db.Model):
    __tablename__ = 'followers'

    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(240))
    followed_nickname = db.Column(db.String(240))

    def __repr__(self):
        return '<Followers %r>' % (self.followed)

class User(db.Model):
    __tablename__ = 'users'

    user = db.Column(db.String(240), primary_key=True)
    name = db.Column(db.String(240))

    def __repr__(self):
        return '<User %r>' % (self.name)

class Rating(db.Model):
    __tablename__ = 'ratings'

    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(240))
    rating = db.Column(db.Float)
    date = db.Column(db.String(240))

    def __repr__(self):
        return '<Rating %r>' % (self.rating)
