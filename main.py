#!/usr/bin/python3
# (c) 2021 by Florentin Möhle. Licensed under the GNU General Public License

from flask import Flask, request, redirect, render_template
import sqlite3 as sql
import random, datetime

app = Flask(__name__)
app.secret_key = 'fdsgkljfjklfljdsljövfdökljfljöbkfljökfgljbfdkljbiojfioufdnkljfcblkewklfgökljvwlök ljkfweoig3940uioiog458089264397ß8 v8ÄRE$%&$%/&&$(%&%$)%/&/$%TGDF/T§$Efdjvklfdljkfdljökbfgökljhrtlökjbfg//(%&/&$§&§/&%$§'

lock_db = False

def lock():
    while not lock_db:
        i = 10
    return True

def connect_db():
    connection = sql.connect('database.db')
    return connection

def check_if_free(termin_id, conn):
#    lock_db = lock()
    cursor = conn.cursor()
    print(termin_id)
    cursor.execute('SELECT max_participants FROM termine WHERE id='+str(termin_id))
    max_participants = int(cursor.fetchone()[0])
    cursor.execute('SELECT COUNT(*) FROM t'+str(termin_id))
    registrated_participants = cursor.fetchone()[0]
    conn.close()
    lock_db = False
    if max_participants >= registrated_participants:
        return max_participants-registrated_participants
    return False

def book(termin_id, conn):
#    lock_db = lock()
    cursor = conn.cursor()
    key = random.randint(0, 999999)
    cursor.execute('INSERT INTO t'+str(termin_id)+'(id, key) VALUES ((select max(id) from t'+str(termin_id)+')+1, '+str(key)+')')
    conn.commit()
    conn.close()
    lock_db = False
    return key


@app.route('/')
def web_index():
    return render_template('index.html')

@app.route('/choose')
def web_choose():
    conn = connect_db()
    cursor = conn.cursor()
    termine = []
    cursor.execute('SELECT COUNT(*) FROM termine')
    anzahl_termine = int(cursor.fetchone()[0])
    print('Test')
    for termin_id in range(1, anzahl_termine+1):
        print(termin_id)
        termin = {'ID': termin_id, 'Time of Start': '', 'Time of End': '', 'Free': check_if_free(termin_id, connect_db())}
        cursor.execute('SELECT time_begin FROM termine WHERE id='+ str(termin_id))
        termin['Time of Start'] = str(datetime.datetime.utcfromtimestamp(int(cursor.fetchone()[0])))
        cursor.execute('SELECT time_end FROM termine WHERE id='+ str(termin_id))
        termin['Time of End'] = str(datetime.datetime.utcfromtimestamp(int(cursor.fetchone()[0])))
        termine.append(str(termin))
        print(termin)
    conn.close()
    return render_template('termin.html', termine=termine)

@app.route('/book', methods=['POST'])
def web_book():
    termin_id = int(request.form['termin_id'])
    anzahl_buchungen = int(request.form['anzahl'])
    if check_if_free(termin_id, connect_db()) < anzahl_buchungen:
        return 'nothing free.'
    keys = []
    for i in range(int(anzahl_buchungen)):
        keys.append(book(termin_id, connect_db()))
    # return render_template('success.html', keys)
    return str(keys)

@app.route('/check', methods=['GET'])
def web_check():
    key = request.args['key']
    termin_id = request.args['termin_id']
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM t'+str(termin_id)+' WHERE key='+str(key))
    return str(bool(cursor.fetchall()))
