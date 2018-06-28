from flask import Flask, render_template, json, request
import MySQLdb
import datetime

app = Flask(__name__)

@app.route('/')
@app.route('/search')
def search_page():
    return render_template("search.html")

@app.route('/search', methods=['GET', 'POST'])
def input():
    conn=MySQLdb.connect(user="root", host="localhost", db="saleinf")
    cursor = conn.cursor()
    try:
        username = request.form['username']
        date1    = request.form['date1']
        date2    = request.form['date2']


        if username or date1 or date2:
            cursor.execute('select id_user from users where user_name= "{!s}"'.format(username))
            idu    = cursor.fetchone()
            cursor.execute('select id_account from orders where date_soldon BETWEEN "{!s}" AND "{!s}"'.format(date1, date2))
            idacc  = cursor.fetchone()
        ## only username input
            if username and not(date1 or date2):
                cursor.execute('select id_user from users where user_name= "{!s}"'.format(username))
                iduser = cursor.fetchone()
                if iduser:
                    cursor.execute('select * from users, accounts, orders where users.id_user=accounts.id_user AND accounts.id_account=orders.id_account AND users.user_name= "{!s}"'.format(username))
                    conn.commit()
                    return render_template('search_result.html', users=cursor.fetchall())
                else:
                    return "No user found"
        ## only dates input
            elif date1 and date2 and not username:
                if idacc:
                    cursor.execute('select * from users, accounts, orders where users.id_user=accounts.id_user AND accounts.id_account=orders.id_account AND orders.date_soldon BETWEEN "{!s}" AND "{!s}"'.format(date1, date2))
                    conn.commit()
                    return render_template('search_result.html', users=cursor.fetchall())
                else:
                    return "No records in this date range found"
        ## username and dates input
            elif username and date1 and date2:
                cursor.execute('select id_user from users where user_name="{!s}"'.format(username))
                iduser = cursor.fetchone()
                if iduser and idacc:
                    cursor.execute('select * from users, accounts, orders where users.id_user=accounts.id_user AND accounts.id_account=orders.id_account AND users.user_name= "{!s}" AND orders.date_soldon BETWEEN "{!s}" AND "{!s}"'.format(username, date1, date2))
                    conn.commit()
                    return render_template('search_result.html', users=cursor.fetchall())
                else:
                    return "No user in this date range found"
        else:
            return "Please enter the required fields"

    finally:
      cursor.close()
      conn.close()


    

if __name__ == "__main__":
    app.run(debug=True, port=5000)
