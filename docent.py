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


