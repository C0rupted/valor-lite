from valor import Valor
from discord import Embed
from discord.ext.commands import Context
from util import LongTextEmbed
import argparse, time, json, os

async def _register_annihilation(valor: Valor):
    desc = "Tracks and informs of the next Annihilation world event"
    parser = argparse.ArgumentParser(description='Annihilation tracker command')

    ANNI_EMBED_COLOR = 0x7A1507
    ANNI_FILE = os.environ["ANNI_TRACKER_FILE"]

    def load_annihilation():
        if not os.path.exists(ANNI_FILE):
            return None
        with open(ANNI_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return None

    @valor.command(aliases=["annie", "anni"])
    async def annihilation(ctx: Context, *options):
        try:
            opt = parser.parse_args(options)
        except:
            return await LongTextEmbed.send_message(
                valor, ctx, "Annihilation", parser.format_help().replace("main.py", "-annihilation"), color=ANNI_EMBED_COLOR
            )

        data = load_annihilation()
        if not data or data.get("timestamp", 0) < int(time.time()):
            return await ctx.send(embed=Embed(
                title="Annihilation Tracker",
                description="There is currently no Annihilation reported.",
                color=ANNI_EMBED_COLOR
            ))

        timestamp = data["timestamp"]
        return await ctx.send(embed=Embed(
            title="Annihilation Tracker",
            description=f"Next Annihilation is at <t:{timestamp}:f> (<t:{timestamp}:R>)",
            color=ANNI_EMBED_COLOR
        ))

    @valor.help_override.command()
    async def annihilation(ctx: Context):
        await LongTextEmbed.send_message(valor, ctx, "Annihilation", desc, color=0xFF00)
