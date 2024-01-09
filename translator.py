import datetime
import requests


class Client:
    def __init__(self, user, password, RCONFIG):
        self.user = user
        self.password = password
        self.conf = RCONFIG
        self.base = "https://ba.tech.eus"

    def get_comedor(self, menu):
        j = self._comedor_get_json()
        e = [self._comedor_to_dict(x) for x in j if self._comedor_search(x, menu)]
        return e

    def _comedor_search(self, array, menu):
        q = self._comedor_to_dict(array)
        if (
            q["codigo_postal"] == int(self.conf["Comedor"]["CodigoPostal"])
            and q["comedor"] == self.conf["Comedor"]["Nombre"]
            and q["menu"] == menu
        ):
            return True
    def _search(self, array, ident, key="aula", converter=None):
        q = converter(array)
        if q[key] == ident:
            return True
        return False
    def _search_2(self, array, val1, val2, key1="aula", key2="fecha", converter=None):
        q = converter(array)
        if q[key1] == val1 and q[key2] == val2:
            return True
        return False

    def _comedor_to_dict(self, array):
        now = datetime.datetime.fromtimestamp(int(array[3]))
        l = f"{now.year}-{now.month:02d}-{now.day:02d}"
        return {
            "codigo_postal": array[0],
            "comedor": array[1],
            "menu": array[2],
            "fecha": l,
            "plato1": array[4],
            "plato2": array[5],
            "plato3": array[6],
            "plato4": array[7],
        }

    def _correo_to_dict(self, array):
        return {
            "aula": array[0],
            "contenido": array[1],
        }

    def _responsables_to_dict(self, array):
        return {
            "aula": array[0],
            "nombre": array[1],
            "categoria": array[2],
            "correo": array[3],
            "telefono": array[4],
        }

    def _tareas_to_dict(self, array):
        now = datetime.datetime.fromtimestamp(int(array[1]))
        l = f"{now.year}-{now.month:02d}-{now.day:02d}"
        return {
            "aula": array[0],
            "fecha": l,
            "tarea": array[2],
            "responsable": array[3],
        }

    def auth(self):
        json_data = {
            "username": self.user,
            "password": self.password,
        }
        response = requests.post(self.base + "/api/auth", json=json_data)
        return response.json()["token"]

    def _comedor_get_json(self):
        headers = {"Authorization": "Bearer " + self.auth()}
        response = requests.get(
            self.base + "/api/et_axelaula_comedor/get_csv/v1?verbose=0",
            headers=headers,
        )
        return response.json()

    def _responsables_get_json(self):
        headers = {"Authorization": "Bearer " + self.auth()}
        response = requests.get(
            self.base + "/api/et_axelaula/get_responsables/v1?verbose=0",
            headers=headers,
        )
        return response.json()

    def _tareas_get_json(self):
        au = self.auth()
        print(au)
        headers = {"Authorization": "Bearer " + au}
        response = requests.get(
            self.base + "/api/et_axelaula/get_tareas/v1?verbose=0",
            headers=headers,
        )
        return response.json()

    def _correo_get_json(self):
        headers = {"Authorization": "Bearer " + self.auth()}
        response = requests.get(
            self.base + "/api/et_axelaula/get_mail/v1?verbose=0",
            headers=headers,
        )
        return response.json()

    def get_responsables(self, ident):
        j = self._responsables_get_json()
        e = [self._responsables_to_dict(x) for x in j if self._search(x, ident, "aula", self._responsables_to_dict)]
        return e

    def get_correo(self, ident):
        j = self._correo_get_json()
        e = [self._correo_to_dict(x) for x in j if self._search(x, ident, "aula", self._correo_to_dict)]
        return e
    def fecha(self):
        now = datetime.datetime.now()
        l = f"{now.year}-{now.month:02d}-{now.day:02d}"
        return l
    def get_tareas(self, ident):
        j = self._tareas_get_json()
        print(j)
        e = [self._tareas_to_dict(x) for x in j if self._search_2(x, ident, self.fecha(), "aula", "fecha", self._tareas_to_dict)]
        return e
