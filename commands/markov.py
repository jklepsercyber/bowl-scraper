import requests
from requests_toolbelt.utils import dump

# This script should be run in order to update your command with new names/descrptions/options.

url = ["https://discord.com/api/v8/applications/<appidhere>/guilds/<guildidhere>/commands",
      "https://discord.com/api/v8/applications/<appidhere>/guilds/<guildidhere>/commands"] # place as many urls as you like here

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
    "Authorization": "Bot <yourtokenhere>"
}

def main():
    for link in url:
        r = requests.post(link, headers=headers, json=req_json)
        print(r)
main()
