from flask import Flask, render_template, json, request, url_for, redirect
import MySQLdb
import cx_Oracle
import base64


app = Flask(__name__)


#Index 
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/add-sale', methods=['GET', 'POST'])
def input():
    conn=MySQLdb.connect("localhost", "root", base64.b64decode("Mi10"), "Ra_sales")
    cursor = conn.cursor()
    try:
        date_soldon       = request.form['soldondate']
        departmentaccount = request.form['departmentaccount']
        subaccount        = request.form['subaccount']
        username          = request.form['username']
        emailextension    = request.form['emailList']
        email             = username +'@'+ emailextension
        itemtitle         = request.form['title'] #drop-down menu
        itemtype          = request.form['itemtypes'] #Radio Button
        salestype         = "RA" #by default                    
        objectcode        = request.form['objectcode'] 
        subobjcode        = request.form['subobjcode']
        formnumber        = request.form['formnumber']
        price             = request.form['unit_price']
        quantity          = request.form['amount']
        total             = request.form['total_price']
        
        # validate the received values

        if date_soldon and username and departmentaccount and email and objectcode and itemtype and salestype and itemtitle and subobjcode and formnumber and price and quantity and total:        

            
            # All Good, let's call MySQL
            cursor.execute('select ID_USER from users WHERE user_name = %s AND email = %s', (username,email))
            userid  = cursor.fetchone()
            cursor.execute('select ID_ACCOUNT from accounts WHERE account_number = %s AND sub_account = %s', (departmentaccount,subaccount))
            accid   = cursor.fetchone()
            cursor.execute('select max(id_account) from accounts')
            maxid   = cursor.fetchone()
            if not userid and not accid:
                cursor.execute('insert into users (user_name, email) values (%s, %s) ',
                               (username,email))
                cursor.execute('insert into accounts (account_number, sub_account, id_user, id_account) values (%s, %s, LAST_INSERT_ID(), LAST_INSERT_ID())',
                               (departmentaccount,subaccount))
                cursor.execute('insert into orders (date_soldon, item_title, obj_code, sub_objcode, item_type, sales_type,  quantity, price_per_copy, total_cost, id_acc_auto, formnumber) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, LAST_INSERT_ID(), %s)',
                               (date_soldon, itemtitle, objectcode, subobjcode, itemtype, salestype, quantity, price, total, formnumber))
            elif userid and accid:
		cursor.execute('insert into accounts (account_number, sub_account, id_user, id_account) values (%s, %s, %s, %s)',
                               (departmentaccount,subaccount, userid, accid))
                cursor.execute('insert into orders (date_soldon, item_title, obj_code, sub_objcode, item_type, sales_type, quantity, price_per_copy, total_cost, id_acc_auto, formnumber) values (%s, %s, %s, %s, %s, %s, %s,  %s, %s, LAST_INSERT_ID(), %s)',
				(date_soldon, itemtitle, objectcode, subobjcode, itemtype, salestype, quantity, price, total, formnumber))
            elif not userid and accid:
                cursor.execute('insert into users (user_name, email) values (%s, %s) ',
                               (username,email))
		cursor.execute('insert into accounts (account_number, sub_account, id_account, id_user) values (%s, %s, %s, LAST_INSERT_ID())',
			       (departmentaccount, subaccount, accid))
                cursor.execute('insert into orders (date_soldon, item_title, obj_code, sub_objcode, item_type, sales_type, quantity, price_per_copy, total_cost, id_acc_auto, formnumber) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, LAST_INSERT_ID(), %s)',
                               (date_soldon, itemtitle, objectcode, subobjcode, itemtype, salestype, quantity, price, total, formnumber))
            else: #if userid and not accid
                cursor.execute('insert into accounts (account_number, sub_account, id_user, id_account) values (%s, %s, %s, %s+1)',
                               (departmentaccount,subaccount,userid, maxid))
                cursor.execute('insert into orders (date_soldon, item_title, obj_code, sub_objcode, item_type, sales_type, quantity, price_per_copy, total_cost, id_acc_auto, formnumber) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, LAST_INSERT_ID(), %s)',
                               (date_soldon, itemtitle, objectcode, subobjcode, itemtype, salestype, quantity, price, total, formnumber))
            new_id = cursor.lastrowid
            conn.commit() #submit and save data
            return render_template('success.html', id=new_id)

        else:
            return "Please enter the required fields" 

    finally:
        cursor.close()
        conn.close()

#Search        
@app.route('/search')
def search_page():
    return render_template("search.html")

