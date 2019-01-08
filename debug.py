from getpass import getpass
from docent import Docent

m = Docent("https://novacollege.magister.net", "hlw1404", getpass("Password: "))

print(m.get_afsprakenvandaag())