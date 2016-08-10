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

@app.route("/colData/<num>/<maxD>/<minD>")
def colData(num, maxD, minD):
    return jsonify(collaspeData(maxD, minD, num))
    # return collaspeData(maxD, minD, num)

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
    return render_template('timeline.html')
    # return redirect(url_for('after'))

@app.route("/rmrec", methods=['POST'])
def rmrec():
    if request.method == 'POST':
        name = request.form['name']
        curr = g.db.cursor()
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

# @app.route("/timeline/<num>/<maxD>/<minD>")
# def collaspeData(max, min, num):
#     if(num < 20):
#         return data()
#         # print 'less than 20 items in view'
#     else:
#         cur = g.db.cursor()
#         result = [];
#         classes = cur.execute("SELECT className FROM timelineNPS2 GROUP BY className").fetchall()
#         rows = cur.execute("SELECT substr(start, -4, 4) AS year, count(*), className FROM timelineNPS2 WHERE CAST(year as integer) < ? and CAST(year as integer) > ? GROUP BY year, className", (max, min)).fetchall()
#         for c in classes:
#             cName = c[0];
#             x = len(rows)
#             i =0
#             while (i < x):
#                 if rows[i][2] == cName:
#                     content = int(rows[i][1])
#                     start = rows[i][0]
#                     end = start
#                     if i+1 < x:
#                         while int(rows[i+1][0]) - int(rows[i][0]) == 1:
#                             if rows[i+1][2] == cName:
#                                 content += int(rows[i+1][1])
#                                 end = rows[i+1][0]
#                             i += 1
#                             if not i+1 < x:
#                                 break
#                     result.append({
#                         'start': start,
#                         'content': content,
#                         'end' :end,
#                         'className' : cName
#                         })
#                 i += 1
#         return result

