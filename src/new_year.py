import discord
from discord.ext import commands, tasks

import sql.sql as sql


class New_Year(commands.Cog):
    """
    New year group command
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db: sql.EasySQL = bot.db
        self.check_guild.start()

    @tasks.loop(seconds=60)
    async def check_guild(self):
        all_guilds = await self.db.fetch("SELECT * FROM config")
        await self.bot.wait_until_ready()
        for guild in self.bot.guild:
            guild: discord.Guild
            if guild.id not in all_guilds:
                await guild.owner.send(
                    embed=discord.Embed(
                        title="Please setup bot!",
                        description="Bot won't works if you don't setup bot!",
                    )
                )
