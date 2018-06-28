from flask import Flask, render_template, json, request, url_for, redirect
import MySQLdb



app = Flask(__name__)
#Index
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/add-sale', methods=['GET', 'POST'])
def input():
    conn=MySQLdb.connect(user="root", host="localhost", db="saleinf")
    cursor = conn.cursor()
    try:
        date_soldon = request.form['soldondate']
        departmentaccount = request.form['departmentaccount']
        subaccount = request.form['subaccount']
        username = request.form['username']
        email = request.form['email']
        software = request.form['softwareList'] #drop-down menu
        itemtype = request.form['itemtypes'] #Radio Button                                      
        objectcode = request.form['objectcode'] #Radio Button 
        subobjcode = request.form['subobjcode']
        price = request.form['unit_price']
        quantity = request.form['amount']
        total = request.form['total_price']
        
        # validate the received values

        if date_soldon and username and departmentaccount and subaccount and email and objectcode and itemtype and software and subobjcode and price and quantity and total:        

            
            # All Good, let's call MySQL
            cursor.execute('select ID_USER from users WHERE user_name = %s AND email = %s', (username,email))
            userid = cursor.fetchone()
            cursor.execute('select ID_ACCOUNT from accounts WHERE account_number = %s AND sub_account = %s', (departmentaccount,subaccount))
            accid = cursor.fetchone()
            if not userid and not accid:
                cursor.execute('insert into users (user_name, email) values (%s, %s) ',(username,email))
                cursor.execute('insert into accounts (account_number, sub_account, id_user) values (%s, %s, LAST_INSERT_ID())',
                               (departmentaccount,subaccount))
                cursor.execute('insert into orders (date_soldon, item_title, obj_code, sub_objcode, item_type, quantity, price_per_copy, total_cost, id_account) values (%s, %s, %s, %s, %s, %s, %s, %s, LAST_INSERT_ID())',
                           (date_soldon, software, objectcode, subobjcode, itemtype, quantity, price, total))
            elif userid and accid:
                cursor.execute('insert into orders (date_soldon, item_title, obj_code, sub_objcode, item_type, quantity, price_per_copy, total_cost, id_account) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)',
                           (date_soldon, software, objectcode, subobjcode, itemtype, quantity, price, total, accid))
            elif not userid and accid:
                cursor.execute('insert into users (user_name, email) values (%s, %s) ',(username,email))
                cursor.execute('insert into orders (date_soldon, item_title, obj_code, sub_objcode, item_type, quantity, price_per_copy, total_cost, id_account) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)',
                           (date_soldon, software, objectcode, subobjcode, itemtype, quantity, price, total, accid))
            else: #if userid and not accid
                cursor.execute('insert into accounts (account_number, sub_account, id_user) values (%s, %s, %s)',(departmentaccount,subaccount,userid))
                cursor.execute('insert into orders (date_soldon, item_title, obj_code, sub_objcode, item_type, quantity, price_per_copy, total_cost, id_account) values (%s, %s, %s, %s, %s, %s, %s, %s, LAST_INSERT_ID())',
                           (date_soldon, software, objectcode, subobjcode, itemtype, quantity, price, total))
            new_id = cursor.lastrowid
            conn.commit() #submit and save data
            return render_template('success.html', id=new_id)

        else:
            return "Please enter the required fields" 

##    except Exception as e:
##        return json.dumps({'error':str(e)})
    finally:
        cursor.close()
        conn.close()

#Search        
@app.route('/search')
def search_page():
    return render_template("search.html")

@app.route('/search', methods=['GET', 'POST'])
def search():
    conn=MySQLdb.connect(user="root", host="localhost", db="saleinf")
    cursor = conn.cursor()
    try:
        username = request.form['username']
        if username:
            cursor.execute('select id_user from users where user_name="{!s}"'.format(username))
            iduser = cursor.fetchone()
            if iduser:
                cursor.execute('select * from users, accounts, orders where users.id_user=accounts.id_user AND accounts.id_account=orders.id_account AND users.user_name= "{!s}"'.format(username))
                conn.commit()
                return render_template('search_result.html', users=cursor.fetchall())
            else:
                return "No users found"
        else:
            return "Please enter the required fields"

    finally:
      cursor.close()
      conn.close()

      
@app.route('/show_users')
def show_users():
    try:
        conn=MySQLdb.connect(user="root", host="localhost", db="saleinf")
        cursor = conn.cursor()
        cursor.execute('select user_name, account_number from users')
        return render_template('show_users.html', users=cursor.fetchall())

##    except Exception as e:
##        return json.dumps({'error':str(e)})
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    app.run(debug=True, port=80)



