import os
from click import command
import discord
import asyncio
from discord.ext import commands
from discord.utils import get
from discord import FFmpegPCMAudio
from discord import TextChannel
from youtube_dl import YoutubeDL
from dotenv import load_dotenv
from discord.ext import tasks
from googleapiclient.discovery import build

#Todo
# 1 Queue list view feature
# 2 deleting song from queue choice
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')


client = commands.Bot(command_prefix=".")
api_key = "AIzaSyA_IZxnw_fv86H9bMOPyxfhD5Qg9BRopig"

class Player(commands.Cog):
    def __init__(self,client):
        self.client = client
        self.song_queue = {}
        self.chat_channel_id = None
        self.first_song_played = {}
        
        
    def setup(self):
        
        
        for guild in self.client.guilds:  
            print(guild.id)     
            self.song_queue[guild.id] = []
            self.first_song_played[guild.id] = False
    
    async def song_over(self,ctx):
        
        if(len(self.song_queue[ctx.message.guild.id]) > 0):
            print(ctx.message.guild.id)
            url = self.song_queue[ctx.message.guild.id][0]
            
            self.song_queue[ctx.message.guild.id].pop(0)
            
            await self.play_song(ctx,url)
        else:
            self.first_song_played[ctx.message.guild.id] = False
            
            
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{client.user} has connected to Discord')
        self.setup()
    
    async def play_song(self,ctx,url):
        YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
        FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_stream 1 -reconnect_delay_max 5', 'options': '-vn'
        }
        voice = ctx.message.guild.voice_client
        
        #text_channel.send(f"Playing {url}")

        if voice is None:            
            voice = get(client.voice_clients,guild=ctx.guild)
        if voice and voice.is_connected():
            channel = ctx.message.author.voice.channel        

            await voice.move_to(channel)
        else:
            channel = ctx.message.author.voice.channel        

            voice = await channel.connect()
        
        if not voice.is_playing():
            channel = ctx.message.author.voice.channel        

            if(self.first_song_played[ctx.message.guild.id] is False):
                for channel in ctx.guild.channels:
                    if channel.name == ctx.message.channel:
                        self.chat_channel_id = channel.id
                await ctx.send(f"Going to play {url}")
            with YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download = False)
            
            URL = info['url']
            print(info['title'])
            
            
            #await self.chat_channel.send(f"Playing")
            await voice.play(FFmpegPCMAudio(URL),after= lambda e : asyncio.run(self.song_over(ctx)))
            

            voice.is_playing()
        
            await ctx.send('Bot is playing')
        
        else :
            self.first_song_played[ctx.message.guild.id] = True
            self.song_queue[ctx.message.guild.id].append(url)
            print(ctx.message.guild.id)
            await ctx.send(f"this song added to queue {url}")
            print("song added to Queue")
            return
        
    

    @commands.command()
    async def join (self,ctx):
        channel = ctx.message.author.voice.channel
        voice = get(client.voice_clients,guild=ctx.guild)
        if voice and voice.is_connected():
            await voice.move_to(channel)
        else:
            voice = await channel.connect()

    @commands.command()
    async def p(self,ctx,*,title):
        youtube = build('youtube','v3',developerKey = api_key)


        request = youtube.search().list(q=title,part = 'snippet', type='video')
        res = request.execute()
        url = "https://www.youtube.com/watch?v="+ res['items'][0]['id']['videoId']
        await self.play_song(ctx,url)
    @commands.command()
    async def resume(self,ctx):
        voice = get(client.voice_clients, guild=ctx.guild)

        if not voice.is_playing():
            voice.resume()
            await ctx.send('Bot is resuming')

    @commands.command()
    async def pause(self, ctx):
        voice = get(client.voice_clients,guild=ctx.guild)

        if voice.is_playing():
            voice.pause()
            await ctx.send('Bot has been paused')

    @commands.command()
    async def stop(ctx):
        voice = get(client.voice_clients, guild=ctx.guild)

        if voice.is_playing():
            voice.stop()
            await ctx.send('Stopping...')

    @commands.command()
    async def s(self,ctx):
        voice = get(client.voice_clients,guild=ctx.guild)

        if voice.is_playing():
            voice.stop()
            if(len(self.song_queue) > 0):
                ctx.send("Skipping")
                asyncio.run(self.song_over(ctx))
    @commands.command()
    async def clear(ctx, amount=5):
        await ctx.channel.purge(limit=amount)
        await ctx.send("Messages have been cleared")

    @commands.command()
    async def check(ctx,name):
        print(name)
    
    @commands.command()
    async def leave(self,ctx):
        for x in client.voice_clients:
            if(x.guild == ctx.message.guild):
                return await x.disconnect()

        self.song_queue[ctx.message.guild.id] = []
        

    
client.add_cog(Player(client))


client.run(TOKEN)