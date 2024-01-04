import datetime
import requests
from flask import Flask, request
import os
app = Flask(__name__)

def auth(user, password):
  headers = {
      # Already added when you pass json=
      # 'Content-Type': 'application/json',
  }
  json_data = {
      'username': user,
      'password': password,
  }
  response = requests.post('htts://ba.tech.eus/api/auth', headers=headers, json=json_data)
  return response.json()["token"]

def get_json(token):
  headers = {'Authorization': 'Bearer ' + token}
  response = requests.get('https://ba.tech.eus/api/et_axelaula_comedor/get_csv/v1?verbose=0', headers=headers)
  return response.json()

a = auth(os.environ["ET_USER"],os.environ["ET_PASS"])
print(get_json(a))
def f(k):
    now = datetime.datetime.fromtimestamp(k[3])
    l = f"{now.year}-{now.month:02d}-{now.day:02d}"
    return {"codigo_postal": k[0], "comedor": k[1], "menu": k[2], "fecha": l, "plato1": k[4], "plato2": k[5], "plato3": k[6], "plato4": k[7]}
def c(arr, args):
    q = f(arr)
    if q["codigo_postal"] == int(args["cp"]) and q["comedor"] == args["c"] and q["menu"] == args["m"]:
       return True
@app.route('/get_data_for_me.csv')
def index():
    request.args["cp"]
    j = get_json(a)
    y = "Fecha,Plato1,Plato2,Postre,Pan\n"
    e = [f(x) for x in j if c(x, request.args)]
    for i in e:
       y += f"{i['fecha']},{i['plato1']},{i['plato2']},{i['plato3']},{i['plato4']}\n"
    return y
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=12321, debug=False)
