import websocket
import json
import mysql.connector
import datetime

websocket_url = "wss://zkillboard.com/websocket/"
channel = "killstream"

try:
    # Connect to MySQL database
    db = mysql.connector.connect(
        host="eve.mysql.database.azure.com",
        user="nikobien",
        password="Mustang1604",
        database="eveskuska"
    )
    print("Database connected")

    # Define callback function for receiving WebSocket messages
    def on_message(ws, message):
        print("received...")
        data = json.loads(message)
        # Extract relevant data from message
        victim_ship_type = data['victim']['ship_type_id']
        attacker_corp = data['attackers'][0]['corporation_id']
        print(attacker_corp)
        kill_time = data['killmail_time']
        time_obj = datetime.datetime.strptime(kill_time, '%Y-%m-%dT%H:%M:%SZ')
        mysql_time_str = time_obj.strftime('%Y-%m-%d %H:%M:%S')
        # Insert data into MySQL database
        sql = "INSERT INTO kills (victim_ship_type, attacker_corp, kill_time) VALUES (%s, %s, %s)"
        val = (victim_ship_type, attacker_corp, mysql_time_str)
        cursor = db.cursor()
        cursor.execute(sql, val)
        db.commit()

    def on_open(ws):
        subscription_command = {"action": "sub", "channel": channel}
        ws.send(json.dumps(subscription_command))
        
    # Set up WebSocket client
    ws = websocket.WebSocketApp(websocket_url, on_open=on_open, on_message=on_message)
    ws.run_forever()

except mysql.connector.Error as error:
    print("Error: {}".format(error))

finally:
    if (db.is_connected()):
        db.close()
        print("Database connection closed.")
