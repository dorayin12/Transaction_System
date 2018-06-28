from flask import Flask, render_template, json, request
import MySQLdb
app = Flask(__name__)

@app.route('/')
@app.route('/delete')
def search_page():
    return render_template("search_result.html")

@app.route('/delete', methods=['GET', 'POST'])
def input():
    conn=MySQLdb.connect(user="root", host="localhost", db="saleinf")
    cursor = conn.cursor()
    try:
        userid = request.form['userid']
        if username:
            cursor.execute=('delete from users where id_user="%s"', (userid))
            conn.commit()
            return: "You have successfully deleted one record"
        else:
            return: "Please enter the required fields"

    finally:
      cursor.close()
      conn.close()


    

if __name__ == "__main__":
    app.run(debug=True, port=5000)
