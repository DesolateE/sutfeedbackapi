from flask import Flask, request,jsonify
from flask_cors import CORS, cross_origin
from flask_restful import Resource, Api
#from json import dumps
import json
import pyrebase
import deepcut
import stopword
import positiveword
import negativeword
import os

app = Flask(__name__)
api = Api(app)
CORS(app)


configclass = {
  "apiKey": "AIzaSyB2dzuzgKVykU54B6ODJnqWCuRNdoENzkk",
  "authDomain": "sut-classroom.firebaseapp.com",
  "databaseURL": "https://sut-classroom.firebaseio.com",
  "storageBucket": "sut-classroom.appspot.com"
}

@app.route("/")
def hello():
    output = 'Hello World'
    return output

@app.route('/start', methods=['POST'])
def getrequest():
    data = json.loads(request.data.decode())
    print(data)
    firebase = pyrebase.initialize_app(configclass)
    db = firebase.database()
    word = deepcut.tokenize(data["comment"], custom_dict='custom_dict.txt')
    cut = [w for w in word if not w in stopword.stopword]
    poslist = []
    neglist = []
    neulist = cut.copy()
    poscount = 0
    negcount = 0
    for y in cut:
        for pos in positiveword.positive_word:
            if y == pos:
                poscount += 1
                poslist.append(y)
        for neg in negativeword.negative_word:
            if y == neg:
                negcount += 1
                neglist.append(y)
                
    for y in poslist:
        if y in neulist:
            neulist.remove(y)
        
    for y in neglist:
        if y in neulist:
            neulist.remove(y)
                
    if(poscount > negcount):
        label = "positive"
    elif(negcount > poscount):
        label = "negative"
    else:
        label = "neutral"

    token = {'positive': poslist , 'neutral': neulist, 'negative': neglist}
    insert = json.dumps({'date': data["date"], 'comment': data["comment"], 'feeling': data["feeling"], 'classLabel': label, 'token': token , 'rating': data["ratingList"]}, ensure_ascii=False)
		
    db.child("users").child(data["uid"]).child("course").child(data["cid"]).child("Feedback").child(data["attendanceId"]).push(json.loads(insert))
    return jsonify({'status':'201'}) , 201



if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)



