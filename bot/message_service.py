import os
import platform
import random
import sys
import asyncio
import sqlite3
import re
from requests.api import request
sys.path.append('./')
import json

# Eventually, we can have all message stuff be carried out through this class.

class MessageExecutor(object):
    def __init__(self) -> None:
        print("MessageHandler initialized!")
        return None

    async def user_message_store(self, msg_json) -> int: # return 0 if invalid message, 1 if human message
        try:
            bot_test = msg_json["author"]["bot"]
            print("Bot message detected. Ignoring :)")
            return 0 # exit if bot_test resolves
        except: # KeyError exception raised if message is not from a bot
            pass

        author = msg_json["author"]["username"]
        content = msg_json["content"] 
        timestamp = msg_json["timestamp"]
        sent_channel = msg_json["channel_id"]
        msg_id = msg_json["id"]

        if "http" in content or len(content)<=1: # handle URLs and 0/1 length sentences
            return 0

        # handle mentions before we log the message
        if len(msg_json["mentions"])!=0:
            mentions = msg_json["mentions"]
            mentionsdict = dict()
            for mention in mentions:
                id = mention["id"] # get userid from current mention
                mentionsdict[id] = mention["username"] # {userid : username} as the key value pair
            for userid in mentionsdict.keys():
                content = re.sub(rf'<@(.)?({userid})>', rf'{mentionsdict[userid]}', content) #replace all instances of mentioned id with username

        # now do the same for handling role mentions
        if len(msg_json["mention_roles"])!=0:
            mentions_roles = msg_json["mention_roles"]
            mentions_roles_dict = dict()
            with open('saved-data/guild-info.json') as guildfile: # need to pull role names from guild-info
                role_guilds = json.loads(guildfile.read())
                for role in mentions_roles: #mentions_roles is just a list of role_id integers
                    for role_query in role_guilds[sent_channel]["guild_roles"]: # time to query saved guild_roles for the one given in our message!
                        if role_query["id"] == role:
                            mentions_roles_dict[role] = role_query["name"] # {role_id : role_name} as the key value pair
                            break
            for roleid in mentions_roles_dict.keys():
                content = re.sub(rf'<@&{roleid}>', mentions_roles_dict[roleid], content) #replace all instances of mentioned id with role name

        bowldb = sqlite3.connect('saved-data/bowl-data.db')
        cursor = bowldb.cursor()
        sql = ("INSERT INTO main(author, msg, channel, id, timestamp) VALUES(?,?,?,?,?)")
        vals = (author, content, sent_channel, msg_id, timestamp)
        cursor.execute(sql, vals)
        bowldb.commit()
        cursor.close()
        bowldb.close()
        
        return 1