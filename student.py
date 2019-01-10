import datetime
import json

from docent import Docent
from magister import Magister, Reden


class Student(Magister):
    def __init__(self, school, username, password):
        Magister.__init__(self, school, username, password)


    def get_student(self, zoekterm):
        """ Deze method zoekt naar een student: naam en stamnummer kunnen worden gebruikt """
        # todo error handling
        r = self.s.get(self.school + "/api/leerlingen/zoeken?q=" + zoekterm + "&top=40&skip=0",
                         headers=self.headers)

        response = json.loads(r.text)
        if response["items"]:
            return response["items"]
        else:
            return False

    def get_studentabsenties(self, persoonId):
        today = str(datetime.date.today())
        r = self.s.get(self.school + "/api/m6/leerlingen/" + str(persoonId) +
                         "/verantwoordingen/maanden?begin=2018-08-01&einde=" + today, headers=self.headers)
        return json.loads(r.text)


