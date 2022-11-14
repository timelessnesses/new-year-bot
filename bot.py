try:
    import uvloop

    uvloop.install()
except (ImportError, ModuleNotFoundError):
    pass

from dotenv import load_dotenv

load_dotenv()
import logging
import os

formatting = logging.Formatter("[%(asctime)s] - [%(levelname)s] [%(name)s] %(message)s")

logging.basicConfig(
    level=logging.NOTSET,
    format="[%(asctime)s] - [%(levelname)s] [%(name)s] %(message)s",
    datefmt="%Y/%m/%d %H:%M:%S",
)

log = logging.getLogger("NewYearBot")
log.setLevel(logging.NOTSET)

try:
    os.mkdir("logs")
except FileExistsError:
    pass
with open("logs/bot.log", "w") as f:
    f.write("")
b = logging.FileHandler("logs/bot.log", "a", "utf-8")
b.setFormatter(formatting)
log.addHandler(b)

# logging purposes

import asyncio
import datetime
import os
import signal
import ssl
import subprocess
import traceback

import discord
from discord.ext import commands
from dotenv import load_dotenv
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from config import config
from replit_support import start
from sql.sql import EasySQL

logging.getLogger("discord").setLevel(logging.WARNING)  # mute

bot = commands.Bot(command_prefix=config.prefix, intents=discord.Intents.all())
bot.log = log

observer = Observer()


class FileHandler(FileSystemEventHandler):
    def on_modified(self, event):
        log.info(f"File changed: {event.src_path}")
        if event.src_path.endswith(".py"):
            log.info("Reloading...")
            path = event.src_path.replace("\\", "/").replace("/", ".")[:-3]
            try:
                asyncio.run(bot.reload_extension(path))
                log.info(f"Reloaded {path}")
            except Exception as e:
                log.error(f"Failed to reload {path}")
                log.error(e)
                log.error(traceback.format_exc())


observer.schedule(FileHandler(), path="src", recursive=False)


def get_git_revision_short_hash() -> str:
    return (
        subprocess.check_output(["git", "rev-parse", "--short", "HEAD"])
        .decode("ascii")
        .strip()
    )


def get_version():
    is_updated = subprocess.check_output("git status -uno", shell=True).decode("ascii")

    if "modified" in is_updated:
        is_updated = None
    elif (
        "up to date" in is_updated
        or "nothing to commit, working tree clean" in is_updated
    ):
        is_updated = True
    else:
        is_updated = False

    if is_updated:
        bot.version_ = f"latest ({get_git_revision_short_hash()})"
    elif is_updated is None:
        bot.version_ = f"{get_git_revision_short_hash()} (modified)"
    else:
        bot.version_ = f"old ({get_git_revision_short_hash()}) - not up to date"


if os.environ.get("ALPHABET_URI"):  # exists
    args = dict(
        dsn=config.database_url,
    )
else:
    args = dict(
        host=config.database_host,
        user=config.database_user,
        password=config.database_password,
        database=config.database_name,
        port=int(config.database_port),
    )

ssl_object = ssl.create_default_context()
ssl_object.check_hostname = False  # type: ignore
ssl_object.verify_mode = ssl.CERT_NONE
args["ssl"] = ssl_object


@bot.event
async def on_ready():
    log.info("Logged in as")
    log.info(bot.user.name)
    log.info(bot.user.id)
    log.info("------")
    await bot.change_presence(activity=discord.Game(name=f"{config.prefix}help"))
    await bot.tree.sync()


async def main():
    try:
        started = False
        while not started:
            async with bot:
                try:
                    bot.db = await EasySQL().connect(**args)
                except (
                    ConnectionError,
                    ConnectionResetError,
                    ConnectionAbortedError,
                    ConnectionRefusedError,
                ) as e:
                    log.fatal(
                        f"Failed to connect to database: {e.with_traceback(None)}"
                    )
                    log.info("Trying to remove SSL context and reconnect")
                    args["ssl"] = None
                    try:
                        bot.db = await EasySQL().connect(**args)
                    except (
                        ConnectionError,
                        ConnectionAbortedError,
                        ConnectionRefusedError,
                        ConnectionResetError,
                    ) as e:
                        log.exception(
                            f"Failed to connect to database: {e.with_traceback(None)}"
                        )
                        log.fatal("Exiting...")
                        return
                    log.info("Successfully connected to database")
                log.info("Connected to database")
                for extension in os.listdir("src"):
                    if extension.endswith(".py") and not extension.startswith("_"):
                        await bot.load_extension(f"src.{extension[:-3]}")
                        log.info(f"Loaded extension {extension[:-3]}")
                await bot.load_extension("jishaku")
                log.info("Loaded jishaku")
                await bot.db.execute(open("sql/starter.sql", "r").read())
                log.info("Executed starter sql")
                observer.start()
                log.info("Started file watcher")
                bot.start_time = datetime.datetime.utcnow()
                get_version()
                log.info(
                    f"Started with version {bot.version_} and started at {bot.start_time}"
                )
                if os.environ.get("IS_REPLIT"):
                    start()
                    log.info("REPLIT detected opening webserver for recieve pinging")
                try:
                    await bot.start(config.token)
                except discord.errors.HTTPException:
                    log.exception("You likely got ratelimited or bot's token is wrong")
                started = True  # break loop
    except KeyboardInterrupt:
        log.info("Exiting...")
        await bot.db.close()


def clean_exit(x: int = None, y: int = None, _=None):
    log.fatal("Exitting")
    observer.stop()
    bot.db: EasySQL
    reason = None
    if not isinstance(x, int) or not isinstance(y, int):
        reason = (x, y)
        x = 1
        y = 1
    try:
        asyncio.run(bot.db.close())
    except Exception as e:
        log.fatal(
            f"Failed to close PostgreSQL connection pool: {e.with_traceback(None)}"
        )
    log.info(
        f"Exitted with exit code {x} : {y}\n{' : '.join([str(b) for b in reason])}"
    )
    exit(1)


signal.signal(signal.SIGTERM, clean_exit)
signal.signal(signal.SIGABRT, clean_exit)
signal.signal(signal.SIGINT, clean_exit)
signal.signal(signal.SIGBREAK, clean_exit)

import sys

sys.excepthook = clean_exit

if __name__ == "__main__":
    asyncio.run(main())
    clean_exit(1, 1)
    log.error("Something causing bot process to be finished")
