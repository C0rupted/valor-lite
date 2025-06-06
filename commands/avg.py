from valor import Valor
from util import avg_process
from util import ErrorEmbed, LongTextEmbed
from commands.common import guild_names_from_tags
from discord.ext.commands import Context
from dotenv import load_dotenv
import time, argparse, os

load_dotenv()
async def _register_avg(valor: Valor):
    desc = "Averages online activity data"
    parser = argparse.ArgumentParser(description='Average command')
    parser.add_argument('-r', '--range', nargs='+', default=None)
    parser.add_argument('-g', '--guild', nargs='+')
    
    @valor.command()
    async def avg(ctx: Context, *options):
        try:
            opt = parser.parse_args(options)
        except:
            return await LongTextEmbed.send_message(valor, ctx, "Avg", parser.format_help().replace("main.py", "-avg"), color=0xFF00)

        start = time.time()

        query = f"SELECT * FROM `guild_member_count` WHERE "
        unidentified = []
        if opt.guild:
            guild_names, unidentified = await guild_names_from_tags(opt.guild)
            query += "("+' OR '.join(["guild="+'"'+n+'"' for n in guild_names])+")" + " AND "

            if not guild_names:
                return await LongTextEmbed.send_message(
                    valor, ctx, f"Average Error", f"{unidentified} unknown", color=0xFF0000)
                
        start_time = start - 3600 * 24 * 7 #these should mimic default values if they ever change
        end_time = start
        
        if opt.range:
            query += f"time >= {start-3600*24*float(opt.range[0])} AND time <= {start-3600*24*float(opt.range[1])}"
        else:
            query += f"time >= {start-3600*24*7}"

        if opt.range:
           start_time = int(start - 3600 * 24 * float(opt.range[0]))
           end_time = int(start - 3600 * 24 * float(opt.range[1]))


        if (end_time - start_time) > (365 *24 * 3600):
           return await LongTextEmbed.send_message(valor, ctx, "avg Error", f" Maximum time range exceeded (365 days), ask an ANO chief if you need a longer timeframe.", color=0xFF0000)

        data_pts, content = await avg_process(query)
        
        end = time.time()

        unid_prefix = f"The following guilds are unidentified: {unidentified}\n" if unidentified else ""

        await LongTextEmbed.send_message(valor, ctx, f"Guild Averages {opt.guild if opt.guild else 'ALL'}", unid_prefix+content, color=0xFF0000, 
            footer = f"Query Took {end-start:.5}s - {data_pts:,} rows"
        )

    @valor.help_override.command()
    async def avg(ctx: Context):
        await LongTextEmbed.send_message(valor, ctx, "Plot", desc, color=0xFF00)