@app.route('/search', methods=['GET', 'POST'])
def search():
    conn=MySQLdb.connect("localhost", "root", base64.b64decode("Mi10"), "Ra_sales")
    cursor = conn.cursor()
    try:
        username = request.form['username']
        date1    = request.form['date1']
        date2    = request.form['date2']
        software = request.form['software']


        if username or software or date1 or date2:
            cursor.execute('select id_user from users where user_name= "{!s}"'.format(username))
            idu    = cursor.fetchone()
            cursor.execute('select id_order from orders where item_title= "{!s}"'.format(software))
            ids   = cursor.fetchone()
            cursor.execute('select id_acc_auto from orders where date_soldon BETWEEN "{!s}" AND "{!s}"'.format(date1, date2))
            idacc  = cursor.fetchone()
        ## only username input
            if username and not(software or date1 or date2):
                cursor.execute('select id_user from users where user_name= "{!s}"'.format(username))
                iduser = cursor.fetchone()
                if iduser:
                    cursor.execute('select * from users, accounts, orders where users.id_user=accounts.id_user AND accounts.id_acc_auto=orders.id_acc_auto AND users.user_name= "{!s}"'.format(username))
                    conn.commit()
                    return render_template('search_result.html', users= cursor.fetchall())
                else:
                    return "No user found"
        ## only dates input
            elif date1 and date2 and not (username or software):
                if idacc:
                    cursor.execute('select * from users, accounts, orders where users.id_user=accounts.id_user AND accounts.id_acc_auto=orders.id_acc_auto AND orders.date_soldon BETWEEN "{!s}" AND "{!s}"'.format(date1, date2))
                    conn.commit()
                    return render_template('search_result.html', users = cursor.fetchall())
                else:
                    return "No records in this date range found"
        ## only software input
            elif software and not (date1 or date2 or username):
                if ids:
                    cursor.execute('select * from users, accounts, orders where users.id_user=accounts.id_user AND accounts.id_acc_auto=orders.id_acc_auto AND orders.item_title= "{!s}"'.format(software))
                    conn.commit()
                    return render_template('search_result.html', users = cursor.fetchall())
                else:
                    return "No records for this product"                
        ## username and dates input
            elif username and date1 and date2:
                if idu and idacc:
                    cursor.execute('select * from users, accounts, orders where users.id_user=accounts.id_user AND accounts.id_acc_auto=orders.id_acc_auto AND users.user_name= "{!s}" AND orders.date_soldon BETWEEN "{!s}" AND "{!s}"'.format(username, date1, date2))
                    conn.commit()
                    return render_template('search_result.html', users = cursor.fetchall())
                else:
                    return "No user in this date range found"
        ## username and software input
            elif username and software:
                if idu and ids:
                    cursor.execute('select * from users, accounts, orders where users.id_user=accounts.id_user AND accounts.id_acc_auto=orders.id_acc_auto AND users.user_name= "{!s}" AND orders.item_title= "{!s}"'.format(username, software))
                    conn.commit()
                    return render_template('search_result.html', users = cursor.fetchall())
                else:
                    return "This user did not purchase this product"
        ## software and datas input
            elif software and date1 and date2:
                if ids and idacc:
                    cursor.execute('select * from users, accounts, orders where users.id_user=accounts.id_user AND accounts.id_acc_auto=orders.id_acc_auto AND orders.item_title= "{!s}" AND orders.date_soldon BETWEEN "{!s}" AND "{!s}"'.format(software, date1, date2))
                    conn.commit()
                    return render_template('search_result.html', users = cursor.fetchall())
                else:
                    return "No records found in this date range for this product"
        ## all input
            elif username and software and date1 and date2:
                if idu and idacc and ids:
                    cursor.execute('select * from users, accounts, orders where users.id_user=accounts.id_user AND accounts.id_acc_auto=orders.id_acc_auto AND users.user_name= "{!s}" AND orders.item_title= "{!s}" AND orders.date_soldon BETWEEN "{!s}" AND "{!s}"'.format(username, software, date1, date2))
                    conn.commit()
                    return render_template('search_result.html', users = cursor.fetchall())
                else:
                    return "No records found"
        ## nothing input
        else:
            return "Please enter the required fields"

    finally:
      cursor.close()
      conn.close()


#Export
@app.route('/export')
def export_page():
    return render_template('export.html')

