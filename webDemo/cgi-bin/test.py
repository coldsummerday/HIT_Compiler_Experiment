#! /usr/bin/python3
import os

print("Content-type: text/html\r\n\r\n")
print("<font size=+1>Environment</font><\br>")
for param in os.environ.keys():
    print("<p><b>%20s</b>: %s</p>" % (param, os.environ[param]))
