import datetime
import json
from magister import Magister, Reden


class Student(Magister):
    def __init__(self, school, username, password):
        Magister.__init__(self, school, username, password)

    def get_student(self, zoekterm):
        """ Deze method zoekt naar een student: naam en stamnummer kunnen worden gebruikt """
        # todo error handling
        r = self.__s.get(self.school + "/api/leerlingen/zoeken?q=" + zoekterm + "&top=40&skip=0",
                         headers=self.__headers)

        response = json.loads(r.text)
        if response["items"]:
            return response["items"]
        else:
            return False

    def get_studentabsenties(self, persoonId):
        today = str(datetime.date.today())
        r = self.__s.get(self.school + "/api/m6/leerlingen/" + str(persoonId) +
                         "/verantwoordingen/maanden?begin=2018-08-01&einde=" + today, headers=self.__headers)
        return json.loads(r.text)

    def set_studentaanwezig(self, persoonId):
        """ deze functie zet een student aanwezig op dit moment """
        afspraakid = self.get_huidigafspraakid()
        return self.set_studentreden(persoonId, afspraakid, Reden.Aanwezig)

    def set_studentreden(self, persoonId, afspraakId, redenId):
        if not isinstance(redenId, Reden):
            raise TypeError('redenId moet een instantie zijn van Reden')

        if self.persoonId == 0:
            # when no id, get the id from the profile
            self.get_profiel()

        data = {
            "persoonId": persoonId,
            "redenId": redenId.value
        }

        r = self.__s.post("https://novacollege.magister.net/api/medewerkers/afspraken/" + str(afspraakId) +
                          "/verantwoordingen", headers=self.__headers, json=data)

        if r.status_code == 204:
            return True
        else:
            return False
