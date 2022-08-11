import json
import discord
from discord.ext import commands, tasks
import aiohttp
import asyncio

with open("./config.json", "r") as file:
    secret_file = json.load(file)

client = commands.Bot(command_prefix="",help_command=None,intents=discord.Intents.default())


@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))


@client.event
async def on_command_error(ctx, error):
    if isinstance(error , commands.CommandNotFound):
        return
    else:
        raise error


#Every 30s it sets the bot's status to your server pop
@tasks.loop(seconds=30)
async def pop_status():
    url = f"https://api.battlemetrics.com/servers/" + str(secret_file["BM_ServerID"])
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                resp_dict = json.loads(await resp.text())
                status = resp_dict["data"]["attributes"]["status"] 
                ConnectedPlayers = resp_dict["data"]["attributes"]["players"] 
                MaxPlayers = resp_dict["data"]["attributes"]["maxPlayers"]
                QueuedPlayers = resp_dict["data"]["attributes"]["details"]["rust_queued_players"]
                if status == "online":
                    if QueuedPlayers > 0:
                        await client.change_presence(status=discord.Status.online,activity=discord.Game(name=f"{ConnectedPlayers}/{MaxPlayers} (+{QueuedPlayers})"))    
                    else:
                        await client.change_presence(status=discord.Status.online,activity=discord.Game(name=f"{ConnectedPlayers}/{MaxPlayers}"))    
                else:
                    await client.change_presence(status=discord.Status.do_not_disturb, activity=discord.Game(name="[Offline]"))
                    
            else:
                await client.change_presence(status=discord.Status.do_not_disturb, activity=discord.Game(name=f"BM Error -> {resp.status} "))
                print(f"Battlemetrics Error with status code: {resp.status}")



@pop_status.before_loop
async def before_pop_status():
    await client.wait_until_ready()


async def main():
    if __name__ == "__main__":
        async with client:
            pop_status.start()
            await client.start(secret_file["BotToken"],reconnect=True)
asyncio.run(main())


