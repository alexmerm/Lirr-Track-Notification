import requests
import json
from dateutil.parser import parse
from pprint import pprint
import time
import pandas as pd






#raw data request
def getData():
    resp = requests.get('https://traintime.lirr.org/api/Departure?loc=NYK')
    data = json.loads(resp.text)
    return data


#pulls train data from LIRR
def getTrains():
    data = getData()
    trains = data['TRAINS']
    #Convert time to time
    for train in trains:
        train['time'] = parse(train['SCHED'])
        train['descrip'] =  train['time'].strftime('%I:%M %p') + ' To ' + train['DEST']
    df = pd.DataFrame(trains).set_index('TRAIN_ID')
    return df




def selectTrain(train_id):
    df = getTrains()
    #check if id valid
    #while loop
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
            print(df)
    #notify
    string = df.loc[train_id]['descrip'] + " is on Track "+ track
    print(string)
    #send notification using pushover
    data = {'token' : '***REMOVED***',
            'user' : '***REMOVED***',
            'title' :'Track ' + track,
            'message' : string}
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
    waitForNext()



if __name__ == '__main__':
    main()
