import time, schedule
import MySQLdb as dbapi
import sys
import csv


def export():
    dbServer='localhost'
    dbSchema='saleinf'
    dbUser='root'
    dbPass=''

    dbQuery = '(SELECT "Uer_ID", "Username", "Email", "Account_ID", "Account", "Sub_Account", "Order_ID", "Date_Soldon", "Date_Entered", "Object Code", "Sub ObjectCode", "Item", "Type", "Quantity", "Price", "Total")\
               UNION ALL\
               (SELECT users.id_user, user_name, email, accounts.id_account, account_number, sub_account, \
                      id_order, date_soldon, date_entered, obj_code, sub_objcode, item_title, item_type, quantity, price_per_copy,total_cost \
               FROM saleinf.users, saleinf.accounts, saleinf.orders\
               WHERE users.id_user = accounts.id_user and accounts.id_account=orders.id_account\
               and WEEKOFYEAR(date_entered)=WEEKOFYEAR(NOW())\
               ORDER BY users.id_user ASC, accounts.id_account ASC);' #ORDER DOESN'T WORK HERE


    db=dbapi.connect(host=dbServer,user=dbUser, passwd=dbPass)
    cursor=db.cursor()
    cursor.execute(dbQuery)      
    result=cursor.fetchall()

    c = csv.writer(open("C:/Users/wsang/Desktop/temp.csv","wb"))
##    num_fields = len(cursor.description)
##    field_names = [i[0] for i in cursor.description]
    for row in result:
        c.writerow(row)

schedule.every(1).minutes.do(export)
##schedule.every().hour.do(job)
##schedule.every().day.at("10:30").do(job)
##schedule.every().monday.do(job)
##schedule.every().wednesday.at("13:15").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