def collaspeData(max, min, num):
    rge = int(max) - int(min)
    cur = g.db.cursor()
    results = []
    if int(num) < 35:
        sql = cur.execute("SELECT * FROM timelineNPS2").fetchall()
        for i in sql:
            results.append({
                'start': i[0],
                'content': i[1],
                'className': i[2],
                'subGroup': i[3],
                'group' : i[4],
                'important' : i[5],
                'metadata' : i[6]
                })
    elif rge < 9:
        sql = cur.execute("SELECT substr(start, -4, 4) AS year, count(*), substr(start, 0, 3) as month, className, start FROM timelineNPS2 GROUP BY year, className, month ORDER BY className, year").fetchall()
        pName = None
        pYear = None
        pMonth = None
        start = None
        content = 0
        end = None
        contains = []
        for row in sql:
            cYear = row[0]
            cName = row[3]
            cMonth = row[2]
            cMonth = cMonth.replace('/','')
            if pYear:
                print pYear +', ' + cYear
            if pYear == None: #special case for first element
                start = row[4]
                end = start
                content = int(row[1])
                contains = []
                temp = cur.execute("SELECT content from timelineNPS2 where substr(start, -4, 4) = ? and substr(start, 0, 3) = ? and className = ?", (cYear, cMonth, cName)).fetchall()
                for r in temp:
                    contains.append(r[0])
            elif pYear == cYear: #if year is same AND feature is same
                print int(cMonth) - int(pMonth)
                if int(cMonth) - int(pMonth) == 1: #if months are sequential
                    content += int(row[1])
                    end = row[4]
                    temp = cur.execute("SELECT content from timelineNPS2 where substr(start, -4, 4) = ? and substr(start, 0, 3) = ? and className = ?", (cYear, cMonth, cName)).fetchall()
                    for r in temp:
                        contains.append(r[0])
                else: #if year is same and month is same
                    if content == 1:
                        i = cur.execute("SELECT * FROM timelineNPS2 WHERE substr(start, -4, 4) = ? and substr(start, 0, 3) =? and className = ?", (start[-4:], start[:2], cName)).fetchall()
                        if len(i) > 0:
                            results.append({
                                'start': i[0][0],
                                'content': i[0][1],
                                'className': i[0][2],
                                'subGroup': i[0][3],
                                'group' : i[0][4],
                                'important' : i[0][5],
                                'metadata' : i[0][6]
                                })
                    else:    
                        results.append({
                            "start" : start,
                            "end" : end,
                            "content" : content,
                            "className" : pName,
                            "contains" : contains
                            })
                    start = row[4]
                    end = start
                    content = int(row[1])
                    contains = []
                    temp = cur.execute("SELECT content from timelineNPS2 where substr(start, -4, 4) = ? and substr(start, 0, 3) = ? and className = ?", (cYear, cMonth, cName)).fetchall()
                    for r in temp:
                        contains.append(r[0])
            else: 
                if content == 1:
                    i = cur.execute("SELECT * FROM timelineNPS2 WHERE substr(start, -4, 4) = ? and substr(start, 0, 3) =? and className = ?", (start[-4:], start[:2], cName)).fetchall()
                    if len(i) > 0:
                        results.append({
                            'start': i[0][0],
                            'content': i[0][1],
                            'className': i[0][2],
                            'subGroup': i[0][3],
                            'group' : i[0][4],
                            'important' : i[0][5],
                            'metadata' : i[0][6]
                            })
                else:    
                    results.append({
                        "start" : start,
                        "end" : end,
                        "content" : content,
                        "className" : pName,
                        "contains" : contains
                        })
                start = row[4]
                end = start
                content = int(row[1])
                contains = []
                temp = cur.execute("SELECT content from timelineNPS2 where substr(start, -4, 4) = ? and substr(start, 0, 3) = ? and className = ?", (cYear, cMonth, cName)).fetchall()
                for r in temp:
                    contains.append(r[0])
            # if pMonth:
            #     print int(cMonth) - int(pMonth)
            pName = cName
            pYear = cYear
            pMonth = cMonth
    else:
        sql = cur.execute("SELECT substr(start, -4, 4) AS year, count(*), className, start FROM timelineNPS2 GROUP BY year, className ORDER BY className, year").fetchall()
        pName = None
        prevYr = None
        start =None
        content =0
        end = None
        contains = []
        temp = []
        for row in sql:
            currYr = row[0]
            cName = row[2]
            if not cName == pName: #if features are not the same
                if prevYr == None: #special case for first element in list
                    start = row[3]
                    end = currYr
                    content = int(row[1])
                else: #all other cases
                    if content ==1: #if there's only one element, make an entry for that element
                        i = cur.execute("SELECT * FROM timelineNPS2 WHERE substr(start, -4, 4) = ? and className = ?", (start[-4:], cName)).fetchall()
                        if len(i) > 0:
                            results.append({
                                'start': i[0][0],
                                'content': i[0][1],
                                'className': i[0][2],
                                'subGroup': i[0][3],
                                'group' : i[0][4],
                                'important' : i[0][5],
                                'metadata' : i[0][6]
                                })
                    else:  #else make a collapse entry
                        results.append({
                            "start" : start,
                            "end" : end,
                            "content" : content,
                            "className" : pName,
                            "contains" : contains
                            })
                    #start a new entry
                    contains = []
                    start = row[3]
                    end = start
                    content = int(row[1])
                    temp = cur.execute("SELECT content from timelineNPS2 where substr(start, -4, 4) = ? and className = ?", (currYr, cName)).fetchall()
                    for r in temp:
                        contains.append(r[0])
            else: #if features are the same 
                if int(currYr) - int(prevYr) == 1: #if years are sequential
                    end = currYr
                    content += int(row[1])
                    temp = cur.execute("SELECT content from timelineNPS2 where substr(start, -4, 4) = ? and className = ?", (currYr, cName)).fetchall()
                    for r in temp:
                        contains.append(r[0])
                else: #if years do not match up
                    if content == 1: #features are same, years are not, content is 1
                        #problem: this is catching the first element in collasped cases?
                        i = cur.execute("SELECT * FROM timelineNPS2 WHERE substr(start, -4, 4) = ? and className = ?", (start[-4:], cName)).fetchall()
                        results.append({
                            'start': i[0][0],
                            'content': i[0][1],
                            'className': i[0][2],
                            'subGroup': i[0][3],
                            'group' : i[0][4],
                            'important' : i[0][5],
                            'metadata' : i[0][6]
                            })
                    else:
                        results.append({
                            "start" : start,
                            "end" : end,
                            "content" : content,
                            "className" : pName,
                            "contains" : contains
                            })
                    contains = []
                    start = row[3]
                    content = int(row[1])
                    end = start
                    temp = cur.execute("SELECT content from timelineNPS2 where substr(start, -4, 4) = ? and className = ?", (currYr, cName)).fetchall()
                    for r in temp:
                        contains.append(r[0])
            pName = cName
            prevYr = currYr
    return results



                    



if __name__ == "__main__":
    app.run(debug=True)