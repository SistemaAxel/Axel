from flask import Flask, render_template, request, redirect, send_file
from gtts import gTTS
from yaml import load, SafeLoader
from pysondb import getDb
from datetime import datetime
import pandas
import requests
CONFIG = load(open("data/config.yaml", "r"), SafeLoader)

Comedor_Menu = {}
Comedor_Menu_Hoy = {}

def get_date():
    now = datetime.now()
    return f"{now.year}-{now.month:02d}-{now.day:02d}"

def get_menu_today(menu):
    fecha = menu[menu["Fecha"] == get_date()]
    if len(fecha["Fecha"].iloc[:1]) > 0:
      e = {
        "Fecha": fecha["Fecha"].iloc[-1],
        "Plato1": fecha["Plato1"].iloc[-1],
        "Plato2": fecha["Plato2"].iloc[-1],
        "Postre": fecha["Postre"].iloc[-1],
        "Pan": fecha["Pan"].iloc[-1],
      }
    else:
      e = None
    return e


def load_comedor():
    cmh = {}
    cm = {}
    if not CONFIG["Comedor"]["Encendido"]:
      return cmh, cm
    for menu in CONFIG["Comedor"]["Menus"]:
        #print(f"/{CONFIG['Comedor']['Id']}/{menu}.csv")
        df = pandas.read_csv(
            f"{CONFIG['Comedor']['Url']}/{CONFIG['Comedor']['Id']}/{menu}.csv", sep=","
        )
        cm[menu] = df
        cmh[menu] = get_menu_today(df)
    return cmh, cm

if CONFIG["Clase"]["Encargos"]["Encendido"]:
    Clase_Encargos = getDb("data/" + CONFIG["Clase"]["Encargos"]["Archivo"])
ElTiempo = {}
app = Flask(__name__)
#gtts(app, route=True, route_path="/gtts")


def check_embed():
    if request.args.get("embed") != None:
        return True
    else:
        return False

def alldata():
  cmh, cm = load_comedor()
  data = {
    "Encargos": {
      "Encendido": CONFIG["Clase"]["Encargos"]["Encendido"],
    },
    "Clase": {
      "Nombre": CONFIG["Clase"]["Nombre"],
    },
    "Escuela": {
      "Nombre": CONFIG["Escuela"]["Nombre"]
    },
    "Comedor": {
      "Encendido": CONFIG["Comedor"]["Encendido"]
    },
    "Embed": check_embed(),
    "Weather": ElTiempo
  }
  if CONFIG["Comedor"]["Encendido"]:
    data["Comedor"] = {
      "Encendido": CONFIG["Comedor"]["Encendido"],
      "Nombre": CONFIG["Comedor"]["Nombre"],
      "Id": CONFIG["Comedor"]["Id"],
      "Menus": CONFIG["Comedor"]["Menus"],
      "Hoy": cmh,
    }
  if CONFIG["Clase"]["Encargos"]["Encendido"]:
    data["Encargos"] = {
      "Encendido": CONFIG["Clase"]["Encargos"]["Encendido"],
      "Hoy": Clase_Encargos.getByQuery({"fecha": get_date()}),
      "Datos": Clase_Encargos.getAll()
      
    }
  if data["Embed"]:
    data["Template"] = "embed.html"
  else:
    data["Template"] = "v2.html"
  return data
@app.route("/")
def index():
    return render_template(
        "index.html",
        data=alldata()
    )
    # return "Index"
def sayplease(msg):
  tts = gTTS(msg, lang="es")
  tts.save('./tts.mp3')
  return send_file("./tts.mp3")


def weather():
  lat = CONFIG["Escuela"]["Ubicacion"]["Lat"]
  lon = CONFIG["Escuela"]["Ubicacion"]["Lon"]
  url = f"https://api.open-meteo.com/v1/forecast?latitude={str(lat)}&longitude={str(lon)}&current=temperature_2m,relative_humidity_2m,rain,wind_speed_10m"
  req = requests.get(url).json()["current"]
  res = {"temperatura": req["temperature_2m"], "humedad": req["relative_humidity_2m"], "lluvia": req["rain"], "viento": req["wind_speed_10m"]}
  return res
  
