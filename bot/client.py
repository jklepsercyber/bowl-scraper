#!/usr/bin/env python
import asyncio
from requests.api import request
import websockets
import json
import os
import sys
sys.path.append('./')
import sqlite3
import requests
from datetime import datetime

#custom library imports
from userslash import SlashHandler
from message_service import MessageExecutor
from json_writer import JsonWriter
from ml_model.training import *

if not os.path.isfile("./config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open("./config.json") as config_file:
        config = json.load(config_file)
        bot_prefix = config["bot_prefix"]
        bot_token = config["token"]

#Initialize some variables
heartbeat = 0 # for discord_heartbeat
heartbeat_ack_bit = True # NEED TO FINISH HEART ACK
sequence_num = 0 # for discord_heartbeat
session_id = ""

#initialization stuff that executes before any asynchronous loop is instantiated
slash_handler = SlashHandler()
message_executor = MessageExecutor()
json_writer = JsonWriter()
headers = { # for HTTP request auth
    "Authorization": "Bot OTAxMzQxNDg5NTU5Mzk2Mzk1.YXOdrQ.F3Xg7jAiJ41OyvNvsaK4eQ2a8mM"
}

if not os.path.exists("saved-data/guild-info.json"): # make sure file exists. r+ doesn't write new files
    with open("saved-data/guild-info.json", 'w'): 
        print("Guildsinfo file did not exist, initializing!")
        pass
if not os.path.exists("saved-data/last-channel-message.json"): # make sure file exists. r+ doesn't write new files
    with open("saved-data/last-channel-message.json", 'w'): 
        print("Lastchannel file did not exist, initializing!")
        pass
bowldb = sqlite3.connect('saved-data/bowl-data.db') # initialize SQL database if does not exist
cursor = bowldb.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS main(
    author TEXT,
    msg TEXT,
    channel TEXT,
    id TEXT,
    timestamp DATETIME 
    )
''')
bowldb.commit()
bowldb.close()



# EVENT LOOPS

async def catch_up(guilds):
    try:
        with open("saved-data/last-channel-message.json", 'r') as f: 
            last_messages = json.load(f)
    except:
        print("No catchup data available.")
        return
    
    catchup_count = 0
    for guild in guilds:
        id = guild["id"]
        url = f"https://discord.com/api/v8/guilds/{id}/channels"
        r = requests.get(url, headers=headers)
        channels = json.loads(r.text)
        for channel in channels:
            if(channel["type"]!=0): # text channel type is 0
                continue
            c_name = channel["name"]
            c_id = channel["id"]
            c_last_msg = channel["last_message_id"]
            try:
                last_recorded_msg_id = last_messages[c_id]
                print(f"Text channel {c_name} : {c_id} accessed!")
            except:
                print(f"No new data for {c_name} : {c_id}. Moving on...")
                continue
            if (last_recorded_msg_id != c_last_msg):
                print("Retrieving new messages...")
                chan_url = f"https://discord.com/api/v8/channels/{c_id}/messages" # https://discord.com/developers/docs/resources/channel#get-channel-messages
                r = requests.get(chan_url, headers=headers, params={'after':last_recorded_msg_id, 'limit':100})
                catchup_messages = json.loads(r.text)
                print("Catching up new messages...")
                for msg in reversed(catchup_messages): # messages come out last to first for some reason
                    try:
                        newmsg = msg["content"]
                        print(f"Message found : {newmsg}")
                        countval = await message_executor.user_message_store(msg)
                        catchup_count += countval
                    except Exception as e:
                        print(f"Error with {newmsg} : caught exception {e}")
                        continue
                await json_writer.update_last_message(catchup_messages[0]) # order is reversed when adding to corpus for continuity, but catchup_messages[0] still holds last msg sent

    print(f"All caught up! {catchup_count} messages added to bowl-data.db.")
    if catchup_count>0:
        sentence_data = sentence_dump()
        markov_chain(sentence_data)
        print("Markov data in bowl-data.db updated!")
        print("------------------------\n")
    else:
        print("No new sentences added; bowl-data.db unchanged.")
        print("------------------------\n")

async def discord_heartbeat(ws):
    while True:
        print(f"Heartbeat service running. Current heartbeat: {heartbeat} --- Current seq #: {sequence_num}")
        if (heartbeat!=0):
            msg_json = json.loads(f"{{ \"op\": 1, \"d\": {sequence_num} }}")
            print(f"Sending heartbeat packet: {json.dumps(msg_json)}")
            await ws.send(json.dumps(msg_json))
            print("Heartbeat packet sent!")
        else:
            print("Heartbeat not found yet. Waiting...")
            await asyncio.sleep(1)
        await asyncio.sleep(heartbeat/1000.0)


async def message_handler():
    async with websocket as ws:
        while True:
            try:
                print("Message service listening...")
                message = await ws.recv()
                msg_json = json.loads(message)
                print(f"-----------------\n Message Received!: {message} \n------------------")
                #print(json.dumps(msg_json, indent=4)) #pretty print for message

                # OP=10: HANDSHAKE PROCEDURE
                if msg_json["op"]==10:
                    global heartbeat
                    global sequence_num
                    heartbeat = msg_json["d"]["heartbeat_interval"]
                    sequence_num = "null"
                    print(f"Heartbeat found!: {heartbeat}")
                    tasks.append(asyncio.ensure_future(discord_heartbeat(ws))) # heartbeat should initialize whenever packet found
 
                    # Construct IDENTIFY packet https://discord.com/developers/docs/topics/gateway#identify
                    msg_json = json.loads(f"""{{  
                        \"op\": 2,
                        \"d\": {{
                            \"token\": \"{bot_token}\",
                            \"intents\": 513,
                            \"properties\": {{
                                \"$os\": \"windows\",
                                \"$browser\": \"bowl_scraper\",
                                 \"$device\": \"bowl_scraper_lib\"
                                }}
                            }}
                        }}""")
                    print(json.dumps(msg_json))
                    print("Sending IDENTIFY packet...")
                    await ws.send(json.dumps(msg_json))
                    print("IDENTIFY packet sent!")
                    raise UnboundLocalError()
                
                # OP=1: GATEWAY REQUESTED A HEARTBEAT https://discord.com/developers/docs/topics/gateway#identify
                if msg_json["op"]==1:
                    msg_json = json.loads(f"{{ \"op\": 1, \"d\": {sequence_num} }}")
                    print(f"Heartbeat packet requested! Sending...: {json.dumps(msg_json)}")
                    await ws.send(json.dumps(msg_json))
                    print("Heartbeat packet sent!")
                    raise UnboundLocalError()
                
                # t=READY: Discord READY packet! Sent to initialize session https://discord.com/developers/docs/topics/gateway#ready, https://discord.com/developers/docs/topics/gateway#guild-create sent after
                if msg_json["t"]=="READY":
                    global session_id
                    global bot_username
                    print("Ready packet received!")
                    bot_username = msg_json["d"]["user"]["username"]
                    guilds = msg_json["d"]["guilds"]
                    session_id = msg_json["d"]["session_id"] # store session ID
                    sequence_num = msg_json["s"] # store sequence number
                    try:
                        await catch_up(guilds) # now that the full handshake is complete, we can run the catch_up service
                    except Exception as e:
                        print(f"Error catching up: {e}")
                    raise UnboundLocalError()
                
                # t=MESSAGE_CREATE: TEXT CHAT MESSAGE RECEIVED IN SOME CHANNEL. CONTAINS NAME AND ROLES
                if msg_json["t"]=="MESSAGE_CREATE":
                    sequence_num = msg_json["s"]
                    await message_executor.user_message_store(msg_json["d"]) # MessageExecutor handles adding message to SQLite database
                    await json_writer.update_last_message(msg_json["d"]) # update json last message
                    raise UnboundLocalError
                
                # t=GUILD_CREATE: GUILD INFO RECEIVED IN GUILD BOT IS IN
                if msg_json["t"]=="GUILD_CREATE":
                    sequence_num = msg_json["s"]
                    g_name = msg_json["d"]["name"]
                    g_roles = msg_json["d"]["roles"]
                    g_id = msg_json["d"]["id"]
                    g_json = {
                        "guild_name" : g_name,
                        "guild_roles" : g_roles
                    }
                    with open("saved-data/guild-info.json", 'r+') as guild_file:
                        try:
                            raw = guild_file.read()
                            data = json.loads(raw)
                        except Exception as e:
                            print(f"{guild_file} empty or exception {e}. Initializing data!")
                            data = dict()
                        data[g_id] = g_json # if guild_id exists, update last entry. if not, create guild_id key!        
                        guild_file.seek(0) # make sure we overwrite beginning of file
                        json.dump(data, guild_file, indent=4)
                        print("Guild saved to guild-info.json!")
                    raise UnboundLocalError
                
                # t=INTERACTION_CREATE: User is calling a slash command!
                if msg_json["t"]=="INTERACTION_CREATE":
                    if msg_json["d"]["type"]==2: # Type 2 represents an Application Command. https://discord.com/developers/docs/interactions/receiving-and-responding#interaction-object-interaction-structure
                        interaction_id = msg_json["d"]["id"]
                        interaction_token = msg_json["d"]["token"]
                        slash_name = msg_json["d"]["data"]["name"]
                        user = msg_json["d"]["member"]["user"]["username"]
                        try: # options may not always exist!
                            options = msg_json["d"]["data"]["options"]
                        except:
                            options = ""
                        print("Slash handler parsing command...")
                        await slash_handler.handle_switch(slash_name, interaction_id, interaction_token, options, user)
                    print("Finished parsing interaction.")
                    raise UnboundLocalError

            except UnboundLocalError:
                print ("Message type parsed. Restarting message listener service...")
                pass
            except websockets.exceptions.ConnectionClosed:
                print("ConnectionClosed. Attempting to Restart...")
                msg_json = json.loads(f"{{ \"op\": 6, \"d\": {{ \"token\" : {bot_token} , \"session_id\" : {session_id} \"seq\" : {sequence_num} }} }}") # RESUME packet
                await ws.send(json.dumps(msg_json))
                print("RESUME packet sent. Hopefully the Gateway responds...")
                pass

            print("Message service looping...  Sleepy time in main :) \n\n")
            await asyncio.sleep(1)


# finally, executable "main" code!
websocket = websockets.connect('wss://gateway.discord.gg/?v=9&encoding=json')
tasks = [
    asyncio.ensure_future(message_handler())
] # modifiable task list so we can add/remove websocket asynchronous tasks as needed

asyncio.get_event_loop().run_until_complete(asyncio.wait(tasks))