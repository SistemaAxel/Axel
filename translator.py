import datetime
import requests


class Client:
    def __init__(self, user, password, RCONFIG):
        self.user = user
        self.password = password
        self.conf = RCONFIG
        self.base = "https://bb.tech.eus"
    def get_comedor(self, menu):
        j = self._comedor_get_json()
        e = [self._comedor_to_dict(x) for x in j if self._comedor_search(x, menu)]
        return e

    def _comedor_search(self, array, menu):
        q = self._comedor_to_dict(array)
        if (
            q["codigo_postal"] == int(self.conf["Comedor"]["CofigoPostal"])
            and q["comedor"] == self.conf["Comedor"]["Nombre"]
            and q["menu"] == menu
        ):
            return True
    def _responsables_search(self, array, ident):
        q = self._responsables_to_dict(array)
        if q["aula"] == ident:
            return True

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
    def _responsables_to_dict(self, array):
        return {
            "aula": array[0],
            "nombre": array[1],
            "categoria": array[2],
            "correo": array[3],
            "telefono": array[4],
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

    def get_responsables(self, ident):
        j = self._responsables_get_json()
        e = [self._responsables_to_dict(x) for x in j if self._responsables_search(x, ident)]
        return e