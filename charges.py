import MySQLdb as dbapi
import cx_Oracle
import sys
import os
import glob
import csv
import base64
import smtplib
import time
from datetime import datetime, timedelta


##name the file
daypoint1  = datetime.now() - timedelta(days=7)  #last week today
day1       = daypoint1.strftime('%Y-%m-%d') #end
daypoint2  = datetime.now()  #today
day2       = daypoint2.strftime('%Y-%m-%d') #start
name_str   = 'RACharges_' + daypoint1.strftime('%m%d%y') + '-' + daypoint2.strftime('%m%d%y') #show only date
csvname    = name_str + '.csv'
csvpath    = '/var/www/statmathsales/charges/' +  csvname


print day1
print day2
print csvpath

dbServer='localhost'
dbSchema='Ra_sales'
dbUser='root'
dbPass=base64.b64decode('Mi10')

db=dbapi.connect(host=dbServer, user=dbUser, db=dbSchema, passwd=dbPass)
cursor     =  db.cursor()

dbQueryChk = '(SELECT id_order FROM orders WHERE date_soldon BETWEEN %s AND %s);'
dbQuery    = '(SELECT "charge form", "date", "buyer", "email", "account", "sub-account", "obj code", "sub obj", "units", "amount", "description")\
               UNION ALL\
              (SELECT orders.formnumber, orders.date_soldon, users.user_name, users.email, \
                      accounts.account_number, accounts.sub_account, \
                      orders.obj_code, sub_objcode, quantity, total_cost, item_title\
               FROM users, accounts, orders\
               WHERE users.id_user = accounts.id_user and accounts.id_acc_auto=orders.id_acc_auto and date_soldon BETWEEN %s AND %s\
               AND orders.sales_type = "RA" \
               ORDER BY users.id_user ASC, accounts.id_acc_auto ASC);'



cursor.execute(dbQueryChk, (day1, day2))      
ChkResult  =  cursor.fetchall()

##Check new entries
if len(ChkResult) == 0:
    print  "No new entries"
else:
    cursor.execute(dbQuery, (day1, day2))
    result    =  cursor.fetchall()
    print "New entries found"

f = open(csvpath,"wb")
c = csv.writer(f)
for row in result:
    c.writerow(row)
f.close()                  #close the csv to sent as attachment (highly important)
with open(csvpath) as ff:
    headerline = ff.next()
    total = 0
    for row in csv.reader(ff):
        total += int(row[9])

with open(csvpath,'a') as fff:
    cc = csv.writer(fff)
    amount = str(total)
    dollar = '$ ' + amount
    field  = [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', dollar] #target the cell
    cc.writerow(field)
    cc.writerow(['NOTE:'])
    cc.writerow(['Chart - UA'])
    cc.writerow(['Account - 66-101-08'])
    cc.writerow(['sub-account - smsal'])
    cc.writerow(['IGNORE ITEM COLUMN'])
        
print "Data has been successfully written in a CSV file!"


##Wait for 10 sec
time.sleep(10)

##Check cvs file
if len(ChkResult) != 0:
    filename = csvname
    filepath = csvpath
else:
    print "There is no file to send."

# Read the file
fo             = open(filepath, "rb")
filecontent    = fo.read()
fo.close()

sender   = 'smsale@iu.edu'
reciever = 'finance@iu.edu'
marker   = "AUNIQUEMARKER"

body     ="""
This is the weekly report of software sale information from Research Analytics.
The excel report is attached to thie email for review.
If you have questions please reply to this email or direct your questions to John Smith at jsmith@indiana.edu.
"""

# Define the main headers.
part1    = """From: Research Analytics <researchanalytics@iu.edu>
To: Finance Office <finance@iu.com>
Subject: Weekly software sales report
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary=%s
--%s
""" % (marker, marker)

# Define the message action
part2    = """Content-Type: text/plain
Content-Transfer-Encoding:8bit

%s
--%s
""" % (body,marker)

# Define the attachment section
part3    = """Content-Type: multipart/mixed; name=\"%s\"
#Content-Transfer-Encoding:base64
Content-Disposition: attachment; filename=%s

%s
--%s--
""" %(filename, filename, filecontent, marker)
message    = part1 + part2 + part3

try:
   smtpObj = smtplib.SMTP('mail-relay.iu.edu')
   smtpObj.sendmail(sender, reciever, message)
   print "Successfully sent email"
except Exception:
   print "Error: unable to send email"

os.remove(filepath)
print "File is removed."
