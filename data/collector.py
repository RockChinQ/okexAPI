import sys
import time
import websocket
import json
import threading

print(str(sys.argv))

PRODUCT = "DOGE-USDT"
PUBLIC_URL = "wss://ws.okex.com:8443/ws/v5/public"

ws = 0


def connect():
    global ws
    ws = websocket.WebSocket()
    print(time.strftime("%m-%d,%H:%M:%S", time.localtime()) + " connecting...")
    ws.connect(PUBLIC_URL, http_proxy_host="localhost", http_proxy_port=10809)

    subscribeDict = {
        "op": "subscribe",
        "args": [{
            "channel": "candle1m",
            "instId": PRODUCT
        }]
    }

    ws.send(json.dumps(subscribeDict))

    print(ws.recv())


connect()
