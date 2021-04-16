import discord
from discord.ext import commands, tasks
import json
from discord.utils import get
import datetime
import collections
import matplotlib.pyplot as plt
Token = ''
intents = discord.Intents.default()
intents.members = True
intents.presences = True
bot = commands.Bot(command_prefix='stats/', intents=intents)
guilds = []
jguilds = {}
hcount = 0
mcntr = collections.Counter()
maind = {}


def jsoner(data):
    with open(str(datetime.datetime.now().date())+'.json', "w") as write_file:
        json.dump(data, write_file)


@bot.command()
async def log(ctx):
    guilds.append(ctx.guild.id)
    print(ctx.guild.id)
    maind[str(ctx.guild.id)] = {'games_total': [], 'messages': [], 'user_visits': [], 'user_total': []}


@bot.command()
async def archive(ctx, arg):
    file = discord.File(arg+'.json')
    await ctx.send(file=file, content="Message to be sent")


@bot.command()
async def graph(ctx, arg, arg1):
    await ctx.send(file=discord.File(arg+'_'+arg1+'.png'))


@tasks.loop(seconds=1200)
async def get_checks():
    global hcount
    hcount += 1
    print(datetime.datetime.now().time())
    if hcount == 72:
        hcount = 0
    for i in guilds:
        cntr = collections.Counter()
        usonline = 0
        check = bot.get_guild(i)
        members = check.member_count
        for j in check.members:
            if isinstance(j.activities, tuple):
                if len(j.activities)!=0:
                    usonline+=1
                    act = j.activities[len(j.activities)-1].name
                    cntr[str(act)] += 1
            else:
                act = 'Nothing'
                cntr[str(act)] += 1
        maind[str(i)]['user_visits'].append(usonline)
        maind[str(i)]['user_total'].append(members)
        maind[str(i)]['games_total'].append(dict(cntr))
        maind[str(i)]['messages'].append(mcntr[str(i)])
        mcntr.clear()
        cntr.clear()
        plt.axis([0, 72, 0, members+1])
        plt.title('Users online a day')
        plt.xlabel('Time')
        plt.ylabel('Users online')
        plt.plot(maind[str(i)]['user_visits'])
        plt.legend(['Every time section equals 20 mins'])
        plt.savefig(str(i)+'_onlineusersday.png')
        plt.clf()
        plt.axis([0, 72, 0, members+10])
        plt.title('Users total a day')
        plt.xlabel('Time')
        plt.ylabel('Users')
        plt.plot(maind[str(i)]['user_total'])
        plt.legend(['Every time section equals 20 mins'])
        plt.savefig(str(i)+'_usersday.png')
        plt.clf()
        plt.axis([0, 72, 0, maind[str(i)]['messages'][len(maind[str(i)]['messages'])-1]+10])
        plt.title('Messages a day')
        plt.xlabel('Time')
        plt.ylabel('Messages')
        plt.plot(maind[str(i)]['messages'])
        plt.legend(['Every time section equals 20 mins'])
        plt.savefig(str(i)+'_message.png')
        plt.close()
        if hcount == 0:
            jsoner(maind)
            maind[str(i)] = {'games_total': [], 'messages': [], 'user_visits': [], 'user_total': []}


@bot.event
async def on_message(message):
    if message.guild.id in guilds:
        mcntr[str(message.guild.id)] += 1
    await bot.process_commands(message)


@bot.event
async def on_ready():
    get_checks.start()
    print('READY')


bot.run(Token)
