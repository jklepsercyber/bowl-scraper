import requests
from requests_toolbelt.utils import dump

# This script should be run in order to update your command with new names/descrptions/options.

url = ["https://discord.com/api/v8/applications/901341489559396395/guilds/901343958964244480/commands", #guild ID is for Alpha Playground
    "https://discord.com/api/v8/applications/901341489559396395/guilds/161001009987059712/commands"] #guild ID is for Shitpost Alpha

req_json = {
    "name": "markov_generate",
    "type": 1, # This is an example CHAT_INPUT or Slash Command, with a type of 1
    "description": "Generate a sentence based off of stored Discord message data, interpreted into a Markov chain.",
    "options": [
        {
            "name": "length",
            "description": "Length of the generated text",
            "type": 4, # type 4 specifies integer input https://discord.com/developers/docs/interactions/application-commands#slash-commands
            "required": True
        },
        {
            "name": "starting_word",
            "description": "The word that the generated sentence should start with",
            "type": 3, # type 3 specifies string input
            "required": False
        }
    ]
}
# For authorization, you can use either your bot token
headers = {
    "Authorization": "Bot OTAxMzQxNDg5NTU5Mzk2Mzk1.YXOdrQ.F3Xg7jAiJ41OyvNvsaK4eQ2a8mM"
}

def main():
    for link in url:
        r = requests.post(link, headers=headers, json=req_json)
        print(r)
main()