@app.route("/menu_comedor")
def menu_comedor():
    
    if CONFIG["Comedor"]["Encendido"]:
      return render_template(
        "menu_comedor.html",
        data=alldata()
      )
    else:
      return render_template("menu_comedor.apagado.html", data=alldata())

@app.route("/api/cron/hourly")
def api__cron():
  ElTiempo = weather()
  return "Refreshed."
@app.route("/resumen")
def resumen():
  return render_template(
        "resumen.html",
        data=alldata()
      )
@app.route("/resumen-voz.txt")
def resumen_voz_txt():
  return render_template(
        "resumen.txt",
        data=alldata()
      )

@app.route("/resumen-voz.mp3")
def resumen_voz_mp3():
  return sayplease(render_template(
        "resumen.txt",
        data=alldata()
      ))

@app.route("/encargos/ver")
def encargos__ver():
  if CONFIG["Clase"]["Encargos"]["Encendido"]:
    return render_template(
        "encargos/ver.html",
        data=alldata(),
    )
  else:
    return render_template(
            "encargos/ver.apagado.html",
            data=alldata(),
        )


@app.route("/encargos/hoy")
def encargos__hoy():
  if not CONFIG["Clase"]["Encargos"]["Encendido"]:
    return render_template(
        "encargos/hoy.apagado.html",
        data=alldata(),)
  return render_template(
    "encargos/hoy.html",
    data=alldata(),
  )
    


@app.route("/encargos/nuevo")
def encargos__nuevo():
  if not CONFIG["Clase"]["Encargos"]["Encendido"]:
    return render_template(
        "encargos/nuevo.apagado.html",
        data=alldata(),)
  return render_template(
        "encargos/nuevo.html",
        data=alldata(),
  )


@app.route("/encargos/editar/<i>")
def encargos__editar(i):
  if not CONFIG["Clase"]["Encargos"]["Encendido"]:
    return render_template(
        "encargos/hoy.apagado.html",
        data=alldata(),)
  enc = Clase_Encargos.getById(i)
  return render_template(
        "encargos/editar.html",
        data=alldata(),
        f=enc,
        id=i
    )


@app.route("/api/encargos/nuevo", methods=["POST"])
def api__encargos__nuevo():
    cliente = request.form["cliente"]
    fecha = request.form["fecha"]
    prod1 = request.form["prod1"]
    prod2 = request.form["prod2"]
    prod3 = request.form["prod3"]
    prod4 = request.form["prod4"]
    email = request.form["email"]
    hecho = request.form["hecho"]
    total = float(request.form["total"].replace(",", "."))
    pagado = float(request.form["pagado"].replace(",", "."))
    Clase_Encargos.add(
        {
            "fecha": fecha,
            "cliente": cliente,
            "prod1": prod1,
            "prod2": prod2,
            "prod3": prod3,
            "prod4": prod4,
            "email": email,
            "hecho": hecho,
            "total": total,
            "pagado": pagado,
        }
    )
    return redirect("/encargos/ver")


@app.route("/api/encargos/editar/<i>", methods=["POST"])
def api__encargos__editar(i):
    cliente = request.form["cliente"]
    fecha = request.form["fecha"]
    prod1 = request.form["prod1"]
    prod2 = request.form["prod2"]
    prod3 = request.form["prod3"]
    prod4 = request.form["prod4"]
    email = request.form["email"]
    hecho = request.form["hecho"]
    total = float(request.form["total"].replace(",", "."))
    pagado = float(request.form["pagado"].replace(",", "."))
    Clase_Encargos.updateById(
        i,
        {
            "fecha": fecha,
            "cliente": cliente,
            "prod1": prod1,
            "prod2": prod2,
            "prod3": prod3,
            "prod4": prod4,
            "email": email,
            "hecho": hecho,
            "total": total,
            "pagado": pagado,
        },
    )
    return redirect("/encargos/ver")


@app.route("/api/encargos/borrar/<i>", methods=["GET"])
def api__encargos__borrar(i):
    Clase_Encargos.deleteById(i)
    return redirect("/encargos/ver")


if __name__ == "__main__":
  ElTiempo = weather()
  app.run(host="0.0.0.0", port=12321, debug=True)
