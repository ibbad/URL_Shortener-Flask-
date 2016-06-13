from app import db


class Url(db.Model):
    __tablename__ = "Url"
    id = db.Column('id', db.Integer, primary_key=True)
    random_key = db.Column(db.String(length=80), unique=True)
    url = db.Column(db.String(length=120), unique=False)

    def __init__(self, random_key, url):
        self.random_key = random_key
        self.url = url

    def __repr__(self):
        return '<url %r>' % self.url
