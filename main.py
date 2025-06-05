from sql import ValorSQL
from dotenv import load_dotenv
import platform, multiprocessing, discord, os, valor, commands, logging, time, asyncio, aiomysql

# this is supposedly "unsafe" on macos, but is the default on unix.
# alternatively use forkserver (or spawn, which breaks because it's unfreezable) instead of fork
if platform.mac_ver()[0]:
    multiprocessing.set_start_method("fork")

load_dotenv()
# set to GMT time
os.environ["TZ"] = "Europe/London"
time.tzset()

logging.basicConfig(format='%(asctime)s %(message)s')
logging.getLogger().setLevel(logging.INFO)
logging.warning("Starting")

loop = asyncio.get_event_loop()
valor = valor.Valor('-', intents=discord.Intents.all())

async def main():
    @valor.event
    async def on_ready():
        await valor.tree.sync()

    async with valor:
        ValorSQL.pool = await aiomysql.create_pool(**ValorSQL._info, loop=valor.loop)
        
        await commands.register_all(valor)
        
        await asyncio.gather(
            asyncio.ensure_future(valor.run()),
        )
        

asyncio.run(main())