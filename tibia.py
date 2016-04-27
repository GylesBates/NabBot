import discord
from discord.ext import commands
import asyncio
import urllib.request
import urllib
import re
import math
import random
import sqlite3
from datetime import *
import time
from calendar import timegm

import sys
import builtins
def print(output):
    builtins.print(output)
    outputfile = open('console.txt', 'a')
    outputfile.write(output+"\r\n")
    outputfile.close()

def getPlayerDeaths(player, singleDeath = False):
    deathList = []
    content = ""
    retry = 0
    while content == "" and retry < 5:
        try:
            page = urllib.request.urlopen('https://secure.tibia.com/community/?subtopic=characters&name='+urllib.parse.quote(player))
            content = page.read()
        except Exception:
            retry=retry+1
            
    if content == "":
        print("Error in getPlayerDeaths("+player+")")
        return deathList
        
    #Check if player exists (in a really lazy way)
    try:
        content.decode().index("Vocation:")
    except Exception:
        return None

    try:
        content.decode().index("<b>Character Deaths</b>")
    except Exception:
        return deathList
    startIndex = content.decode().index("<b>Character Deaths</b>")
    endIndex = content.decode().index("<B>Search Character</B>")
    content = content[startIndex:endIndex]

    regex_deaths = r'valign="top" >([^<]+)</td><td>(.+?)</td></tr>'
    pattern = re.compile(regex_deaths,re.MULTILINE+re.S)
    matches = re.findall(pattern,content.decode())

    for m in matches:
        deathTime = ""
        deathLevel = ""
        deathKiller = ""
        deathByPlayer = False
        regex_deathtime = r'(\w+).+?;(\d+).+?;(\d+).+?;(\d+):(\d+):(\d+).+?;(\w+)'
        pattern = re.compile(regex_deathtime,re.MULTILINE+re.S)
        m_deathtime = re.search(pattern,m[0])
        
        if m_deathtime:
            deathTime = "{0} {1} {2} {3}:{4}:{5} {6}".format(m_deathtime.group(1),m_deathtime.group(2),m_deathtime.group(3),m_deathtime.group(4),m_deathtime.group(5),m_deathtime.group(6),m_deathtime.group(7))
         
        if m[1].find("Died") != -1:
            regex_deathinfo_monster = r'Level (\d+) by ([^.]+)'
            pattern = re.compile(regex_deathinfo_monster,re.MULTILINE+re.S)
            m_deathinfo_monster = re.search(pattern,m[1])
            if m_deathinfo_monster:
                deathLevel = m_deathinfo_monster.group(1)
                deathKiller = m_deathinfo_monster.group(2)
        else:
            regex_deathinfo_player = r'Level (\d+) by .+?name=([^"]+)'
            pattern = re.compile(regex_deathinfo_player,re.MULTILINE+re.S)
            m_deathinfo_player = re.search(pattern,m[1])
            if m_deathinfo_player:
                deathLevel = m_deathinfo_player.group(1)
                deathKiller = urllib.parse.unquote_plus(m_deathinfo_player.group(2))
                deathByPlayer = True

        deathList.append({'time': deathTime, 'level' : deathLevel, 'killer' : deathKiller, 'byPlayer' : deathByPlayer})
        if(singleDeath):
            break
    return deathList

def getServerOnline(server):
    onlineList = []
    content = ""
    retry = 0
    while content == "" and retry < 5:
        try:
            page = urllib.request.urlopen('https://secure.tibia.com/community/?subtopic=worlds&world='+server)
            content = page.read()
        except Exception:
            retry=retry+1
    
    if content == "":
        print("Error in getServerOnline("+server+")")
        return onlineList
    
    try:
        content.decode().index("Vocation&#160;&#160;")
    except Exception:
        return onlineList
    
    startIndex = content.decode().index('Vocation&#160;&#160;')
    endIndex = content.decode().index('Search Character')
    content = content[startIndex:endIndex]
    
    
    regex_members = r'<a href="https://secure.tibia.com/community/\?subtopic=characters&name=(.+?)" >.+?</a></td><td style="width:10%;" >(.+?)</td>'
    pattern = re.compile(regex_members,re.MULTILINE+re.S)

    m = re.findall(pattern,content.decode())
    #Check if list is empty
    if m:
        #Building dictionary list from online players
        for (name, level) in m:
            name = urllib.parse.unquote_plus(name)
            onlineList.append({'name' : name.title(), 'level' : int(level)})
    return onlineList

