#This file contains all slash commands that might be called by a user, read into the message handler. Functions will called from client.py.

from collections import defaultdict
import json
import requests
import asyncio
import sys
sys.path.append('./')

#Custom module imports
from ml_model.markov_gen import *
from ml_model.training import *

def case_markov_generate(count, start_word="") -> str:
    if count<=3:
        content = "That count is too woaw :3" 
        return content
    elif count>400:
        content = "That count is too damn high!"
        return content
    content = ""
    with open ('./markov_dict.json', 'r') as file:
        markov_dict = json.load(file)
    print("Markov dict loaded!")
    content = generate_sentence(markov_dict, count, start_word)
    return content   

def case_update_resources(user, url, resp_json):
    if user=="dogchow33":
        resp_json["data"]["content"] = "Got it. Updating markov_dict.json..."
        r = requests.post(url, json=resp_json) # send post request before updating resources due to time it takes to do so
        markov_chain(sentence_dump()) # this command is blocking so that /markov_generate may not be called during update time
        return
    else:
        resp_json["data"]["content"] = "You are not allowed to update markov_dict.json!"
        r = requests.post(url, json=resp_json) 
    return

class SlashHandler(object):
    def __init__(self) -> None:
        print("SlashHandler initialized!")
        return None

    async def handle_switch(self, command_name, interaction_id, interaction_token, options, user):
        url = f"https://discord.com/api/v8/interactions/{interaction_id}/{interaction_token}/callback"
        resp_json = {
            "type": 4,
            "data": {
                "content": "Initial response! Can be modified later."
            }
        }
        
        #time to decide which custom command should be run!
        if command_name == "markov_generate":
            try:
                start_word = options[1]["value"] # start word contained in second option
            except:
                start_word = "" # if no start word specified
            resp_json["data"]["content"] = case_markov_generate(options[0]["value"], start_word) # num words to generate contained in first option
        elif command_name == "update_resources": 
            case_update_resources(user, url, resp_json)
            return 
        else:
            resp_json["data"]["content"] = "Oopsie woopsie! Command not wecognized :3"    

        try: # for commands other than update_resources, send POST request at the end
            r = requests.post(url, json=resp_json)
            print("POST request sent to Discord!")
        except:
            print("Exception occurred while sending test response.")
        
        return
    

