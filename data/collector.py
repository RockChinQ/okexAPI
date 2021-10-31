import sys
import threading
import time
import traceback

import websocket
import json
import MySQLdb

print(str(sys.argv))

PUBLIC_URL = "wss://ws.okex.com:8443/ws/v5/public"

ws = 0

# configurations
conf = open("data.conf", "r")

confs = conf.readline(1000).replace("\n", "").split(" ")
if confs[0].startswith("#"):
    confs = conf.readline(1000).replace("\n", "").split(" ")
print(str(confs))
confs2 = conf.readline(1000).replace("\n", "").split(" ")
if confs2[0].startswith("#"):
    confs2 = conf.readline(1000).replace("\n", "").split(" ")

tableName = ""


def connect():
    global ws, db, cursor, tableName
    ws = websocket.WebSocket()
    while 1:
        try:
            print(time.strftime("%m-%d,%H:%M:%S", time.localtime()) + " connecting...")
            ws.connect(PUBLIC_URL, http_proxy_host="localhost", http_proxy_port=10809)
            break
        except BaseException:
            print("retry...")
            continue

    subscribeDict = {
        "op": "subscribe",
        "args": [{
            "channel": "candle1m",
            "instId": confs2[0]
        }]
    }

    ws.send(json.dumps(subscribeDict))

    print(ws.recv())

    db = MySQLdb.connect(confs[0], confs[1], confs[2], confs[3], charset='utf8')
    cursor = db.cursor()
    ts = time.strftime("%y_%m_%d_%H_%M_%S", time.localtime())
    tableName = confs2[0].replace("-", "_") + "_" + ts
    print(tableName)
    createTable = """CREATE TABLE `""" + tableName + """` (
	`id` int unsigned auto_increment,
    `timeStamp` int8 unsigned not null,
    `price` float unsigned not null,
    primary key (id)
    )"""

    cursor.execute(createTable)


connect()


def storageWatchdog():

    db2 = MySQLdb.connect(confs[0], confs[1], confs[2],"information_schema", charset='utf8')
    cursor2 = db2.cursor()
    while 1:
        try:
            exec="select concat(round(sum(data_length/1024/1024),2),'MB') as data from tables where table_schema='coinbot' and table_name='" + tableName + "'"
            # print(exec)
            cursor2.execute(exec)
            results = cursor2.fetchall()
            print(time.strftime("%m-%d,%H:%M:%S", time.localtime()) + " Size of table:" + tableName + " is " + str(results[0][0]))
        except BaseException:
            traceback.print_exc()
            print(time.strftime("%m-%d,%H:%M:%S", time.localtime()) +" Failed to fetch size.")
        time.sleep(60 * 5)


threading.Thread(target=storageWatchdog).start()


def loopRecv():
    global currentCandleStart, isPreviousSaRPointHigh, ws
    while True:
        dataJSON = ""
        try:
            dataJSON = ws.recv()
        except BaseException:
            connect()
            continue

        # print(dataJSON)
        receive = json.loads(dataJSON)

        insert = "INSERT INTO " + tableName + " (timeStamp,price) values (%d" % int(
            receive["data"][0][0]) + ",%.8f" % float(receive["data"][0][4]) + ");"
        # print(insert)
        try:
            cursor.execute(insert)
            db.commit()
        except:
            print("failed to insert")


loopRecv()