@app.route('/export', methods=['GET', 'POST'])
def export():
    conn=MySQLdb.connect("localhost", "root", base64.b64decode("Mi10"), "Ra_sales")
    cursor = conn.cursor()
    try:
        username = request.form['username']
        date1    = request.form['date1']
        date2    = request.form['date2']
        software = request.form['software']


        if username or software or date1 or date2:
            cursor.execute('select id_user from users where user_name= "{!s}"'.format(username))
            idu    = cursor.fetchone()
            cursor.execute('select id_order from orders where item_title= "{!s}"'.format(software))
            ids   = cursor.fetchone()
            cursor.execute('select id_acc_auto from orders where date_soldon BETWEEN "{!s}" AND "{!s}"'.format(date1, date2))
            idacc  = cursor.fetchone()
        ## only username input
            if username and not(software or date1 or date2):
                cursor.execute('select id_user from users where user_name= "{!s}"'.format(username))
                iduser = cursor.fetchone()
                if iduser:
                    cursor.execute('select * from users, accounts, orders where users.id_user=accounts.id_user AND accounts.id_acc_auto=orders.id_acc_auto AND users.user_name= "{!s}"\
                                    INTO OUTFILE "/home/wsang/statmathsales/charges/export.csv" FIELDS TERMINATED BY "," LINES TERMINATED BY "\n"'.format(username))
                    conn.commit()
                    return render_template('export_success.html')
                else:
                    return "No user found"
        ## only dates input
            elif date1 and date2 and not (username or software):
                if idacc:
                    cursor.execute('select * from users, accounts, orders where users.id_user=accounts.id_user AND accounts.id_acc_auto=orders.id_acc_auto AND orders.date_soldon BETWEEN "{!s}" AND "{!s}"\
                                    INTO OUTFILE "/home/wsang/statmathsales/charges/export.csv" FIELDS TERMINATED BY "," LINES TERMINATED BY "\n"'.format(date1, date2))
                    conn.commit()
                    return render_template('export_success.html')
                else:
                    return "No records in this date range found"
        ## only software input
            elif software and not (date1 or date2 or username):
                if ids:
                    cursor.execute('select * from users, accounts, orders where users.id_user=accounts.id_user AND accounts.id_acc_auto=orders.id_acc_auto AND orders.item_title= "{!s}"\
                                    INTO OUTFILE "home/wsang/statmathsales/charges/export.csv" FIELDS TERMINATED BY "," LINES TERMINATED BY "\n"'.format(software))
                    conn.commit()
                    return render_template('export_success.html')
                else:
                    return "No records for this product"                
        ## username and dates input
            elif username and date1 and date2:
                if idu and idacc:
                    cursor.execute('select * from users, accounts, orders where users.id_user=accounts.id_user AND accounts.id_acc_auto=orders.id_acc_auto AND users.user_name= "{!s}" \
                                    AND orders.date_soldon BETWEEN "{!s}" AND "{!s}"\
                                    INTO OUTFILE "/var/www/statmathsales/reports/export.csv" FIELDS TERMINATED BY "," LINES TERMINATED BY "\n"'.format(username, date1, date2))
                    conn.commit()
                    return render_template('export_success.html')
                else:
                    return "No user in this date range found"
        ## username and software input
            elif username and software:
                if idu and ids:
                    cursor.execute('select * from users, accounts, orders where users.id_user=accounts.id_user AND accounts.id_acc_auto=orders.id_acc_auto AND users.user_name= "{!s}" \
                                    AND orders.item_title= "{!s}"\
                                    INTO OUTFILE "/var/www/statmathsales/reports/export.csv" FIELDS TERMINATED BY "," LINES TERMINATED BY "\n"'.format(username, software))
                    conn.commit()
                    return render_template('export_success.html')
                else:
                    return "This user did not purchase this product"
        ## software and datas input
            elif software and date1 and date2:
                if ids and idacc:
                    cursor.execute('select * from users, accounts, orders where users.id_user=accounts.id_user AND accounts.id_acc_auto=orders.id_acc_auto AND orders.item_title= "{!s}" \
                                    AND orders.date_soldon BETWEEN "{!s}" AND "{!s}"\
                                    INTO OUTFILE "/var/www/statmathsales/reports/export.csv" FIELDS TERMINATED BY "," LINES TERMINATED BY "\n"'.format(software, date1, date2))
                    conn.commit()
                    return render_template('export_success.html')
                else:
                    return "No records found in this date range for this product"
        ## all input
            elif username and software and date1 and date2:
                if idu and idacc and ids:
                    cursor.execute('select * from users, accounts, orders where users.id_user=accounts.id_user AND accounts.id_acc_auto=orders.id_acc_auto AND users.user_name= "{!s}" \
                                    AND orders.item_title= "{!s}" AND orders.date_soldon BETWEEN "{!s}" AND "{!s}"\
                                    INTO OUTFILE "/var/www/statmathsales/reports/export.csv" FIELDS TERMINATED BY ","  LINES TERMINATED BY "\n"'.format(username, software, date1, date2))
                    conn.commit()
                    return render_template('export_success.html')
                else:
                    return "No records found"
        ## nothing input
        else:
            return "Please enter the required fields"

    finally:
      cursor.close()
      conn.close()







#validate
@app.route('/validate')
def validate_page():
    return render_template("validate.html")

#select account numbers
@app.route('/validate', methods=['GET', 'POST'])
def validate():   

    conn   = cx_Oracle.connect('hpastats', base64.b64decode('a2'), 
                                'esdbd100.uits.indiana.edu')
    cursor = conn.cursor ()

    try:
        acc = request.values['accounts']

	if acc:
            a = acc.splitlines()
            options = []
            for query in a:
                thing = query.split()
                if len(thing) == 2:
                    nbr = query.split()[0]
                    sub = query.split()[1]
                    cursor.execute("select * from DSS_KFS.CA_SUBACCT_GT where ACCOUNT_NBR= '{!s}' and SUB_ACCT_NBR= '{!s}'".format(nbr, sub))
                elif len(thing) == 1:
                    nbr = query.split()[0]
                    cursor.execute("select * from DSS_KFS.CA_SUBACCT_GT where ACCOUNT_NBR= '{!s}'".format(nbr))
                for row in cursor.fetchall():
                    options.append(row)
                conn.commit()
            return render_template('vali_result.html', accounts=options)
	else:
	    return "Please fill in required field"



    finally:
      cursor.close()
      conn.close()

if __name__ == "__main__":
    app.run(debug=True, port=80)


