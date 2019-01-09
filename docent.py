import datetime
import json

import requests

from magister import Magister
from dateutil.parser import parse


class Docent(Magister):
    def __init__(self, *args, **kwargs):
        super(Docent, self).__init__(*args, **kwargs)

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