def getGuildOnline(guildname):
    #Fetch webpage
    content = ""
    retry = 0
    while content == "" and retry < 5:
        try:
            page = urllib.request.urlopen('https://secure.tibia.com/community/?subtopic=guilds&page=view&GuildName='+urllib.parse.quote(guildname)+'&onlyshowonline=1')
            content = page.read()
        except Exception:
            retry=retry+1

    if content == "":
        print("Error in getGuildOnline("+guildname+")")
        return 'NO'
    #Check if guild exists (in a really lazy way)
    try:
        content.decode().index("Information")
    except Exception:
        return 'NE'
    #Trimming content string to reduce load
    startIndex = content.decode().index("<td>Status</td>")
    endIndex = content.decode().index("name=\"Show All\"")
    content = content[startIndex:endIndex]

    #Regex pattern to fetch information
    regex_members = r'<TD>(.+?)</TD>\s</td><TD><A HREF="https://secure.tibia.com/community/\?subtopic=characters&name=(.+?)">.+?</A> *\(*(.*?)\)*</TD>\s<TD>(.+?)</TD>\s<TD>(.+?)</TD>\s<TD>(.+?)</TD>'
    pattern = re.compile(regex_members,re.MULTILINE+re.S)

    m = re.findall(pattern,content.decode())
    member_list = [];
    #Check if list is empty
    if m:
        #Building dictionary list from members
        for (rank, name, title, vocation, level, joined) in m:
            rank = '' if (rank == '&#160;') else rank
            name = urllib.parse.unquote_plus(name)
            joined = joined.replace('&#160;','-')
            member_list.append({'rank' : rank, 'name' : name, 'title' : title,
            'vocation' : vocation, 'level' : level, 'joined' : joined})
        return member_list
    
    return 'NO'

def getPlayer(name):
    print("ayyyyy get le player")
    char = {'guild' : ''}
    #Fetch website
    content = ""
    retry = 0
    while content == "" and retry < 5:
        try:
            page = urllib.request.urlopen('https://secure.tibia.com/community/?subtopic=characters&name='+urllib.parse.quote(name))
            content = page.read()
        except Exception:
            retry=retry+1

    if content == "":
        print("Error in getPlayer("+name+")")
        return
    #Check if player exists (in a really lazy way)
    try:
        content.decode().index("Vocation:")
    except Exception:
        return
    #Trimming content to reduce load
    startIndex = content.decode().index("BoxContent")
    endIndex = content.decode().index("<B>Search Character</B>")
    content = content[startIndex:endIndex]

    #TODO: Is there a way to reduce this part?
    #Name
    m = re.search(r'Name:</td><td>([^<]+)\s',content.decode())
    if m:
        char['name'] = m.group(1).strip()

    #Vocation
    m = re.search(r'Vocation:</td><td>([^<]+)',content.decode())
    if m:
        char['vocation'] = m.group(1)

    #Level
    m = re.search(r'Level:</td><td>(\d+)',content.decode())
    if m:
        char['level'] = int(m.group(1))

    #World
    m = re.search(r'World:</td><td>([^<]+)',content.decode())
    if m:
        char['world'] = m.group(1)

    #Residence (City)        
    m = re.search(r'Residence:</td><td>([^<]+)',content.decode())
    if m:
        char['residence'] = m.group(1)

    #Sex, only stores pronoun
    m = re.search(r'Sex:</td><td>([^<]+)',content.decode())
    if m:
        if m.group(1) == 'male':
            char['pronoun'] = 'He'
        else:
            char['pronoun'] = 'She'
            
    #Guild rank
    m = re.search(r'membership:</td><td>([^<]+)\sof the',content.decode())
    if m:
        char['rank'] = m.group(1)
        #Guild membership
        m = re.search(r'GuildName=.*?([^"]+).+',content.decode())
        if m:
            char['guild'] = urllib.parse.unquote_plus(m.group(1))
        
    return char

