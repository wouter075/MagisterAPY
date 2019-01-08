import json

from magister import Magister


class Mentor(Magister):
    def __init__(self, school, username, password):
        Magister.__init__(self, school, username, password)

    def get_mentorstudenten(self):
        r = self.__s.get(self.school + "/api/leerlingen/zoeken?q=**&top=40&skip=0&rol=mentor", headers=self.__headers)

        return json.loads(r.text)
