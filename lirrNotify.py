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
    return trains



def selectTrain(train_id):
    df = pd.DataFrame(getTrains()).set_index('TRAIN_ID')
    #check if id valid
    print("Error: Train ID ", train_id, " not valid")
    #while loop
    track = ''
    while(track == ''):
        df = pd.DataFrame(getTrains()).set_index('TRAIN_ID')
        if(train_id in df.index ):
            track = df.loc[train_id]['TRACK']
            if(track == ''):
                print("Track not assigned yet. Try again in 5 seconds")
                time.sleep(5)
        else:
            print('error: TRAIN_ID not found in index, continuing')
            print(df)
    #notify
    print(df.loc['TRAIN_ID']['descrip'], "is on track ", track)

def waitForNext():
    df = pd.DataFrame(getTrains()).set_index('TRAIN_ID')
    next = df[df['TRACK'] == ''].iloc[0]
    print(next)
    train_id = next.name
    selectTrain(train_id)



def main():
    trains = getTrains()
    df = pd.DataFrame(trains)
    print(df)
    waitForNext()



if __name__ == '__main__':
    main()
