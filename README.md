# Python Discord Bot Template

This repository is a template that everyone can use for the start of their discord bot.

I would've been happy if there were any template existing. However, there wasn't any existing template. That's why I
decided to create my own template to let <b>you</b> guys create your discord bot easily.


## How to download it

Alternatively you can do the following:

* Clone/Download the repository
    * To clone it and get the updates you can definitely use the command
      `git clone`
* Create a discord bot [here](https://discord.com/developers/applications)
* Get your bot token
* Invite your bot on servers using the following invite:
  https://discord.com/oauth2/authorize?&client_id=YOUR_APPLICATION_ID_HERE&scope=bot+applications.commands&permissions=PERMISSIONS (
  Replace `YOUR_APPLICATION_ID_HERE` with the application ID and replace `PERMISSIONS` with the required permissions your bot needs that it can be get at the bottom of a this page https://discord.com/developers/applications/YOUR_APPLICATION_ID_HERE/bot)

## How to set up

To set up the bot I made it as simple as possible. I now created a [config.json](config.json) file where you can put the
needed things to edit.

Here is an explanation of what everything is:

| Variable                  | What it is                                                            |
| ------------------------- | ----------------------------------------------------------------------|
| YOUR_BOT_PREFIX_HERE      | The prefix(es) of your bot                                            |
| YOUR_BOT_TOKEN_HERE       | The token of your bot                                                 |
| YOUR_APPLICATION_ID_HERE  | The application ID of your bot                                        |
| OWNERS                    | The user ID of all the bot owners                                     |

## How to start

To start the bot you simply need to launch, either your terminal (Linux, Mac & Windows), or your Command Prompt (
Windows)
.

Before running the bot you will need to install all the requirements with this command:

```
pip install -r requirements.txt
```

<br>

If you have just installed python today, then you just need to use the following command:

```
python client.py
```

## Built With

* [Python 3.8](https://www.python.org/)
