from valor import Valor
from discord.ext.commands import Context
from util import ErrorEmbed, LongTextEmbed
from datetime import datetime
from util import SettingsManager
import requests

async def _register_join(valor: Valor):
    desc = "Gets you the join date of a player to the guild."
    manager = SettingsManager()
    
    @valor.command()
    async def join(ctx: Context, username: str):
        server_id = ctx.guild.id
        guild_name = manager.get(server_id, "guild_name")

        if not guild_name:
            return await ctx.send(embed=ErrorEmbed(
                "Guild name is not set for this server. Use `-settings set guild_name <name>` to configure it."
            ))
    
        user_data = requests.get(f"https://api.wynncraft.com/v3/guild/{guild_name}").json()
        users = []
        for k, v in user_data["members"].items():
            if k != "total":
                for name, value in v.items():
                    value["name"] = name
                    users.append(value)
        
        for m in users:
            if m["name"] == username:
                ezjoin = datetime.fromisoformat(m["joined"][:-1])
                return await LongTextEmbed.send_message(valor, ctx, "Most Recent Join Date of %s" % username, ezjoin.strftime("%d %b %Y %H:%M:%S.%f UTC"), color=0xFF00)
        
        await ctx.send(embed=ErrorEmbed("%s isn't in the guild" % username))

    @join.error
    async def cmd_error(ctx, error: Exception):
        await ctx.send(embed=ErrorEmbed())
        raise error
    
    @valor.help_override.command()
    async def join(ctx: Context):
        await LongTextEmbed.send_message(valor, ctx, "Join", desc, color=0xFF00)
    
    
    
