import json

from magister import Magister


class Mentor(Magister):
    def __init__(self, *args, **kwargs):
        # Magister.__init__(self, *args, **kwargs)
        super(Mentor, self).__init__(*args, **kwargs)

    def get_mentorstudenten(self):
        r = self.s.get(self.school + "/api/leerlingen/zoeken?q=**&top=40&skip=0&rol=mentor", headers=self.headers)

        return json.loads(r.text)
