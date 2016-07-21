import csv
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, jsonify


app = Flask(__name__)
app.config.from_object(__name__)

# app.config.update(dict(
#     DATABASE=os.path.join(app.root_path, 'NPSDATA.db'),
#     SECRET_KEY='development key',
#     USERNAME='admin',
#     PASSWORD='default'
# ))

DATABASE2 = "NPSDATA.db"

@app.before_request
def before_request():
    g.db = sqlite3.connect(DATABASE2)

@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/data")
def data():
    return jsonify(get_data())

@app.route('/spanData')
def spanData():
    return jsonify(get_span())

@app.route('/grain')
def grain():
    return render_template('grain.html')

@app.route("/timeline/")
def after():
    return render_template('timeline.html')

@app.route("/span/")
def span():
    return render_template("span.html")

@app.route("/addrec", methods=['POST'])
def addrec():
    if request.method == 'POST':
            name = request.form['name']
            state = request.form['state']
            desig = request.form['designation']
            desig2 = desig
            date = request.form['date']
            meta = request.form['meta']
            cur = g.db.cursor()
            cur.execute("INSERT INTO timelineNPS2 VALUES (?, ?, ?, ?, ?, ?, ?)", (dateformat(date), name, desig, state, desig2, 'false', meta) )
            g.db.commit()
    # return render_template('timeline.html')
    return redirect(url_for('after'))

@app.route("/rmrec", methods=['POST'])
def rmrec():
    if request.method == 'POST':
        name = request.form['name']
        curr = g.db.cursor()
        print name
        curr.execute('DELETE FROM timelineNPS2 WHERE content=?', (name,))
        g.db.commit()
    return render_template('timeline.html')

@app.route("/editrec", methods=['POST'])
def editrec():
    if request.method == 'POST':
        name = request.form['name']
        state = request.form['state']
        day = request.form['date']
        origname = request.form['origName']
        imp = request.form['important']
        meta = request.form['meta']
        cur3 = g.db.cursor()
        cur3.execute("UPDATE timelineNPS2 SET content=?, subGroup=?, start=?, metadata=? WHERE content=?", (name, state, dateformat(day), meta, origname))
        cur3.execute("UPDATE timelineNPS2 SET important=? WHERE content=?", (imp, name))
        g.db.commit()
    return render_template('timeline.html')


def get_data():
    cur2 = g.db.cursor()
    rows = cur2.execute("SELECT * FROM timelineNPS2").fetchall()
    RESULTS = []
    for i in rows:
        RESULTS.append({
            'start': i[0],
            'content': i[1],
            'className': i[2],
            'subGroup': i[3],
            'group' : i[4],
            'important' : i[5],
            'metadata' : i[6]

        })
    return RESULTS

def get_span():
    curv = g.db.cursor()
    rows = curv.execute("SELECT * FROM spandata").fetchall()
    result = []
    for i in rows:
        result.append({
            'id': i[0],
            'content' : i[1],
            'start' : i[2],
            'end' : i[3],
            'parent' : i[4],
            'className' : i[5]
        })
    return result


def dateformat(date):
    year = date[:4]
    month = date[5:7]
    day = date[-2:]
    res = month + '/'+day+'/'+year
    return res



if __name__ == "__main__":
    app.run(debug=True)