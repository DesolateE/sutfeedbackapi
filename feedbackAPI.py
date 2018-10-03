from flask import Flask, request,jsonify
from flask_cors import CORS, cross_origin
from flask_restful import Resource, Api
#from json import dumps
import json
import pyrebase
import deepcut
import stop
import os

app = Flask(__name__)
api = Api(app)
CORS(app)


configclass = {
  "apiKey": "AIzaSyB5M0bxNI8kj3enMyPAgaksUVXU8qrNa4M",
  "authDomain": "classattendence-c4e10.firebaseapp.com",
  "databaseURL": "https://classattendence-c4e10.firebaseio.com",
  "storageBucket": "classattendence-c4e10.appspot.com"
}
positive_word = ['สอนเข้าใจ','ไม่ยาก','ชอบ','สอนดี','น่าสนใจ','สอนสนุก','สนุก'
                 ,'เยี่ยม','ดี','เข้าใจ','เข้าใจดี']
negative_word = ['ง่วง','สอนเร็ว','สอบยาก','ข้อสอบยาก','เสียงเบา','พูดเสียงเบา','จดไม่ทัน'
                 ,'พูดเร็ว','ไม่ค่อยเข้าใจ','งานเยอะ','ปล่อยช้า','ไม่เข้าใจ','ยาก','ไม่ได้ยิน']

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
    cut = [w for w in word if not w in stop.stopword]
    poslist = []
    neglist = []
    neulist = cut.copy()
    poscount = 0
    negcount = 0
    for y in cut:
        for pos in positive_word:
            if y == pos:
                poscount += 1
                poslist.append(y)
        for neg in negative_word:
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

    print(cut)  
    print(neulist)
    print(poslist)
    print(neglist)
    token = {'positive': poslist , 'neutral': neulist, 'negative': neglist}
    length = db.child("users").child(data["uid"]).child("course").child(data["cid"]).child("Feedback").child(data["attendanceId"]).get()
    insert = json.dumps({'date': data["date"], 'comment': data["comment"], 'feeling': data["feeling"], 'classLabel': label, 'token': token , 'rating': data["ratingList"]}, ensure_ascii=False)
    print(insert)
    if length.val() == None:
        pointer = 0
    else:
        pointer = len(length.val())
    db.child("users").child(data["uid"]).child("course").child(data["cid"]).child("Feedback").child(data["attendanceId"]).child(pointer).set(json.loads(insert))
    return jsonify({'status':'201'}) , 201



if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)



