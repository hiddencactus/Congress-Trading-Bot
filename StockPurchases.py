from CongressIndex import df
from env_secrets import API_KEY
import websocket #websocket for client side only, websockets is for websocket server
import asyncio


with open("CongressIndex.py") as file: #running CongressIndex.py from this file
    exec(file.read())

#print("xd")
#print(df)
print(df.loc[:,'Stock'])

#NOTE: if you use websockets to get current prices, need to module to real time update excel sheet

def on_message(ws, message):
    print(message)

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    ws.send('{"type":"subscribe","symbol":"AAPL"}')
    ws.send('{"type":"subscribe","symbol":"AMZN"}')
    ws.send('{"type":"subscribe","symbol":"BINANCE:BTCUSDT"}')
    ws.send('{"type":"subscribe","symbol":"IC MARKETS:1"}')

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(f'wss://ws.finnhub.io?token={API_KEY}',on_message = on_message,on_error = on_error,on_close = on_close)
    
    ws.on_open = on_open
    ws.run_forever()