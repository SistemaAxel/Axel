from flask import Flask, render_template, request, redirect
#from flask_gtts import gtts
from yaml import load, SafeLoader
from pysondb import getDb
from datetime import datetime
import pandas

CONFIG = load(open("config.yaml", "r"), SafeLoader)

if CONFIG["Comedor"]["Encendido"]:
    Comedor_Menu = {}
    Comedor_Menu_Hoy = {}


def get_menu_today(menu):
    fecha = menu[menu["Fecha"] == "2023-11-24"]
    e = {
        "Fecha": fecha["Fecha"].iloc[:1][0],
        "Plato1": fecha["Plato1"].iloc[:1][0],
        "Plato2": fecha["Plato2"].iloc[:1][0],
        "Postre": fecha["Postre"].iloc[:1][0],
        "Pan": fecha["Pan"].iloc[:1][0],
    }
    return e


def load_comedor():
    Comedor_Menu = {}
    for menu in CONFIG["Comedor"]["Menus"]:
        print(f"/{CONFIG['Comedor']['Id']}/{menu}.csv")
        df = pandas.read_csv(
            f"{CONFIG['Comedor']['Url']}/{CONFIG['Comedor']['Id']}/{menu}.csv", sep=","
        )
        Comedor_Menu[menu] = df
        Comedor_Menu_Hoy[menu] = get_menu_today(df)


if CONFIG["Clase"]["Encargos"]["Encendido"]:
    Clase_Encargos = getDb(CONFIG["Clase"]["Encargos"]["Archivo"])

app = Flask(__name__)
#gtts(app, route=True, route_path="/gtts")


def check_embed():
    if request.args.get("embed") != None:
        return True
    else:
        return False


@app.route("/")
def index():
    can_encargos = CONFIG["Clase"]["Encargos"]["Encendido"]
    encargoss = Clase_Encargos.getAll() # Clase_Encargos.getByQuery({"fecha": get_date()})
    return render_template(
        "index.html",
        escuela_clase=CONFIG["Clase"]["Nombre"],
        can_encargos=can_encargos,
        encargos=encargoss,
        escuela_nombre=CONFIG["Escuela"]["Nombre"],
    )
    # return "Index"


@app.route("/menu_comedor")
def menu_comedor():
    load_comedor()
    if CONFIG["Comedor"]["Encendido"]:
        comedor = CONFIG["Comedor"]["Nombre"]
        return render_template(
            "menu_comedor.html",
            hoy=Comedor_Menu_Hoy,
            menus=CONFIG["Comedor"]["Menus"],
            comedor=comedor,
            embed=check_embed(),
        )
    else:
        return render_template("menu_comedor.no_comedor.html")


def get_date():
    now = datetime.now()
    return f"{now.year}-{now.month}-{now.day}"


@app.route("/encargos/ver")
def encargos__ver():
    can_encargos = CONFIG["Clase"]["Encargos"]["Encendido"]
    encargoss = Clase_Encargos.getAll()
    return render_template(
        "encargos/ver.html",
        escuela_clase=CONFIG["Clase"]["Nombre"],
        can_encargos=can_encargos,
        encargos=encargoss,
        embed=check_embed(),
    )


@app.route("/encargos/hoy")
def encargos__hoy():
    can_encargos = CONFIG["Clase"]["Encargos"]["Encendido"]
    encargoss = Clase_Encargos.getByQuery({"fecha": get_date()})
    return render_template(
        "encargos/hoy.html",
        escuela_clase=CONFIG["Clase"]["Nombre"],
        can_encargos=can_encargos,
        encargos=encargoss,
        embed=check_embed(),
    )


@app.route("/encargos/nuevo")
def encargos__nuevo():
    return render_template(
        "encargos/nuevo.html",
        escuela_clase=CONFIG["Clase"]["Nombre"],
        embed=check_embed(),
    )


@app.route("/encargos/editar/<i>")
def encargos__editar(i):
    enc = Clase_Encargos.getById(i)
    return render_template(
        "encargos/editar.html",
        escuela_clase=CONFIG["Clase"]["Nombre"],
        f=enc,
        embed=check_embed(),
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
            "hecho": "No",
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
            "hecho": "No",
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
    app.run(host="0.0.0.0", port=12321, debug=True)
