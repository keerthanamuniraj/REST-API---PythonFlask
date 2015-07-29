__author__ = 'keer7682'

from flask import Flask, request, jsonify, Response, make_response
from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug.routing import BaseConverter
from sqlalchemy import DateTime
import hashlib
import datetime


app = Flask(__name__)
db = SQLAlchemy(app)
app.config[
    'SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/pppdb'


class Users(db.Model):
    __tablename__ = 'users'
    serialno = db.Column(db.Integer)
    username = db.Column(db.String(20), primary_key=True)
    hashpswd = db.Column(db.String(20))


class Recordtype(db.Model):
    __tablename__ = 'recordtype'
    serialnum = db.Column(db.Integer)
    type = db.Column(db.String(20), primary_key=True)
    description = db.Column(db.String(100))


class Ppp(db.Model):
    __tablename__ = 'ppp'
    serial_no = db.Column(db.Integer)
    username = db.Column(db.String(20), db.ForeignKey('users.username'),
                         primary_key=True)
    date_entered = db.Column(DateTime, default=datetime.datetime.now().date(),
                             primary_key=True)
    type = db.Column(db.String(20), db.ForeignKey('recordtype.type'),
                     primary_key=True)
    content = db.Column(db.Text)


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]

app.url_map.converters['regex'] = RegexConverter

def validatetoken(tokenreceived, username):
    try:
        token = Users.query.filter_by(username=username,
                                      hashpswd=tokenreceived).first()
        if token:
            return True
    except Exception:
        return False


@app.route("/")
def hello():
    return "Hello welcome to project TRACKBONE"


@app.route('/users/adduser/', methods=['GET', 'POST'])
def users():
    if request.method == 'POST':
        try:
            request_info = request.json
            username = request_info['username']
            rawpassword = request_info['password']
            hash_object = hashlib.md5(rawpassword)
            hex_dig = hash_object.hexdigest()
            hashpswd = hex_dig
            u = Users(username=username, hashpswd=hashpswd)
            db.session.add(u)
            db.session.commit()
            return "User added"
        except Exception:
            json_results = []
            error = {
                'Error': 'the username already exists, please enter another valid username!'}
            json_results.append(error)
            return make_response(jsonify(error), 400)


@app.route("/login/", methods=["POST"])
def login():
    if request.method == 'POST':
        try:
            request_info = request.json
            username = request_info['username']
            rawpassword = request_info['password']
            hash_object = hashlib.md5(rawpassword)
            hex_dig = hash_object.hexdigest()
            entered_hash_pswd = hex_dig
            try:
                token = Users.query.filter_by(username=username).first()
                if token.hashpswd == entered_hash_pswd:
                    response = {"password": token.hashpswd}
                    return make_response(jsonify(response), 200)

            except Exception:
                # if the users enter credentials which are not matched
                return make_response("Invalid credentials", 401)

        except Exception:
            json_results = []
            error = {
                'Error': 'please check your request'}
            json_results.append(error)
            return make_response(jsonify(error), 500)


@app.route(
    '/users/<regex("[a-zA-Z][a-zA-Z][a-zA-Z][a-zA-Z][0-9][0-9][0-9][0-9]"):username>/recordtype/',
    methods=['GET'])
def recordtype(username):
    if validatetoken(request.headers.get('X-Auth-Token'), username):

        if request.method == 'GET':
            try:
                results = Recordtype.query.all()
                json_results = []
                for result in results:
                    d = {'serialnum': result.serialnum,
                         'type': result.type,
                         'description': result.description}
                    json_results.append(d)
                return jsonify(recordtype=json_results)
            except Exception:
                return Response("Error", 400)
    else:
        json_results = []
        error = {
            'Error': 'please check your request'}
        json_results.append(error)
        return make_response(jsonify(error), 400)


@app.route(
    '/users/<regex("[a-zA-Z][a-zA-Z][a-zA-Z][a-zA-Z][0-9][0-9][0-9][0-9]"):username>/pppentry/',
    methods=['POST'])
def ppp(username):
    if validatetoken(request.headers.get('X-Auth-Token'), username):
        if request.method == 'POST':
            try:
                request_info = request.json
                username_entered = request_info['username']
                entrydate = request_info['date']
                type = request_info['type']
                content = request_info['content']
                if username == username_entered:
                    u = Ppp(username=username_entered, date_entered=entrydate,
                            type=type, content=content)
                    db.session.add(u)
                    db.session.commit()
                    return "ppp record added"
                else:
                    json_results = []
                    error = {
                        'Error': 'This operation is not allowed'}
                    json_results.append(error)
                    return make_response(jsonify(error), 400)

            except Exception as e:
                json_results = []
                error = {
                    'Error': str(e)}
                json_results.append(error)
                return make_response(jsonify(error), 400)

    else:
        json_results = []
        error = {
            'Error': 'please check your request'}
        json_results.append(error)
        return make_response(jsonify(error), 400)


@app.route(
    '/users/<regex("[a-zA-Z][a-zA-Z][a-zA-Z][a-zA-Z][0-9][0-9][0-9][0-9]"):username>/record/',
    methods=['GET'])
def example(username):
    recordtype = request.args.get('recordtype')
    date = request.args.get('date')
    if validatetoken(request.headers.get('X-Auth-Token'), username):
        if request.method == 'GET':
            try:
                token = Ppp.query.filter_by(username=username,
                                            date_entered=date).first()
                if token.username == username and token.type == recordtype:
                    return "Welcome : %s !!! \nRecordtype : %s \nRecord content is : %s \ndate : %r" % (
                        username, recordtype, token.content,
                        str(token.date_entered))
            except Exception:
                json_results = []
                error = {
                    'Error': 'please check your request'}
                json_results.append(error)
                return make_response(jsonify(error), 500)

    else:
        json_results = []
        error = {
            'Error': 'please check your request'}
        json_results.append(error)
        return make_response(jsonify(error), 500)


@app.route(
    '/users/<regex("[a-zA-Z][a-zA-Z][a-zA-Z][a-zA-Z][0-9][0-9][0-9][0-9]"):username>/getrecord/',
    methods=['GET'])
def getrecord(username):
    team_username = request.args.get('team_username')
    date = request.args.get('date')
    type = request.args.get('type')
    if validatetoken(request.headers.get('X-Auth-Token'), username):
        if username == "libn1011":
            if request.method == 'GET':
                if team_username is None and date is None and type is None:
                    try:
                        results = Ppp.query.all()
                        json_results = []
                        for result in results:
                            d = {'serial_no': result.serial_no,
                                 'username': result.username,
                                 'date_entered': str(result.date_entered),
                                 'type': result.type,
                                 'content': result.content}
                            json_results.append(d)
                        return jsonify(ppp=json_results)

                    except Exception:
                        return Response("Error", 400)

                if team_username is None or date is None or type is None:
                    json_results = []
                    error = {
                        'Error': 'please make sure you have passed the 3 arguments :username,date and type'}
                    json_results.append(error)
                    return make_response(jsonify(error), 500)

                else:
                    results = Ppp.query.filter_by(username=team_username,
                                                  date_entered=date,
                                                  type=type).first()
                    return "username : %s \nrecordtype: %s \ndate: %r\ncontent: %s" % (
                        results.username, results.type,
                        str(results.date_entered),
                        results.content)

    else:
        json_results = []
        error = {
            'Error': 'please check your request'}
        json_results.append(error)
        return make_response(jsonify(error), 500)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
