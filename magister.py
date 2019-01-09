"""
    MagisterAPI
    todo: every part should have his own file:
    - cijfers
    - mentor
"""
import random
from getpass import getpass
from urllib.parse import unquote
import requests
import json
from enum import Enum


class Reden(Enum):
    Telaat = 14
    Uitgestuurd = 25
    Absent = 47
    Aanwezig = 52
    Boekenvergeten = 54
    Huiswerkvergeten = 55


class Magister:
    school = ""
    gebruikersnaam = ""
    wachtwoord = ""
    filterName = ""
    authorizeUrl = ""
    profiel = {}
    persoonId = 0
    returnUrl = ""
    sessionId = ""
    xsrf = ""
    bearerToken = ""
    headers = {}
    s = requests.Session()

    def __init__(self, school, username, password):
        self.__accountUrl = "https://accounts.magister.net"
        self.__authUrl = "https://accounts.magister.net/challenge/"
        self.login(school, username, password)

    def login(self, school, username, password):
        def randomhash():
            return '%032x' % random.getrandbits(128)

        if "https://" not in school and "magister.net" not in school:
            raise ValueError('Wrong url format, needs to be: https://schooname.magister.net')

        if not username:
            raise ValueError('No username provided')

        if not password:
            raise ValueError('No password provided')

        # needed variables
        self.school = school
        self.gebruikersnaam = username
        self.wachtwoord = password
        self.filterName = school.replace("https://", "")
        self.authorizeUrl = "https://accounts.magister.net/connect/authorize?client_id=M6-" + self.filterName + \
                            "&redirect_uri=https%3A%2F%2F" + self.filterName + "%2Foidc%2Fredirect_callback.html" + \
                            "&response_type=id_token%20token&scope=openid%20profile%20magister.ecs.legacy%20" + \
                            "magister.mdv.broker.read%20magister.dnn.roles.read" + \
                            "&state=" + randomhash() + \
                            "&nonce=" + randomhash() + "&acr_values=tenant%3A" + self.filterName
        self.profiel = {}
        self.persoonId = 0

        # get authorizeUrl
        r = self.s.get(self.authorizeUrl, allow_redirects=False)

        if r.status_code != 302:
            raise RuntimeError("ReturnUrl error " + str(r.status_code))

        self.returnUrl = unquote(r.headers['Location'].split("returnUrl=")[1])

        r2 = self.s.get(r.headers['Location'], allow_redirects=False)
        if r2.status_code != 302:
            raise RuntimeError("SessionId error " + str(r2.status_code))

        self.sessionId = r2.headers['Location'] \
            .split("?")[1] \
            .split("&")[0] \
            .split("=")[1]

        # get xsrf
        self.xsrf = r2.headers['Set-Cookie'].split("XSRF-TOKEN=")[1].split(";")[0]

        # prepare data
        data = {
            "sessionId": self.sessionId,
            "returnUrl": self.returnUrl,
            "username": self.gebruikersnaam
        }

        # prapare headers
        headers = {
            "X-XSRF-TOKEN": self.xsrf
        }

        # post username
        r3 = self.s.post(self.__authUrl + "username", json=data, headers=headers)
        if r3.status_code != 200:
            raise RuntimeError("Username error " + str(r3.status_code))

        # post password
        data = {
            "sessionId": self.sessionId,
            "returnUrl": self.returnUrl,
            "password": self.wachtwoord
        }

        r4 = self.s.post(self.__authUrl + "password", json=data, headers=headers)
        if r4.status_code != 200:
            raise RuntimeError("Password error " + str(r4.status_code))

        r5 = self.s.get(self.__accountUrl + self.returnUrl, headers=headers, allow_redirects=False)
        if r5.status_code != 302:
            raise RuntimeError("BearerToken error " + str(r5.status_code))

        self.bearerToken = r5.headers["Location"].split("&access_token=")[1].split("&")[0]

        # set headers to use everywhere!
        self.headers = {
            "Authorization": "Bearer " + self.bearerToken,
            "X-XSRF-TOKEN": self.xsrf
        }

    def get_profiel(self):
        """ this function retrieves the users profile. """
        # todo error handling
        # todo do we need this in the future for the Persoon Id?

        r = self.s.get(self.school + "/api/account?noCache=0", headers=self.headers)

        self.profiel = json.loads(r.text)
        self.persoonId = self.profiel["Persoon"]["Id"]

        return self.profiel

