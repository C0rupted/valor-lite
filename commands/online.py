from valor import Valor
from discord.ext.commands import Context
from util import ErrorEmbed, LongTextEmbed
from .common import guild_name_from_tag
import discord, argparse, requests

async def _register_online(valor: Valor):
    desc = "Online: shows who's online in a guild\nThe new command is formatted like this: -online -g <guild_TAG>.\n For example: -online -g ano"

    parser = argparse.ArgumentParser(description='Online command')
    parser.add_argument('-g', '--guild', type=str)
    
    @valor.command()
    async def online(ctx: Context, *options):
        try:
            opt = parser.parse_args(options)
        except:
            return await LongTextEmbed.send_message(valor, ctx, "Online", parser.format_help().replace("main.py", "-online"), color=0xFF00)
        
        guild = await guild_name_from_tag(opt.guild)

        res = requests.get(valor.endpoints["guild"].format(guild)).json()

        if "members" not in res:
            return await ctx.send(embed=ErrorEmbed("Guild doesn't exist."))

        # add the rank name along with wc
        # online_rn = [(p, k, members[p]) for k in all_players for p in all_players[k] if p in members]
        online_rn = [(name, member["server"], rank) for rank, v in res["members"].items() if rank != "total" for name, member in v.items() if member["online"]]
        
        if not len(online_rn):
            return await LongTextEmbed.send_message(valor, ctx, f"{guild} Members Online", "There are no members online.", color = 0xFF)
        print(online_rn)

        rank_dict = {
            "recruit": "",
            "recruiter": "*",
            "captain": "**",
            "strategist": "***",
            "chief": "****",
            "owner": "*****"
        }

        desc = "```isbl\n"
        desc += "Name            ┃ Rank  ┃ World\n"
        desc += "━━━━━━━━━━━━━━━━╋━━━━━━━╋━━━━━━\n"
        for player in online_rn:
            t = player[0]
            t += (16 - len(player[0])) * " "
            t += "┃ " + rank_dict[player[2]]
            t += (5 - len(rank_dict[player[2]])) * " "
            t += " ┃ " + player[1] + "\n"
            
            desc += t
        desc += "```"


        embed = discord.Embed(title=f"Members of {guild} online ({len(online_rn)})", description=desc, color=0x7785cc)
        await ctx.send(embed=embed)

    
    
    @online.error
    async def cmd_error(ctx, error: Exception):
        await ctx.send(embed=ErrorEmbed("The command is formatted like this: -online -g <guild_TAG>.\n For example: -online -g ANO"))
        print(error.with_traceback())
    
    @valor.help_override.command()
    async def online(ctx: Context):
        await LongTextEmbed.send_message(valor, ctx, "Online", desc, color=0xFF00)
    
    
    