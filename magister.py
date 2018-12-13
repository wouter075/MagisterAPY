"""
    MagisterAPI
    todo: every part should have his own file:
    - student
    - teacher
    - grades
"""
import random
import datetime
from getpass import getpass
from urllib.parse import unquote
import requests
import json
from enum import Enum


class Reason(Enum):
    Telaat = 14
    Uitgestuurd = 25
    Absent = 47
    Aanwezig = 52
    Boekenvergeten = 54
    Huiswerkvergeten = 55


class Magister:
    def __init__(self, school, username, password):
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
        self.username = username
        self.password = password
        self.filterName = school.replace("https://", "")
        self.authorizeUrl = "https://accounts.magister.net/connect/authorize?client_id=M6-" + self.filterName + \
                            "&redirect_uri=https%3A%2F%2F" + self.filterName + "%2Foidc%2Fredirect_callback.html" + \
                            "&response_type=id_token%20token&scope=openid%20profile%20magister.ecs.legacy%20" + \
                            "magister.mdv.broker.read%20magister.dnn.roles.read" + \
                            "&state=" + randomhash() + \
                            "&nonce=" + randomhash() + "&acr_values=tenant%3A" + self.filterName
        self.__authUrl = "https://accounts.magister.net/challenge/"
        self.__accountUrl = "https://accounts.magister.net"
        self.userProfile = {}
        self.userId = 0

        # start session
        self.__s = requests.Session()

        # get authorizeUrl
        r = self.__s.get(self.authorizeUrl, allow_redirects=False)

        if r.status_code != 302:
            raise RuntimeError("ReturnUrl error " + str(r.status_code))

        self.__returnUrl = unquote(r.headers['Location'].split("returnUrl=")[1])

        r2 = self.__s.get(r.headers['Location'], allow_redirects=False)
        if r2.status_code != 302:
            raise RuntimeError("SessionId error " + str(r2.status_code))

        self.__sessionId = r2.headers['Location'] \
            .split("?")[1] \
            .split("&")[0] \
            .split("=")[1]

        # get xsrf
        self.__xsrf = r2.headers['Set-Cookie'].split("XSRF-TOKEN=")[1].split(";")[0]

        # prepare data
        data = {
            "sessionId": self.__sessionId,
            "returnUrl": self.__returnUrl,
            "username": self.username
        }

        # prapare headers
        headers = {
            "X-XSRF-TOKEN": self.__xsrf
        }

        # post username
        r3 = self.__s.post(self.__authUrl + "username", json=data, headers=headers)
        if r3.status_code != 200:
            raise RuntimeError("Username error " + str(r3.status_code))

        # post password
        data = {
            "sessionId": self.__sessionId,
            "returnUrl": self.__returnUrl,
            "password": self.password
        }

        r4 = self.__s.post(self.__authUrl + "password", json=data, headers=headers)
        if r4.status_code != 200:
            raise RuntimeError("Password error " + str(r4.status_code))

        r5 = self.__s.get(self.__accountUrl + self.__returnUrl, headers=headers, allow_redirects=False)
        if r5.status_code != 302:
            raise RuntimeError("BearerToken error " + str(r5.status_code))

        self.__bearerToken = r5.headers["Location"].split("&access_token=")[1].split("&")[0]

        # set headers to use everywhere!
        self.__headers = {
            "Authorization": "Bearer " + self.__bearerToken,
            "X-XSRF-TOKEN": self.__xsrf
        }

    def profileinfo(self):
        """ this function retrieves the users profile. """
        # todo error handling
        # todo do we need this in the future for the Persoon Id?

        r = self.__s.get(self.school + "/api/account?noCache=0", headers=self.__headers)

        self.userProfile = json.loads(r.text)
        self.userId = self.userProfile["Persoon"]["Id"]

        return self.userProfile

    def getstudentbyname(self, studentname):
        """ this function retrieves the search result of a student name """
        # todo error handling
        r = self.__s.get(self.school + "/api/leerlingen/zoeken?q=" + studentname + "&top=40&skip=0",
                         headers=self.__headers)

        response = json.loads(r.text)
        if response["items"]:
            return response["items"]
        else:
            return False

    def gettodaylessonid(self):
        """ this function retrieves today lesson ids """
        # todo error handling
        today = str(datetime.date.today())
        idlist = []

        if self.userId == 0:
            # when no id, get the id from the profile
            self.profileinfo()

        r = self.__s.get(self.school + "/api/medewerkers/" + str(self.userId) +
                         "/afspraken?begin=" + today + "&einde=" + today + "&status=actief", headers=self.__headers)

        response = json.loads(r.text)
        if len(response["items"]) > 0:
            for i in response["items"]:
                idlist.append(i["id"])

            return idlist
        else:
            return False

    def setstudentreason(self, personid, hourid, reasonid):
        """ this function sets the reason for a person on a certain day """
        if not isinstance(reasonid, Reason):
            raise TypeError('reasonid must be an instance of Reason Enum')

        if self.userId == 0:
            # when no id, get the id from the profile
            self.profileinfo()

        data = {
            "persoonId": personid,
            "redenId": reasonid.value
        }

        r = self.__s.post("https://novacollege.magister.net/api/medewerkers/afspraken/" + str(hourid) +
                          "/verantwoordingen", headers=self.__headers, json=data)

        if r.status_code == 204:
            return True
        else:
            return False


m = Magister("https://novacollege.magister.net", "hlw1404", getpass("Password: "))
print(m.profileinfo())

