from getpass import getpass
from docent import Docent
from student import Student

m = Student("https://novacollege.magister.net", "hlw1404", getpass("Password: "))

print(m.set_studentaanwezig(181617))
