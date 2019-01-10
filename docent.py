import datetime
import json

import requests

from magister import Magister
from dateutil.parser import parse

from student import Student
from magister import Reden


class Docent(Magister):
    def __init__(self, school, username, password):
        Magister.__init__(self, school, username, password)

    def set_studentaanwezig(self, persoonId):
        """ deze functie zet een student aanwezig op dit moment """
        afspraakid = Docent.get_huidigafspraakid()
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

        r = self.s.post("https://novacollege.magister.net/api/medewerkers/afspraken/" + str(afspraakId) +
                          "/verantwoordingen", headers=self.headers, json=data)

        if r.status_code == 204:
            return True
        else:
            return False

    def get_afsprakenvandaag(self):
        """ this function retrieves today lesson ids """
        # todo error handling
        today = str(datetime.date.today())
        idlist = []

        if self.persoonId == 0:
            # when no id, get the id from the profile
            self.get_profiel()

        r = self.s.get(self.school + "/api/medewerkers/" + str(self.persoonId) +
                         "/afspraken?begin=" + today + "&einde=" + today + "&status=actief", headers=self.headers)

        response = json.loads(r.text)
        if len(response["items"]) > 0:
            return response["items"]
        else:
            return False

    def get_huidigafspraakid(self):
        """ deze functie geeft het huidig afspraak id terug """
        afspraken = self.get_afsprakenvandaag()
        ct = datetime.datetime.utcnow()
        for a in afspraken:
            bt = parse(a["begin"]).replace(tzinfo=None)
            et = parse(a["einde"]).replace(tzinfo=None)
            if bt <= ct <= et:
                return a["id"]