def getItem(name):
    #Reading item database
    c = sqlite3.connect('Database.db').cursor()
    #Search query
    c.execute("SELECT title, vendor_value FROM Items WHERE name LIKE ?",(name,))
    result = c.fetchone()
    #Checking if item exists
    if(result is not None):
        #Turning result tuple into dictionary
        item = dict(zip(['name','value'],result))
        #Checking NPCs that buy the item
        c.execute("SELECT NPCs.title, city FROM Items, SellItems, NPCs WHERE Items.name LIKE ? AND SELLItems.itemid = Items.id AND NPCs.id = vendorid AND vendor_value = value",(name,))
        npcs = []
        for row in c:
            name = row[0]
            city = row[1].title()
            #Replacing cities for special npcs
            if(name == 'Alesar' or name == 'Yaman'):
                city = 'Green Djinn\'s Fortress'
            elif(name == 'Nah\'Bob' or name == 'Haroun'):
                city = 'Blue Djinn\'s Fortress'
            elif(name == 'Rashid'):
                city = [
                    "Svargrond",
                    "Liberty Bay",
                    "Port Hope",
                    "Ankrahmun",
                    "Darashia",
                    "Edron",
                    "Carlin"][date.today().weekday()]
            elif(name == 'Yasir'):
                city = 'his boat'
            npcs.append({"name" : name, "city": city})
        item['npcs'] = npcs
        return item
    return
    
def getLocalTime(tibiaTime):
    #Getting local time and GMT
    t = time.localtime()
    u = time.gmtime(time.mktime(t))
    #UTC Offset
    local_utc_offset = ((timegm(t) - timegm(u))/60/60)

    #Convert time string to time object
    #Removing timezone cause CEST and CET are not supported
    t = datetime.strptime(tibiaTime[:-4].strip(), "%b %d %Y %H:%M:%S")
    #Extracting timezone
    tz = tibiaTime[-4:].strip()

    #Getting the offset
    if(tz == "CET"):
        utc_offset = 1
    elif(tz == "CEST"):
        utc_offset = 2
    else:
        return None
    #Add/substract hours to get the real time
    return t + timedelta(hours=(local_utc_offset - utc_offset))
    
