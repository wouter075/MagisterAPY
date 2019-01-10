import datetime
import json

from docent import Docent
from magister import Magister, Reden


class Student(Magister):
    def __init__(self, school, username, password):
        Magister.__init__(self, school, username, password)




