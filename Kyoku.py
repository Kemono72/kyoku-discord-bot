import discord
from discord.ext import commands
import youtube_dl
import asyncio

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=':p ', intents=intents)

queues = {}

def check_queue(ctx, voice):
    if queues.get(ctx.guild.id):
        source = queues[ctx.guild.id].pop(0)
        voice.play(source, after=lambda x=None: check_queue(ctx, voice))

@bot.event
async def on_ready():
    print(f'Bot connected as {bot.user}')

@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
    else:
        await ctx.send("You're not in a voice channel!")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.guild.voice_client.disconnect()
    else:
        await ctx.send("I'm not in a voice channel!")

@bot.command()
async def play(ctx, *, url):
    if ctx.voice_client is None:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.send("Join a voice channel first!")
            return

    ydl_opts = {'format': 'bestaudio', 'noplaylist': 'True'}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        url2 = info['formats'][0]['url']
        source = await discord.FFmpegOpusAudio.from_probe(url2, method='fallback')

        if ctx.voice_client.is_playing():
            if ctx.guild.id in queues:
                queues[ctx.guild.id].append(source)
            else:
                queues[ctx.guild.id] = [source]
            await ctx.send("Added to queue.")
        else:
            ctx.voice_client.play(source, after=lambda x=None: check_queue(ctx, ctx.voice_client))
            await ctx.send(f"Now playing: {info['title']}")

@bot.command()
async def pause(ctx):
    if ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("Paused ⏸")

@bot.command()
async def resume(ctx):
    if ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("Resumed ▶")

@bot.command()
async def skip(ctx):
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("Skipped ⏭")

@bot.command()
async def queue(ctx):
    if ctx.guild.id in queues and queues[ctx.guild.id]:
        await ctx.send(f"Queue has {len(queues[ctx.guild.id])} songs queued.")
    else:
        await ctx.send("Queue is empty!")

