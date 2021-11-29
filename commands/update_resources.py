import requests
from requests_toolbelt.utils import dump

# This script should be run in order to update your command with new names/descrptions/options.

url = ["https://discord.com/api/v8/applications/<appidhere>/guilds/<guildidhere>/commands", 
    "https://discord.com/api/v8/applications/<appidhere>/guilds/<guildidhere>/commands"] # add as many guild URLs as you like here

req_json = {
    "name": "update_resources",
    "type": 1, # This is an example CHAT_INPUT or Slash Command, with a type of 1 https://discord.com/developers/docs/interactions/application-commands#slash-commands
    "description": "Update the markov_dict.json without having to restart the client.",
}
# For authorization, you can use either your bot token
headers = {
    "Authorization": "Bot <bottokenhere>"
}

def main():
    for link in url:
        r = requests.post(link, headers=headers, json=req_json)
        print(r)
main()
