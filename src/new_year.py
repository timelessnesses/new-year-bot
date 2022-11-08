import typing
from datetime import datetime

import discord
import pytz
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

    @tasks.loop(hours=24)
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
                continue

    @tasks.loop(minutes=5)
    async def check_time(self):
        await self.bot.wait_until_ready()
        now = datetime.now()
        for guild in self.bot.guild:
            guild: discord.Guild  # mf type hinting
            db_guild = await self.db.fetch(
                "SELECT * FROM config WHERE guild_id = $1", guild.id
            )
            reminder_message = await self.db.fetch(
                "SELECT * FROM reminder_mesage WHERE guild_id = $1"
            )
            reminder_message = await guild.get_channel(
                reminder_message["channel_id"]
            ).fetch_message(reminder_message["message_id"])
            new_year_message = await self.db.fetch(
                "SELECT * FROM new_year_message WHERE guild_id = $1"
            )
            new_year_message = guild.get_channel(new_year_message["channel_id"])
            try:
                current_timezone = pytz.timezone(db_guild["timezone"].title())
            except pytz.exceptions.UnknownTimeZoneError:
                current_timezone = pytz.timezone("UTC")
            current_time = now.astimezone(current_timezone)
            new_year_time = datetime(
                current_time.year, 1, 1, 0, 0, 0, 0, current_timezone
            )
            estimated_left = new_year_time - current_time
            if estimated_left.total_seconds() in range(
                0, 86400 * 2
            ):  # new year is here and it lasts for 2 days after that
                channel = guild.get_channel(db_guild["annouce_channel_id"])
                j = await channel.send(
                    f"{(guild.get_role(new_year_message['ping_role_id']).mention if new_year_message['ping_role_id'] else '@everyone')}",
                    embed=discord.Embed(
                        title=f"{new_year_message['message_format'] if new_year_message['message_format'] else 'Happy new year! 🎉'}",
                        description=f"{new_year_message['body_message_format'] if new_year_message['body_message_format'] else f'Happy new year! I hope you have a great year ahead! Welcome to {new_year_time.year}!'}",
                        color=discord.Color.green(),
                    ),
                )
                await self.db.execute(
                    "INSERT INTO new_year_message(id) VALUES ($1) WHERE guild_id = $2",
                    j.id,
                    guild.id,
                )
            else:
                # delete annouced message then count the time left
                try:
                    new_year_message.get_partial_message(
                        new_year_message["message_id"]
                    ).delete()
                except:
                    pass
                await reminder_message.edit(
                    embed=(
                        discord.Embed(
                            title="New year is coming!",
                            description=f"{self.format_time_to_string(estimated_left)} left until new year!",
                            color=discord.Color.green(),
                        )
                    ).set_footer(
                        text=f"This message is controlled by timezone that's configured by the owner: {current_timezone.zone}"
                    )
                )

    @commands.hybrid_group()
    async def new_year(self, ctx: commands.Context):
        """
        New year group command
        """
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)


async def setup(bot: commands.Bot) -> typing.NoReturn:
    await bot.add_cog(New_Year(bot))
