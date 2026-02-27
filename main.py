import discord
from discord.ext import commands
from discord import app_commands
import wavelink
import asyncio
from collections import defaultdict
from datetime import timedelta

TOKEN = ""

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="Shoko ", intents=intents)

queues = defaultdict(list)
cooldowns = {}

# ================= READY =================
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    node = wavelink.Node(
        uri="http://127.0.0.1:8080",
        password="292005"
    )

    await wavelink.Pool.connect(nodes=[node], client=bot)
    print("Lavalink connected")

    synced = await bot.tree.sync()
    print(f"Synced {len(synced)} global slash commands")

def format_duration(ms):
    return str(timedelta(seconds=ms // 1000))

def create_nowplaying_embed(track):
    
    embed = discord.Embed(
        title=f"Shoko Singer Play Song {track.title}",
        description=f"**{track.title}**",
        color=discord.Color.purple()
    )
    embed.add_field(name="Author", value=track.author, inline=True)
    embed.add_field(name="Duration", value=format_duration(track.length), inline=True)
    embed.set_thumbnail(
    url="https://cdn.prod.website-files.com/627128d862c9a44234848dda/689573cac182e13df4d06ef4_Rizki%20Apc.jpg"
)
    embed.set_image(
    url="https://cdn.prod.website-files.com/627128d862c9a44234848dda/64448bdcb67dfe8e5a4b6dab_MOUSEPAD-1-FULL.jpg"
    )

    return embed


async def ensure_voice(guild, user):
    if not user.voice:
        return None

    if guild.voice_client:
        return guild.voice_client

    return await user.voice.channel.connect(cls=wavelink.Player)


async def remove_cooldown(user_id):
    await asyncio.sleep(2)
    cooldowns.pop(user_id, None)


async def handle_play(guild, user, query, send_func):

    if user.id in cooldowns:
        return await send_func("Slow down spammer")

    cooldowns[user.id] = True
    asyncio.create_task(remove_cooldown(user.id))

    player: wavelink.Player = await ensure_voice(guild, user)
    if not player:
        return await send_func("Pls Join Voice Channel")

    tracks = await wavelink.Playable.search(query)

    if not tracks:
        return await send_func("Shoko get failed stream")

    track = tracks[0]

    if player.playing or player.paused:
        queues[guild.id].append(track)
        return await send_func("Add success PlayList")

    await player.play(track)
    await send_func(embed=create_nowplaying_embed(track),
                    view=PlayerControls(player))


async def play_next(player: wavelink.Player):
    guild_id = player.guild.id

    if queues[guild_id]:
        next_track = queues[guild_id].pop(0)
        await player.play(next_track)

        channel = player.guild.system_channel
        if channel:
            await channel.send(embed=create_nowplaying_embed(next_track),
                               view=PlayerControls(player))
    else:
        print("Queue empty - staying connected")


# ================= EVENTS =================
@bot.event
async def on_wavelink_track_end(payload):
    await play_next(payload.player)


@bot.event
async def on_wavelink_track_exception(payload):
    print("Track exception:", payload.exception)


# ================= BUTTON VIEW =================
class PlayerControls(discord.ui.View):
    def __init__(self, player):
        super().__init__(timeout=180)
        self.player = player

    @discord.ui.button(label="⏯", style=discord.ButtonStyle.primary)
    async def pause_resume(self, interaction: discord.Interaction, _):

        if self.player.paused:
            await self.player.pause(False)
            await interaction.response.send_message("▶ Resume", ephemeral=True)
        else:
            await self.player.pause(True)
            await interaction.response.send_message("⏸ Pause", ephemeral=True)

    @discord.ui.button(label="⏭", style=discord.ButtonStyle.secondary)
    async def skip(self, interaction: discord.Interaction, _):
        await self.player.stop()
        await interaction.response.send_message("⏭ Skipped", ephemeral=True)

    @discord.ui.button(label="⏹", style=discord.ButtonStyle.danger)
    async def stop(self, interaction: discord.Interaction, _):
        queues[self.player.guild.id].clear()
        await self.player.stop()
        await interaction.response.send_message("⏹ Stopped & Cleared", ephemeral=True)


# ================= PREFIX COMMAND =================
@bot.command()
async def join(ctx):
    if not ctx.author.voice:
        return await ctx.send("Pls Join Voice Channel")

    await ensure_voice(ctx.guild, ctx.author)
    await ctx.send("Shoko Joined voice channel")


@bot.command()
async def play(ctx, *, search: str):
    await handle_play(ctx.guild, ctx.author, search, ctx.send)


@bot.command()
async def queue(ctx):
    if not queues[ctx.guild.id]:
        return await ctx.send("Queue is empty")

    description = "\n".join(
        f"{i+1}. {t.title} ({format_duration(t.length)})"
        for i, t in enumerate(queues[ctx.guild.id])
    )

    embed = discord.Embed(title="📜 Music Queue",
                          description=description,
                          color=discord.Color.blue())

    await ctx.send(embed=embed)


@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Bye Bye")


# ================= SLASH COMMAND =================
@bot.tree.command(name="join", description="Join voice channel")
async def slash_join(interaction: discord.Interaction):
    if not interaction.user.voice:
        return await interaction.response.send_message("Pls Join Voice Channel")

    await ensure_voice(interaction.guild, interaction.user)
    await interaction.response.send_message("Shoko Joined voice channel")


@bot.tree.command(name="play", description="Play a song")
@app_commands.describe(search="Song name or URL")
async def slash_play(interaction: discord.Interaction, search: str):
    await interaction.response.defer()
    await handle_play(
        interaction.guild,
        interaction.user,
        search,
        interaction.followup.send
    )


@bot.tree.command(name="list", description="Show music list")
async def slash_queue(interaction: discord.Interaction):
    if not queues[interaction.guild.id]:
        return await interaction.response.send_message("list music is empty")

    description = "\n".join(
        f"{i+1}. {t.title} ({format_duration(t.length)})"
        for i, t in enumerate(queues[interaction.guild.id])
    )

    emed = discord.Embed(title="List Music",
                          description=description,
                          color=discord.Color.blue()
                          )
    embed.set_thumbnail(url="https://cdn.prod.website-files.com/627128d862c9a44234848dda/64dc8dfab3dfcf5fa53e042b_33.jpg")
    embed.set_image(url="https://cdn.prod.website-files.com/627128d862c9a44234848dda/644348eb0bdf182b2c582715_STARFIELD-FULL.jpg")

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="skip", description="Skip current song")
async def slash_skip(interaction: discord.Interaction):
    player = interaction.guild.voice_client
    if not player:
        return await interaction.response.send_message("Nothing playing")

    await player.stop()
    await interaction.response.send_message("⏭ Skipped")

@bot.tree.command(name="pause", description="Pause current song")
async def slash_pause(interaction: discord.Interaction):
    player: wavelink.Player = interaction.guild.voice_client

    if not player or not player.playing:
        return await interaction.response.send_message("Nothing playing")

    await player.pause(True)
    await interaction.response.send_message("⏸ Paused")

@bot.tree.command(name="resume", description="Resume current song")
async def slash_resume(interaction: discord.Interaction):
    player: wavelink.Player = interaction.guild.voice_client

    if not player or not player.paused:
        return await interaction.response.send_message("Nothing paused")

    await player.pause(False)
    await interaction.response.send_message("▶ Resumed")


@bot.tree.command(name="stop", description="Stop and clear queue")
async def slash_stop(interaction: discord.Interaction):
    player: wavelink.Player = interaction.guild.voice_client

    if not player:
        return await interaction.response.send_message("Nothing playing")

    queues[interaction.guild.id].clear()
    await player.stop()
    await interaction.response.send_message("⏹ Stopped & Cleared")




@bot.tree.command(name="leave", description="Leave voice channel")
async def slash_leave(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("Bye Bye")


bot.run(TOKEN)
