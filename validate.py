from flask import Flask, render_template, json, request
import MySQLdb
import cx_Oracle

app = Flask(__name__)

@app.route('/validate')
def validate_page():
    return render_template("validate.html")

#select account numbers
@app.route('/validate', methods=['GET', 'POST'])
def validate():

    connO   = cx_Oracle.connect('hpastats','klj06mq','esdbd72.uits.indiana.edu')
    cursorO = connO.cursor ()

    try:
       acc = request.values['accounts']

       if acc:
            a = acc.splitlines()
            options = []
            for query in a:
                nbr = query.split()[0]
                sub = query.split()[1]
                cursorO.execute("select * from DSS_KFS.CA_SUBACCT_GT where ACCOUNT_NBR= '{!s}' and SUB_ACCT_NBR= '{!s}'".format(nbr, sub))
                for row in cursor.fetchall():
                    options.append(row)
                connO.commit()
            return render_template('vali_result.html', accounts=options)
       else:
            return "Please fill in required field"



    finally:
      cursorO.close()
      connO.close()
    

if __name__ == "__main__":
    app.run(debug=True, port=5000)
