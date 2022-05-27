from flask import Flask,request,session,abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
import json
import hashlib,time


app = Flask(__name__)
app.secret_key = "NO"
app.config['SQLALCHEMY_DATABASE_URI'] = 'NO'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

salt = "NO"

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(26), unique=False, nullable=False)
    messages = db.relationship('msg',backref="author",lazy=True)
    def __init__(self,username,password) -> None:
        self.username = username
        self.password = password



class msg(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    to_ = db.Column(db.String(50), unique=False, nullable=False)
    from_ = db.Column(db.String(50),db.ForeignKey('user.username'), nullable=False)
    message = db.Column(db.String(20), unique=False, nullable=False)
    timestamp = db.Column(db.Integer, nullable=False)
    def __init__(self,to_,from_,message,timestamp) -> None:
        self.to_ = to_
        self.from_ = from_
        self.message = message
        self.timestamp = timestamp

@app.route('/msg',methods=["POST"])
def get_messages():
    if 'username' not in session:
        return "Not logged in"
    d1 = [i for i in msg.query.filter_by(to_=request.form['to'],from_=request.form['from']).all()]
    d2 = [i for i in msg.query.filter_by(from_=request.form['to'],to_=request.form['from']).all()]
    d1.extend(d2)
    data = []
    theting = [i.timestamp for i in d1]
    theting.sort()
    for x,d in enumerate(theting):
        if d1[x].timestamp == d:
            data.insert(x,d1[x].from_+':'+d1[x].message)
    return json.dumps(data)

@app.route('/send_msg',methods=["POST"])
def send_messages():
    if 'username' not in session:
        return "Not logged in"
    m = msg(request.form['to'],request.form['from'],request.form['msg'],int(time.time()))
    db.session.add(m)
    db.session.commit()
    del m
    return 'sent'

@app.route('/users')
def get_user():
    if 'username' not in session:
        return "Not logged in"
    data = [i.username for i in User.query.order_by(User.username).all()]
    return json.dumps(data)

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        u = request.form["nm"]
        p = request.form['ps']
        p = hashlib.sha256(p.encode()+salt).hexdigest()
        account = User.query.filter_by(username=u).first()
        if account is None:
            return abort(404, description="Username is Incorrect")
        if account.password != p:
            return abort(404, description="Password is Incorrect")
        session['username'] = u
        
        return "Logged in"
    else:
        return "No get"

@app.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        username = request.form["nm"]
        password = request.form['ps']
        try:
            account = User(username, hashlib.sha256(password.encode()+salt).hexdigest())
            db.session.add(account)
            db.session.commit()
            session['username'] = username
        except IntegrityError:
            return abort(404, description="Username already exists")
        return "Signed Up!"
    else:
        return "No get"

@app.errorhandler(404)
def errorh(e):
    return e.description

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
