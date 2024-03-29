import requests
import json
import time
from dateutil.parser import parse
from pprint import pprint
import pandas as pd
from flask import *
import threading
import datetime
import pytz



#init flask
app = Flask(__name__)


PUSHOVER_TOKEN = 'PUSHOVER TOKEN'

def loadStationInfo():
    #resp = requests.get('https://traintime.lirr.org/api/Stations-All')
    #data = resp.json()
    file = open('./Stations-All.json')
    text = file.read()
    file.close()
    data = json.loads(text)
    stations = pd.DataFrame(data['Stations']).T.set_index('ABBR')['NAME']
    return stations

#pulls train data from LIRR and return it processed in DF
def getTrains():
    stations = loadStationInfo()
    resp = requests.get('https://traintime.lirr.org/api/Departure?loc=NYK')
    data = json.loads(resp.text)
    trains = data['TRAINS']
    tz = pytz.timezone("America/New_York")
    #Convert time to time
    for train in trains:
        train['time'] = tz.localize(parse(train['SCHED']))
        train['destination'] = stations.loc[train['DEST']]
        train['descrip'] =  train['time'].strftime('%I:%M %p') + ' towards ' + train['destination']
    df = pd.DataFrame(trains).set_index('TRAIN_ID')
    return df

@app.route("/getTrains")
def getTrainsRest():
    df = getTrains()
    descriptions =  df['descrip'].to_dict()
    print(descriptions)
    #Converts to list of lists so stays ordered, AND switches the key and the value
    desc_list =[[v, u] for (u, v) in descriptions.items()]
    headers = {'Content-Type' :'application/json'}
    js = json.dumps(desc_list)
    print(js)
    return js,200,headers




@app.route("/selectTrain",methods=['POST','GET'])
def selectTrainAPI():
    #put in check to see  tingz there +valid
    body = request.get_json()
    train_id = body['train_id']
    push_key = body['push_key']
    print("New selecTrains Request with content:")
    print("train_id :",train_id)
    print("push_key :", push_key)


    #check if train_id is valid
    df = getTrains()
    if(train_id in df.index):
        #Check if train is in more than 40 min
        depart = df.loc[train_id]['time']
        print("departireTime : ", depart.isoformat())
        tz = pytz.timezone("America/New_York")
        now = datetime.datetime.now(tz = tz)
        timeDiff = depart - now
        print("Curr time : ", now.isoformat())
        print("Time Diff", timeDiff)
        if(timeDiff > datetime.timedelta(hours=1)):
            print("Train leaves over an hour from now. We're not doing this sis")
            sendNotification(push_key,'Error: Train leaves too long from now','Please request again less than an hour before departure.')
            return {'status':403,'message':'Error: Train leaves over an hour from now. Please Select and Earlier train'},403



        t = threading.Thread(target=selectTrain,args=(train_id,push_key,))
        t.start()
        return {'status':200,'message' : 'Successfully selected train. Notification setup.' },200
    else:
        return {'status':400,'message': 'Error: train_id not valid'},400


def selectTrain(train_id,push_key):
    df = getTrains()
    #error count
    errorCount = 0

    track = ''
    while(track == ''):
        df = getTrains()
        if(train_id in df.index ):
            track = df.loc[train_id]['TRACK']
            if(track == ''):
                print("Track not assigned yet. Try again in 5 seconds")
                time.sleep(10)
        else:
            print('error: TRAIN_ID,',train_id,', not found in index, continuing')
            print("Error Count:", errorCount)
            time.sleep(2)
            errorCount+=1
            #if error more than 10 times, kill the thread
            if(errorCount > 10):
                print('Reached 10 errors, quitting thread')
                return
    #notify
    string = df.loc[train_id]['descrip'] + " is on Track "+ track
    print(string)
    #send notification using pushover
    sendNotification(push_key,'Track ' + track,string)


#send notification using pushover
def sendNotification(push_key,title,message):
    data = {'token' : PUSHOVER_TOKEN,
            'user' : push_key,
            'title' : title,
            'message' : message}
    resp = requests.post('https://api.pushover.net/1/messages.json',params=data)


def waitForNext():
    df = getTrains()
    next = df[df['TRACK'] == ''].iloc[0]
    print(next)
    train_id = next.name
    selectTrain(train_id)



def main():
    df = getTrains()
    print(df)
    app.run('0.0.0.0')


    #waitForNext()
    pass



if __name__ == '__main__':
    main()
