'''
This is the Memory game.  This is the server (written using Flask).

To run the client use:
    http://localhost:5000/memory6

Results are stored in sqlite3 database: games.db

The database 'games' holds records in table 'results' that look like:

    +------+---------------------+------+--------+
    | time | date                | name | latest |
    +------+---------------------+------+--------+
    |   51 | 2021-12-28 20:40:08 | -    |        |
    |   52 | 2022-01-17 17:54:58 | -    |        |
    |   52 | 2021-03-25 18:28:32 | -    |        |
    |   52 | 2022-01-17 17:51:07 | -    |        |
    |   53 | 2022-12-05 16:28:15 | -    |        |
    |   53 | 2025-12-15 16:44:43 | -    |        |
    |   54 | 2021-10-19 17:48:14 | -    |        |
    |   54 | 2020-04-08 17:58:54 | -    |        |
    |   54 | 2020-02-11 17:16:43 | -    |        |
    |   54 | 2022-05-11 16:55:59 | -    |        |
    +------+---------------------+------+--------+

these need to be returned to the client in the form:

    topTenResults = 
       ["51 2021-12-28 20:40:08", 
        "52 2022-01-17 17:54:58", 
        "52 2021-03-25 18:28:32", 
        "52 2022-01-17 17:51:07",
        "53 2022-12-05 16:28:15", 
        "53 2025-12-15 16:44:43",
        "54 2021-10-19 17:48:14", 
        "54 2020-04-08 17:58:54", 
        "54 2020-02-11 17:16:43",
        "54 2022-05-11 16:55:59"]
'''

DATABASE = '/opt/Games/games.db'
LOG_FILENAME = "/opt/Games/games.log"
debug = True
my_logger = None

import os
import sqlite3
from flask import Flask, g, render_template, send_file, request, jsonify, logging
from datetime import datetime
from urllib.parse import parse_qs
import logging
import logging.handlers

 
app = Flask(__name__)

def clearLatestResultFlag(name):
    doTransaction(f"UPDATE results SET latest = ' ' WHERE name = '{name}';")

def doTransaction(SQL):
    try:
        connection = getConnection()
        cursor = connection.cursor()    
        cursor.execute("BEGIN")    # Start a transaction
        cursor.execute(SQL)
        connection.commit()
    except sqlite3.Error as e:
        print(e.sqlite_errorcode)
        print(e.sqlite_errorname)
        my_logger.error(f"{SQL} causes {e}")
    except Exception as e:
        print(e)
    finally:
        if debug: print(SQL)
        return cursor

def createTable():
    try:
        cursor = getConnection().cursor()
        cursor.execute("CREATE TABLE results(time, date, name, latest)")
    except Exception as e:
        if debug: print(e)

def getConnection():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def getTopTenResultsFromDatabase(name):
    if name == "-":
        sql = f"SELECT time, date, latest FROM results ORDER BY time ASC, date DESC LIMIT 10;"
    else:
        sql = f"SELECT time, date, latest FROM results WHERE name = '{name}' ORDER BY time ASC, date DESC LIMIT 10;"
    cursor = doTransaction(sql)
    my_logger.debug(f"getTopTenResultsFromDatabase: {sql}")
    results = cursor.fetchall() # returns a list of 10 tuples
    if debug: 
        print(sql)
        print(results)

    topTenResults = []

    for result in results:
        time = result[0]
        date = result[1]   #.strftime("%Y-%m-%d")
        latest = result[2]
        if latest == "*": 
            date = date + "*"     # browser will highlight this record in red
        topTenResults.append(f"{time} {date}")
    return topTenResults

def processAjaxCallback(time, name):
    if time > 0:
        updateDatabaseWithLatestResult(time, name)
    if name == "": name = "-"
    topTenResults = getTopTenResultsFromDatabase(name)
    my_logger.debug(f"processAjaxCallback: {topTenResults}")
    print(f"***** {topTenResults} *****")
    return topTenResults

def queryLastPlayer():
    sql = f"SELECT name FROM results ORDER BY date DESC LIMIT 1;"
    cursor = doTransaction(sql)
    my_logger.debug(f"queryLastPlayer: {sql}")
    results = cursor.fetchone()
    player = results[0]
    return player

def updateDatabaseWithLatestResult(time, name):
    clearLatestResultFlag(name)
    current_date = datetime.now()
    date = current_date.strftime("%Y-%m-%d %H:%M:%S")
    latest = '*'
    sql = f"INSERT INTO results (time, date, name, latest) VALUES ({time}, '{date}', '{name}', '{latest}');"
    doTransaction(sql)

############################################# ROUTES #############################################################

app = Flask(__name__)

@app.route("/memory6")
def hello():
    return render_template('memory6.html')

@app.route('/css/<path:filename>')
def base_static(filename):
    return send_file(f"css/{filename}")

@app.route('/jquery/<path:filename>')
def base_static2(filename):
    return send_file(f"jquery/{filename}")

@app.route('/images/cards/<path:filename>')
def base_static3(filename):
    return send_file(f'images/cards/{filename}')

# Ajax callbacks
@app.route('/games/MemoryServer/lastPlayer')
def getLastPlayer():
    player = queryLastPlayer()
    return jsonify(player)

@app.route('/games/MemoryServer')
def results():
    os.system("clear")
    queryString = request.query_string
    my_logger.debug(f'query string = {queryString}')

    json = parse_qs(queryString.decode())
    time = int(json['time'][0])
    name = json['name'][0]
    my_logger.debug(f'time = {time}, name = {name}')
    
    data = processAjaxCallback(time, name)    
    # if data == []: raise("no data")
    return jsonify(data)

def setupLogging(level):
    global my_logger
    os.system(f"rm {LOG_FILENAME}")
    my_logger = logging.getLogger('MyLogger')
    my_logger.setLevel(level)

    # Add the log message handler to the logger
    handler = logging.handlers.RotatingFileHandler(filename=LOG_FILENAME, maxBytes=20000, backupCount=5)
    my_logger.addHandler(handler)

############################################# MAIN #############################################################

if __name__ == "__main__":
    createTable()       # does nothing if table exists
    setupLogging(level = logging.DEBUG)

    port = 5000
    my_logger.info(f"serving on port {port}")
    print(f"serving on port {port}")
    app.run(debug=debug, port=port)
