# Discord Chess Bot

**Note 1:** This is a fork of https://github.com/Kaweees/Discord-Chess-Bot.

## Changes in this fork

- This fork has been migrated to discord.py version 2.0.0.
- This fork uses hybrid commands in a cog.
- Uses the latest versions of the API's and libs previously used
- It now actually works
- It says if it is white's or black's turn
- It doesn't create a new match before the challengee has accepted the challenge
- The challengee has 6 minutes to react to an emoji to accept
- It shows the previous move in green
- A help embed has been created
- The chess.com embed has been improved
- Gives more error messages and deletes them after 5 seconds
- Forbids bots from being challenged
- Forbids self challenging
- Stops a player from being in two games at the same time
- Stops more than 3 matches playing at the same time
- Displays why the match has ended

## Setup

- In the [Discord developer portal](https://discord.com/developers/applications) create a new application and give it a name. Under `Bot` select "add bot"
- Under `Bot`, turn on PRESENCE INTENT, SERVER MEMBERS INTENT and MESSAGE CONTENT INTENT
- Generate an invite link for your bot under `QAuth2 > URL Generator`, with "bot" > , "read messages/view channels", "send messages", "use external emojis", "manage messages" and "add reactions" permissions
- Use the invite link in your browser to invite your bot to any servers you want the bot in
- Download the `bot` folder to your environment, the one with the `__main__.py` file, `.env` file and `cogs` folder
- Install python 3.10+. Make sure you have set Python to the system path to use pip
- Install dependencies with `pip install requirements.txt`
- You can change the bot prefix in the `__main__.py` file
- Back in the developer portal, under `Bot`, copy your bot's secret token. create a new `.env` file in the `bot` folder. Make sure the file is called ".env" and _not_ ".env.txt"
- Specify a variable called `TOKEN=your_token_here` with your bot's secret token replacing "your_token_here"
- Run it as a module with `python chessbot`, or `sudo nohup python3 chessbot` or whatever command you use to run python scripts in your environment; or directly run the `__main__.py` file. Congratulations, you are now self-hosting a discord bot
- You might need to turn on all intents in the developer portal, or change the bots intents in the `__main__.py` file
- If you do not want to self-host, I suggest using Heroku or [Fly.io](https://fly.io/docs/getting-started/) or Heroku
