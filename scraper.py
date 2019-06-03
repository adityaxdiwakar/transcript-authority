import re as regex
import smtplib
import os

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from shutil import copyfile

from dotenv import load_dotenv

import urllib.request
import mechanicalsoup

import PyPDF2
import requests

load_dotenv()

try: 
    os.remove("/home/tAuth/report.pdf")
except:
    pass

browser = mechanicalsoup.StatefulBrowser()

username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")

url = f"https://campus.forsyth.k12.ga.us/campus/verify.jsp?appName=forsyth&screen=&username={username}&password={password}%21&x=0&y=0&useCSRFProtection=true"

browser.open(url)

url = os.getenv("T_LINK") 

response = browser.open(url)

with open('/home/tAuth/report.pdf', 'wb') as f:
    f.write(response.content)

files = os.listdir("/home/tAuth/backups/")
max = 0
for i in range(len(files)):
    if int(regex.findall(r'\d+', files[i])[0]) > max:
        max = int(regex.findall(r'\d+', files[i])[0])
    if int(regex.findall(r'\d+', files[i])[0]) > 10:
        try:
            os.remove("/home/tAuth/backups/report_" + str(int(regex.findall(r'\d+', files[i])[0]) - 100) + ".pdf")
        except:
            pass
fName = max+1

pdfFileObj = open('/home/tAuth/report.pdf', 'rb') 
pdfReader = PyPDF2.PdfFileReader(pdfFileObj) 
pageObj = pdfReader.getPage(0).extractText()
classRank = (regex.findall('ClassRank\s+[0-9]+of[0-9]+', pageObj)[0]).split("\n")[1]
gpa = regex.findall('CumulativeGPA+\s\(Weighted\)[0-9].[0-9][0-9][0-9]', pageObj)[0].split(")")[1]
pdfFileObj.close() 

print(classRank, gpa)

case = 0
f = open("/home/tAuth/ois", "r")
oldInfo = f.readline().split(",")
info = [classRank, gpa]
if oldInfo != info:
    f = open("/home/tAuth/ois", "w")
    copyfile("/home/tAuth/report.pdf", "/home/tAuth/backups/report_" + str(fName) + ".pdf")
    a = open("log", "a")
    f.write(info[0] + "," + info[1])
    a.write(info[0] + "," + info[1])
    a.write("\n")
    case = 1

if case == 1:
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()

    user = os.getenv("EMAIL")
    pw = os.getenv("EMAIL_PASSWORD")
    sendTo = os.getenv("TO_EMAIL")

    msg = MIMEMultipart()
    msg['From'] = "Transcript Alert"
    msg['To'] = sendTo
    msg['Subject'] = '[CRITICAL] Change in Transcript (GPA Delta Detected)'

    html = """\
    <html>
    <head></head>
    <body>
        <h2>Transcript has been updated!</h2>
        <p>
        Below you can find the changes made in the transcripts:
        </p>
    </body>
    </html>
    """

    part = MIMEBase('application', "octet-stream")
    part.set_payload(open("/home/tAuth/report.pdf", "rb").read())
    encoders.encode_base64(part)

    part.add_header('Content-Disposition', 'attachment; filename="report.pdf"')

    msg.attach(MIMEText(html, 'html'))
    msg.attach(part)

    server.login(user, pw)
    server.sendmail(user, sendTo, msg.as_string())
