import os
import sys
import json

class JsonWriter(object):
    def __init__(self) -> None:
        print("JsonWriter initialized!")
        return None
    
     # add a JSON file here storing channel_id : last_message_id pairs for message catch_up purposes. Discord API sorts messages by message ID
    async def update_last_message(self, newmsg):
        sent_channel = newmsg["channel_id"]
        msg_id = newmsg["id"]
        try:
            print("Updating last-message json...")
            with open("saved-data/last-channel-message.json", 'r+') as last_msg_file:
                try:
                    raw = last_msg_file.read()
                    data = json.loads(raw)
                except Exception as e:
                    print(f"{last_msg_file} empty or exception {e}. Initializing data!")
                    data = dict()
                data[sent_channel] = msg_id # if channel exists, update last message. if not, create channel key!        
                last_msg_file.seek(0) # make sure we overwrite beginning of file
                json.dump(data, last_msg_file, indent=4)
                print("Message saved, and last-message JSON updated! \n Message : \n")
                print(newmsg["content"]+"\n")
        except Exception as e:
            print(f"Exception {e} while writing last-channel JSON...")
