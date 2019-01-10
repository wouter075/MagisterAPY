import json

from magister import Magister


class Mentor(Magister):
    def __init__(self, *args, **kwargs):
        # Magister.__init__(self, *args, **kwargs)
        super(Mentor, self).__init__(*args, **kwargs)


