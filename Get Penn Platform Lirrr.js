// Variables used by Scriptable.
// These must be at the very top of the file. Do not edit.
// icon-color: purple; icon-glyph: subway;

//put in the key for your pushbullet
let push_key = "PUSHOVER USER KEY"


let baseURL = "https://penn-track-alert.herokuapp.com"
//let baseURL = "http://192.168.0.16:5000"

//pull Data
let url = baseURL + '/getTrains'
let r = new Request(url)
let json = await r.loadJSON()


// //Convert from arr of arrays to Map
// let trains = new Map();
// trains.set('test','jj');
// for (i in json){
//   item = json[i];
//   console.log(item);
//   trains.set(item[0],item[1]);
// }
// console.log(trains)

//Create popup
let alert = new Alert()
alert.title = "Choose a train"
let train
for (let i in json){
  train = json[i]
  alert.addAction(train[0])
}
alert.addCancelAction('Cancel')
//Choose Train
let resultIndex = await alert.presentSheet()
console.log(resultIndex)
//If chose real train, setup alert
if (resultIndex != -1){
  train = json[resultIndex]
  console.log(train[0])
  console.log('Train ID: ' + train[1])
  let r2 = new Request(baseURL + '/selectTrain')
  let body = {'push_key':push_key, 'train_id' : train[1]}
  r2.method = "POST"
  r2.headers = {'Content-Type' : 'application/json'}
  r2.body = JSON.stringify(body)
  console.log(r2.body)
  console.log("tet1")
  let resp = await r2.loadJSON()
  console.log("blaj")
  console.log(resp['status'])
  let a = new Alert()
  if (resp['status'] == 200){
    a.title = 'Setup Successful'
    a.message = 'You will be notified when the train arrives'
  } else{
    a.title = 'Error in Setup'
    a.message = resp['message']
  }
  a.addAction('Ok')
  await a.presentAlert()
  //Exit app
  let cb = new CallbackURL("launcher://homescreen")
  //await cb.open()



}


/*
let str = JSON.stringify(json, null, 2)
QuickLook.present(str)
*/
