from valor import Valor
from discord.ext.commands import Context
from discord.ui import Select, View
from discord import File
from util import ErrorEmbed, LongTextEmbed
from PIL import Image, ImageFont, ImageDraw
from sql import ValorSQL
from commands.common import from_uuid
import discord, asyncio, time, os, aiohttp

class LeaderboardSelect(Select):
    def __init__(self, options):
        super().__init__(options=options, placeholder="Select a stat to view its leaderboard.", row=0)
    
    async def callback(self, interaction: discord.Interaction):
        self.view.page = 0
        self.is_fancy = self.view.is_fancy
        board = await get_leaderboard(self.values[0], self.view.page, self.is_fancy)

        self.embed.title = f"Leaderboard for {self.values[0]}"
        self.embed.set_footer(text=f"Page {self.view.page+1} | Use arrow buttons to switch between pages.")
        if self.is_fancy:
            self.embed.set_image(url="attachment://leaderboard.png")
            self.embed.description = ""
            await interaction.response.edit_message(embed=self.embed, view=self.view, attachments=[board])
        else:
            self.embed.description = board
            self.embed.set_image(url=None)
            await interaction.response.edit_message(embed=self.embed, view=self.view, attachments=[])



class LeaderboardView(View):
    def __init__(self, default, stat_set):
        super().__init__()
        self.page = 0
        self.is_fancy = False

        self.stats = [stat_set[i:i + 25] for i in range(0, len(stat_set), 25)] # split into pages of 25 because discord limits select menus to 25 options
        self.max_page = 4

        for sublist in self.stats:
            if default in sublist:
                self.page = self.stats.index(sublist)
                break
        select_options = [discord.SelectOption(label=stat) for stat in self.stats[self.page]]
        self.select = LeaderboardSelect(options=select_options)
        self.select.values.append("galleons_graveyard")
        self.add_item(self.select)

    
    @discord.ui.button(emoji="⬅️", row=1)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page -= 1
        if self.page < 0:
            self.page = 0
            await interaction.response.send_message("You are at the first page!", ephemeral=True)
        else:
            await self.update(interaction)
    
    @discord.ui.button(emoji="➡️", row=1)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page += 1
        if self.page > self.max_page:
            self.page = self.max_page
            await interaction.response.send_message("You are at the last page!", ephemeral=True)
        else:
            await self.update(interaction)
    
    @discord.ui.button(emoji="✨", row=1)
    async def fancy(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.is_fancy = not self.is_fancy
        await self.update(interaction)

    async def update(self, interaction: discord.Interaction):
        self.select.options = [discord.SelectOption(label=stat) for stat in self.stats[0]]
        self.select.embed.set_footer(text=f"Page {self.page+1} | Use arrow buttons to switch between pages.")
        await interaction.response.defer()
        board = await get_leaderboard(self.select.values[0], self.page, self.is_fancy)
        self.embed = self.select.embed

        self.embed.title = f"Leaderboard for {self.select.values[0]}"
        if self.is_fancy:
            self.embed.set_image(url="attachment://leaderboard.png")
            self.embed.description = ""
            await interaction.edit_original_response(embed=self.embed, view=self, attachments=[board])
        else:
            self.embed.description = board
            self.embed.set_image(url=None)
            await interaction.edit_original_response(embed=self.embed, view=self, attachments=[])

async def download_model(session, url, filename):
    user_agent = {'User-Agent': 'valor-bot/1.0'}
    try:
        async with session.get(url, headers=user_agent) as response:
            if response.status == 200:
                content = await response.read()
                with open(filename, "wb") as f:
                    f.write(content)
            else:
                print(f"Failed to fetch {url}: {response.status}")
    except Exception as e:
        print(f"Error fetching {url}: {e}")

async def fetch_all_models(rows):
    model_base = "https://visage.surgeplay.com/bust/"
    tasks = []
    now = time.time()
    async with aiohttp.ClientSession() as session:
        for row in rows:
            if row[0]:
                filename = f"/tmp/{row[0]}_model.png"
                url = model_base + row[0] + '.png'

                if not os.path.exists(filename) or now - os.path.getmtime(filename) > 24 * 3600:
                    tasks.append(download_model(session, url, filename))
        await asyncio.gather(*tasks)  # Run all downloads in parallel

async def get_leaderboard(stat, page, is_fancy: bool):
    if stat == "raids":
        res = await ValorSQL._execute("SELECT uuid_name.name, uuid_name.uuid, player_stats.the_canyon_colossus + player_stats.nexus_of_light + player_stats.the_nameless_anomaly + player_stats.nest_of_the_grootslangs FROM player_stats LEFT JOIN uuid_name ON uuid_name.uuid=player_stats.uuid ORDER BY player_stats.the_canyon_colossus + player_stats.nexus_of_light + player_stats.the_nameless_anomaly + player_stats.nest_of_the_grootslangs DESC LIMIT 50")
    elif stat == "dungeons":
        res = await ValorSQL._execute("SELECT uuid_name.name, uuid_name.uuid, player_stats.decrepit_sewers + player_stats.corrupted_decrepit_sewers + player_stats.infested_pit + player_stats.corrupted_infested_pit + player_stats.corrupted_underworld_crypt + player_stats.underworld_crypt + player_stats.lost_sanctuary + player_stats.corrupted_lost_sanctuary + player_stats.ice_barrows + player_stats.corrupted_ice_barrows + player_stats.corrupted_undergrowth_ruins + player_stats.undergrowth_ruins + player_stats.corrupted_galleons_graveyard + player_stats.galleons_graveyard + player_stats.fallen_factory + player_stats.eldritch_outlook + player_stats.corrupted_sand_swept_tomb + player_stats.sand_swept_tomb + player_stats.timelost_sanctum FROM player_stats LEFT JOIN uuid_name ON uuid_name.uuid=player_stats.uuid ORDER BY player_stats.decrepit_sewers + player_stats.corrupted_decrepit_sewers + player_stats.infested_pit + player_stats.corrupted_infested_pit + player_stats.corrupted_underworld_crypt + player_stats.underworld_crypt + player_stats.lost_sanctuary + player_stats.corrupted_lost_sanctuary + player_stats.ice_barrows + player_stats.corrupted_ice_barrows + player_stats.corrupted_undergrowth_ruins + player_stats.undergrowth_ruins + player_stats.corrupted_galleons_graveyard + player_stats.galleons_graveyard + player_stats.fallen_factory + player_stats.eldritch_outlook + player_stats.corrupted_sand_swept_tomb + player_stats.sand_swept_tomb + player_stats.timelost_sanctum DESC LIMIT 50")
    else:
        res = await ValorSQL._execute(f"SELECT uuid_name.name, uuid_name.uuid, player_stats.{stat} FROM player_stats LEFT JOIN uuid_name ON uuid_name.uuid=player_stats.uuid ORDER BY {stat} DESC LIMIT 50")
    stats = []
    for m in res:
        if not m[0] and m[1]:
            stats.append((await from_uuid(m[1]), m[2]))
        else:
            stats.append((m[0] if m[0] else "can't find name", m[2]))
    
    if not is_fancy:
        start = page * 10
        end = start + 10
        return "```isbl\n" + '\n'.join("%3d. %24s %5d" % (i+1, stats[i][0], stats[i][1]) for i in range(start, min(end, len(stats)))) + "\n```"

    
        
    stats_list = []
    for i in range(len(stats)):
        stats_list.append([i+1, stats[i][0], stats[i][1]])

        
    rank_margin = 45
    model_margin = 115
    name_margin = 205
    value_margin = 685

    font = ImageFont.truetype("MinecraftRegular.ttf", 20)
    board = Image.new("RGBA", (730, 695), (110, 110, 110))
    overlay = Image.open("assets/overlay.png")
    overlay2 = Image.open("assets/overlay2.png")
    overlay_toggle = True
    draw = ImageDraw.Draw(board)

    await fetch_all_models(stats)

    for i in range(1, 11):
        stat = stats_list[(i-1)+(page*10)]
        height = ((i-1)*69)+5
        board.paste(overlay if overlay_toggle else overlay2, (5, height), overlay)
        overlay_toggle = not overlay_toggle
        match stat[0]:
            case 1:
                color = "yellow"
            case 2:
                color = (170,169,173,255)
            case 3:
                color = (169,113,66,255)
            case _:
                color = "white"
        try:
            model_img = Image.open(f"/tmp/{stat[1]}_model.png", 'r')
            model_img = model_img.resize((64, 64))
        except Exception as e:
            model_img = Image.open(f"assets/unknown_model.png", 'r')
            model_img = model_img.resize((64, 64))
            print(f"Error loading image: {e}")

        board.paste(model_img, (model_margin, height), model_img)
        draw.text((rank_margin, height+22), "#"+str(stat[0]), fill=color, font=font)
        draw.text((name_margin, height+22), str(stat[1]), font=font)
        draw.text((value_margin, height+22), str(stat[2]), font=font, anchor="rt")


    board.save("/tmp/leaderboard.png")

    return File("/tmp/leaderboard.png", filename="leaderboard.png")


async def _register_leaderboard(valor: Valor):
    desc = "The leaderboard"
    stat_set = ['sand_swept_tomb', 'galleons_graveyard', 'firstjoin', 'scribing', 'chests_found', 'woodcutting', 'tailoring', 'fishing', 'eldritch_outlook', 'alchemism', 'logins', 'deaths', 'corrupted_decrepit_sewers', 'armouring', 'corrupted_undergrowth_ruins', 'items_identified', 'nest_of_the_grootslangs', 'blocks_walked', 'lost_sanctuary', 'mining', 'the_canyon_colossus', 'undergrowth_ruins', 'corrupted_ice_barrows', 'jeweling', 'woodworking', 'uuid', 'underworld_crypt', 'fallen_factory', 'mobs_killed', 'infested_pit', 'decrepit_sewers', 'corrupted_sand_swept_tomb', 'corrupted_infested_pit', 'farming', 'corrupted_lost_sanctuary', 'cooking', 'guild', 'combat', 'weaponsmithing', 'playtime', 'corrupted_underworld_crypt', 'ice_barrows', 'nexus_of_light', "guild_rank", "the_nameless_anomaly", "raids", "corrupted_galleons_graveyard", "timelost_sanctum", "dungeons"]
    stats_abbr = {'tna' : 'the_nameless_anomaly', 'notg' : 'nest_of_the_grootslangs', 'sst' : 'sand_swept_tomb', 'gg' : 'galleons_graveyard', 'cgg' : 'corrupted_galleons_graveyard', 'csst' : 'corrupted_sand_swept_tomb', 'cds' : 'corrupted_decrepit_sewers', 'ds' : 'decrepit_sewers', 'cur' :'corrupted_undergrowth_ruins', 'ur' : 'undergrowth_ruins', 'tcc' : 'the_canyon_colossus', 'ib' : 'ice_barrows', 'cib' : 'corrupted_ice_barrows', 'uc' : 'underworld_crypt', 'cuc' : 'corrupted_underworld_crypt', 'ff' : 'fallen_factory', 'ip' : 'infested_pit', 'cip' : 'corrupted_infested_pit', 'ls' : 'lost_sanctuary', 'cls' : 'corrupted_lost_sanctuary', 'nol' : 'nexus_of_light', }
    
    @valor.command()
    async def leaderboard(ctx: Context, stat="galleons_graveyard"): 

        if stat in stats_abbr:
            stat = stats_abbr[stat]
        
        if stat not in stat_set:
            return await LongTextEmbed.send_message(valor, ctx, "Invalid Stat, choose from the following: ", content='\n'.join(stat_set), code_block=True, color=0x1111AA)
        
        view = LeaderboardView(stat, stat_set)
        view.select.values[0] = stat
        view.page = 0

        board = await get_leaderboard(stat, 0, view.is_fancy)
        
        view.select.embed = discord.Embed(
            title=f"Leaderboard for {stat}",
            description=board,
            color=0x333333,
        )
        view.select.embed.set_footer(text=f"Page {view.page+1} | Use arrow buttons to switch between pages.")
        await ctx.send(embed=view.select.embed, view=view)

    @leaderboard.error
    async def cmd_error(ctx, error: Exception):
        await ctx.send(embed=ErrorEmbed())
        raise error
    
    @valor.help_override.command()
    async def leaderboard(ctx: Context):
        await LongTextEmbed.send_message(valor, ctx, "Leaderboard", desc, color=0xFF00)