def getTimeDiff(time):
    if not isinstance(time, timedelta):
        return None
    hours = time.seconds//3600
    minutes = (time.seconds//60)%60
    if time.days > 1:
        return "{0} days ago".format(time.days)
    if time.days == 1:
        return "1 day ago"
    if hours > 1:
        return "{0} hours ago".format(hours)
    if hours == 1:
        return "1 hour ago"
    if minutes > 20:
        return "{0} minutes ago".format(minutes)
    else:
        return "moments ago"
    
####################### Commands #######################

class Tibia():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True,aliases=['player','checkplayer','char'])
    @asyncio.coroutine
    def check(self,ctx,*name : str):
        """Tells you information about a character"""
        name = " ".join(name)
        char = getPlayer(name)
        if char:
            replyF = "**{1}** is a level {2} __{3}__. {0} resides in __{4}__ in the world __{5}__.{6}"
            guildF = "\n{0} is __{1}__ of the **{2}**."
            if(char['guild']):
                guild = guildF.format(char['pronoun'],char['rank'],char['guild'])
            else:
                guild = ""
            reply = replyF.format(char['pronoun'],char['name'],char['level'],char['vocation'],char['residence'],char['world'],guild)
            yield from self.bot.say(reply)
        else:
            yield from self.bot.say("That character doesn't exist.")

    @commands.command(pass_context=True,aliases=['expshare','party'])
    @asyncio.coroutine
    def share(self,ctx,*param : str):
        """Shows the sharing range for that level or character"""
        level = 0
        name = ''
        #Check if param is numeric
        try:
            level = int(param[0])
        #If it's not numeric, then it must be a char's name
        except ValueError:
            name = " ".join(param)
            char = getPlayer(name)
            if char:
                level = int(char['level']);
                name = char['name'];
            else:
                yield from self.bot.say('There is no character with that name.');
                return
        if(level <= 0):
            replies = ["Invalid level.", "I don't think that's a valid level.",
            "You're doing it wrong!", "Nope, you can't share with anyone.",
            "You probably need a couple more levels"]
            yield from self.bot.say(random.choice(replies))
            return
        low = int(math.ceil(level*2.0/3.0))
        high = int(math.floor(level*3.0/2.0))
        if(name == ''):
            yield from self.bot.say('A level '+str(level)+' can share experience with levels **'+str(low)+
        '** to **'+str(high)+'**.')
        else:
            yield from self.bot.say('**'+name+'** ('+str(level)+') can share experience with levels **'+str(low)+
        '** to **'+str(high)+'**.')
            
        

    @commands.command(pass_context=True,aliases=['guildcheck'])
    @asyncio.coroutine
    def guild(self,ctx,*guildname : str):
        """Checks who is online in a guild"""
        guildname = " ".join(guildname).title()
        onlinelist = getGuildOnline(guildname)
        if onlinelist == 'NE':
            yield from self.bot.say('The guild '+urllib.parse.unquote_plus(guildname)+' doesn\'t exist.')
        elif onlinelist == 'NO':
            yield from self.bot.say('Nobody is online on '+urllib.parse.unquote_plus(guildname)+'.')
        else:
            result = ('There '+
            ('are' if (len(onlinelist) > 1) else 'is')+' '+str(len(onlinelist))+' player'+
            ('s' if (len(onlinelist) > 1) else '')+' online in **'+guildname+'**:')
            for member in onlinelist:
                result += '\n'  
                if(member['rank'] != ''):
                    result += '__'+member['rank']+'__\n'
                result += '\t'+member['name']
                result += (' (*'+member['title']+'*)' if (member['title'] != '') else '')
                result += ' -- '+member['level']+' '
                vocAbb = {'None' : 'N', 'Druid' : 'D', 'Sorcerer' : 'S', 'Paladin' : 'P', 'Knight' : 'K',
                'Elder Druid' : 'ED', 'Master Sorcerer' : 'MS', 'Royal Paladin' : 'RP', 'Elite Knight' : 'EK'}
                try:
                    result += vocAbb[member['vocation']]
                except KeyError:
                    result += 'N'            
                
            yield from self.bot.say(result)
            
            
    @commands.command(aliases=['checkprice','item'])
    @asyncio.coroutine
    def itemprice(self,*itemname : str):
        """Checks an item's highest NPC price"""
        itemname = " ".join(itemname).strip()
        item = getItem(itemname)
        if(item is not None):   
            #Check if item has npcs that buy the item
            if('npcs' in item and len(item['npcs']) > 0):
                reply = "**{0}** can be sold for {1:,} gold coins to:".format(item['name'],item['value'])
                for npc in item['npcs']:
                    reply += "\n\t**{0}** in *{1}*".format(npc['name'],npc['city'])
                yield from self.bot.say(reply)
            else:
                yield from self.bot.say('**'+item['name']+'** can\'t be sold to NPCs.')
        else:
            yield from self.bot.say("I couldn't find an item with that name.")
            
    @commands.command()
    @asyncio.coroutine
    def deaths(self,*name : str):
        name = " ".join(name).strip()
        deaths = getPlayerDeaths(name)
        if(deaths is None):
            yield from self.bot.say("That character doesn't exists!")
            return
        if(len(deaths) == 0):
            yield from self.bot.say(name.title()+" hasn't died recently.")
            return
        
        reply = name.title()+" recent deaths:"
        for death in deaths:
            diff = getTimeDiff(datetime.now() - getLocalTime(death['time']))
            died = "Killed" if death['byPlayer'] else "Died"
            reply += "\n\t{0} at level **{1}** by {2} - *{3}*".format(died,death['level'],death['killer'],diff)
            
        yield from self.bot.say(reply)
        

def setup(bot):
    bot.add_cog(Tibia(bot))