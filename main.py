import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp
import asyncio
import os
import wavelink

Token = "YOUR_BOT_TOKEN"

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="Shoko ", intents=intents)

ytdl_opts = {
    "format": "bestaudio[ext=m4a]/bestaudio/best",
    "quiet": True,
    "default_search": "ytsearch",
    "noplaylist": True,
    "geo_bypass": True
}

ytdl = yt_dlp.YoutubeDL(ytdl_opts)
queues = {}


# ================= LAVALINK CONNECT =================
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Shoko ready as {bot.user}")

    node = wavelink.Node(
        uri="http://localhost:8080",
        password="youshallnotpass"  # đổi nếu bạn đã đổi trong application.yml
    )

    await wavelink.Pool.connect(client=bot, nodes=[node])
    print("Connected to Lavalink!")


# ================= QUEUE HANDLER =================
async def play_next_song(guild_id, channel):
    player: wavelink.Player = discord.utils.get(bot.voice_clients, guild__id=guild_id)

    if guild_id in queues and queues[guild_id]:
        next_url = queues[guild_id].pop(0)
        tracks = await wavelink.Playable.search(next_url)

        if tracks:
            track = tracks[0]
            await player.play(track)
            await channel.send(f"Shoko Play Song: **{track.title}**")
    else:
        await channel.send("End song, wait for the next song")


async def play_music(guild_id, channel, url):
    player: wavelink.Player = discord.utils.get(bot.voice_clients, guild__id=guild_id)

    if not player:
        return

    tracks = await wavelink.Playable.search(url)

    if not tracks:
        await channel.send("Shoko get failed stream")
        return

    track = tracks[0]
    await player.play(track)
    await channel.send(f"Shoko Play Song: **{track.title}**")


@bot.event
async def on_wavelink_track_end(payload):
    guild_id = payload.player.guild.id
    channel = payload.player.guild.system_channel

    if guild_id in queues and queues[guild_id]:
        next_url = queues[guild_id].pop(0)
        tracks = await wavelink.Playable.search(next_url)

        if tracks:
            await payload.player.play(tracks[0])
            if channel:
                await channel.send(f"Shoko Play Song: **{tracks[0].title}**")


# ================= PREFIX COMMANDS =================
@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        if ctx.voice_client:
            await ctx.voice_client.move_to(channel)
        else:
            await channel.connect(cls=wavelink.Player)
        await ctx.send("Shoko Joined voice channel")
    else:
        await ctx.send("Pls Join Voice Channel")


@bot.command()
async def play(ctx, *, search):
    if not ctx.voice_client:
        await ctx.invoke(join)

    guild_id = ctx.guild.id

    if guild_id not in queues:
        queues[guild_id] = []

    player: wavelink.Player = ctx.voice_client

    if player.playing:
        queues[guild_id].append(search)
        await ctx.send("Add success PlayList")
    else:
        await play_music(guild_id, ctx.channel, search)


@bot.command()
async def skip(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()
        await ctx.send("Skip Song")


@bot.command()
async def pause(ctx):
    if ctx.voice_client:
        ctx.voice_client.pause()
        await ctx.send("Pause")


@bot.command()
async def resume(ctx):
    if ctx.voice_client:
        ctx.voice_client.resume()
        await ctx.send("Resume")


@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        queues[ctx.guild.id] = []
        ctx.voice_client.stop()
        await ctx.send("Stop & Clear Queue")


@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Bye Bye")


# ================= SLASH COMMANDS =================
@bot.tree.command(name="join", description="Join voice channel")
async def slash_join(interaction: discord.Interaction):
    if interaction.user.voice:
        channel = interaction.user.voice.channel
        await channel.connect(cls=wavelink.Player)
        await interaction.response.send_message("Shoko Joined voice channel")
    else:
        await interaction.response.send_message("Pls Join Voice Channel")


@bot.tree.command(name="play", description="Play music from YouTube")
@app_commands.describe(search="Link hoặc tên bài hát")
async def slash_play(interaction: discord.Interaction, search: str):
    await interaction.response.defer()

    if not interaction.guild.voice_client:
        if interaction.user.voice:
            await interaction.user.voice.channel.connect(cls=wavelink.Player)
        else:
            await interaction.followup.send("Pls Join Voice Channel")
            return

    guild_id = interaction.guild.id

    if guild_id not in queues:
        queues[guild_id] = []

    player: wavelink.Player = interaction.guild.voice_client

    if player.playing:
        queues[guild_id].append(search)
        await interaction.followup.send("Add success PlayList")
    else:
        await play_music(guild_id, interaction.channel, search)
        await interaction.followup.send("Processing...")


@bot.tree.command(name="skip", description="Skip current song")
async def slash_skip(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        interaction.guild.voice_client.stop()
        await interaction.response.send_message("Skip Song")


@bot.tree.command(name="pause", description="Pause music")
async def slash_pause(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        interaction.guild.voice_client.pause()
        await interaction.response.send_message("Pause")


@bot.tree.command(name="resume", description="Resume music")
async def slash_resume(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        interaction.guild.voice_client.resume()
        await interaction.response.send_message("Resume")


@bot.tree.command(name="stop", description="Stop and clear queue")
async def slash_stop(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        queues[interaction.guild.id] = []
        interaction.guild.voice_client.stop()
        await interaction.response.send_message("Stop & Clear Queue")


@bot.tree.command(name="leave", description="Leave voice channel")
async def slash_leave(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("Bye Bye")


bot.run(Token)
