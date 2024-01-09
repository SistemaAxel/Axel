from flask import Flask, render_template, request, redirect, send_file
from gtts import gTTS
from yaml import load, SafeLoader
from datetime import datetime
import requests
from translator import Client
from os import environ


def search_one(list, key, value):
    return next(item for item in list if item[key] == value)


refreshComedor = {}
ComedorData = {}
WeatherData = {}
clients = {}
refreshElTiempo = {}


def weather(RCONFIG):
    lat = RCONFIG["Escuela"]["Ubicacion"]["Lat"]
    lon = RCONFIG["Escuela"]["Ubicacion"]["Lon"]
    url = f"https://api.open-meteo.com/v1/forecast?latitude={str(lat)}&longitude={str(lon)}&current=temperature_2m,relative_humidity_2m,rain,wind_speed_10m"
    req = requests.get(url).json()["current"]
    res = {
        "Temperatura": req["temperature_2m"],
        "Humedad": req["relative_humidity_2m"],
        "Lluvia": req["rain"],
        "Viento": req["wind_speed_10m"],
    }
    return res


def get_date():
    now = datetime.now()
    return f"{now.year}-{now.month:02d}-{now.day:02d}"


def get_menu_today(menu):
    hoy = next((m for m in menu if m["fecha"] == get_date()), None)
    if hoy == None:
        return None
    return hoy


def load_weather(RCONFIG, fi):
    if refreshElTiempo.get(fi) == True or refreshElTiempo.get(fi) == None:
        refreshElTiempo[fi] = False
        WeatherData[fi] = weather(RCONFIG)
    return WeatherData[fi]


def load_comedor(RCONFIG, fi, client):
    if (
        refreshComedor.get(fi) == True
        or refreshComedor.get(fi) == None
        or ComedorData.get(fi) == None
    ):
        refreshComedor[fi] = False
        ComedorData[fi] = {"hoy": {}, "MC": {}}
        if RCONFIG["Comedor"]["Encendido"] == False:
            return ComedorData[fi]["hoy"], ComedorData[fi]["MC"]
        for menu in RCONFIG["Comedor"]["Menus"]:
            req = client.get_comedor(menu)
            ComedorData[fi]["MC"][menu] = req
            ComedorData[fi]["hoy"][menu] = get_menu_today(req)
    return ComedorData[fi]["hoy"], ComedorData[fi]["MC"]


app = Flask(__name__)
# gtts(app, route=True, route_path="/gtts")


def check_embed():
    if request.args.get("embed") != None:
        return True
    else:
        return False


def alldata(RCONFIG):
    fi = request.args["a"]
    if fi not in clients:
        clients[fi] = Client(environ["ET_USER"], environ["ET_PASS"], RCONFIG)
    client = clients[fi]
    cmh, cm = load_comedor(RCONFIG, fi, client)
    data = {
        "Clase": {
            "Nombre": RCONFIG["Clase"]["Nombre"],
        },
        "Escuela": {"Nombre": RCONFIG["Escuela"]["Nombre"]},
        "Comedor": {"Encendido": RCONFIG["Comedor"]["Encendido"]},
        "Embed": check_embed(),
        "Weather": load_weather(RCONFIG, fi),
        "Responsables": client.get_responsables(fi),
        "Tareas": client.get_tareas(fi),
        "Email": client.get_correo(fi),
    }
    if RCONFIG["Comedor"]["Encendido"]:
        data["Comedor"] = {
            "Encendido": RCONFIG["Comedor"]["Encendido"],
            "Nombre": RCONFIG["Comedor"]["Nombre"],
            "CodigoPostal": RCONFIG["Comedor"]["CodigoPostal"],
            "Menus": RCONFIG["Comedor"]["Menus"],
            "Hoy": cmh,
            "Dias": cm,
        }
    if data["Embed"]:
        data["Template"] = "embed.html"
    else:
        data["Template"] = "v2.html"
    return data


@app.route("/")
def index():
    RCONFIG = load(open("data/" + request.args["a"] + ".yaml", "r"), SafeLoader)
    return render_template("index.html", data=alldata(RCONFIG), a=request.args["a"])
    # return "Index"


@app.route("/responsables")
def responsables():
    RCONFIG = load(open("data/" + request.args["a"] + ".yaml", "r"), SafeLoader)
    return render_template(
        "responsables/index.html", data=alldata(RCONFIG), a=request.args["a"]
    )


@app.route("/tareas")
def tareas():
    RCONFIG = load(open("data/" + request.args["a"] + ".yaml", "r"), SafeLoader)
    return render_template(
        "tareas/index.html", data=alldata(RCONFIG), a=request.args["a"]
    )


def sayplease(msg):
    tts = gTTS(msg, lang="es")
    tts.save("./data/tts.mp3")
    return send_file("./data/tts.mp3")


@app.route("/menu_comedor")
def menu_comedor():
    RCONFIG = load(open("data/" + request.args["a"] + ".yaml", "r"), SafeLoader)
    return render_template(
        "menu_comedor.html", data=alldata(RCONFIG), a=request.args["a"]
    )


@app.route("/menu_comedor.txt")
def menu_comedor_txt():
    RCONFIG = load(open("data/" + request.args["a"] + ".yaml", "r"), SafeLoader)
    return render_template(
        "menu_comedor.txt", data=alldata(RCONFIG), a=request.args["a"]
    )


@app.route("/menu_comedor.json")
def menu_comedor_json():
    RCONFIG = load(open("data/" + request.args["a"] + ".yaml", "r"), SafeLoader)
    return RCONFIG["Comedor"]["Hoy"]


@app.route("/api/cron/weather")
def api__cron_weather():
    fi = request.args["a"]
    refreshElTiempo[fi] = True
    return "Refreshed."


@app.route("/api/cron/comedor")
def api__cron_comedor():
    fi = request.args["a"]
    refreshComedor[fi] = True
    return "Refreshed."


@app.route("/resumen")
def resumen():
    RCONFIG = load(open("data/" + request.args["a"] + ".yaml", "r"), SafeLoader)
    return render_template("resumen.html", data=alldata(RCONFIG), a=request.args["a"])


@app.route("/resumen-voz.txt")
def resumen_voz_txt():
    RCONFIG = load(open("data/" + request.args["a"] + ".yaml", "r"), SafeLoader)
    return render_template("resumen.txt", data=alldata(RCONFIG), a=request.args["a"])


@app.route("/resumen-voz.mp3")
def resumen_voz_mp3():
    RCONFIG = load(open("data/" + request.args["a"] + ".yaml", "r"), SafeLoader)
    return sayplease(
        render_template("resumen.txt", data=alldata(RCONFIG), a=request.args["a"])
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=12321, debug=False)
