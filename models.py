from manage import db,app

class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer)
    mes = db.Column(db.String(240))
    date = db.Column(db.String(240))

    def __repr__(self):
        return '<Message %r>' % (self.nickname)
