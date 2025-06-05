from valor import Valor
from discord.ext.commands import Context
from util import ErrorEmbed, LongTextEmbed, SettingsManager, SETTINGS_SCHEMA
import argparse, discord

async def _register_settings(valor: Valor):
    desc = (
        "Server settings command.\n"
        "Format:\n"
        "-settings <setting_name> get\n"
        "-settings <setting_name> set <value>\n\n"
        "Examples:\n"
        "-settings auto_moderation set true\n"
        "-settings log_level get\n"
        "-settings welcome_message set \"Welcome to the guild, traveler!\"\n\n"
        "⚠️ Wrap strings in quotes if they contain spaces."
    )

    parser = argparse.ArgumentParser(description='Settings command')
    parser.add_argument('action', nargs='?', default=None, choices=['get', 'set', 'list'], help='Action to perform')
    parser.add_argument('setting', nargs='?', default=None, help='The setting key')
    parser.add_argument('value', nargs='?', help='Value to set (required if action is "set")')

    manager = SettingsManager()

    @valor.command()
    async def settings(ctx: Context, *options):
        try:
            args = parser.parse_args(options)
        except:
            return await LongTextEmbed.send_message(valor, ctx, "Settings", parser.format_help().replace("main.py", "-settings"), color=0xFF00)
        

        server_id = ctx.guild.id
        action = args.action.lower()

        if action == "list":
            # Show all settings for this server
            data = manager._load(server_id)  # get raw stored data
            embed = discord.Embed(title=f"Settings for {ctx.guild.name}", color=0x7785cc)

            for key, info in manager.schema.items():
                val = data.get(key, info["default"])
                desc = info.get("description", "")
                typ = info.get("type", "unknown")
                display_val = val

                # For lists, join them nicely
                if typ == "list":
                    display_val = ", ".join(str(i) for i in val) if val else "(empty list)"
                elif val == "":
                    display_val = "(empty string)"

                embed.add_field(
                    name=f"{key} [{typ}]",
                    value=f"Value: `{display_val}`\n{desc}",
                    inline=False,
                )

            await ctx.send(embed=embed)
            return


        key = args.setting

        if key not in SETTINGS_SCHEMA:
            return await ctx.send(embed=ErrorEmbed(f"Unknown setting: `{key}`"))

        schema = SETTINGS_SCHEMA[key]

        if action == "get":
            value = manager.get(server_id, key)
            return await ctx.send(embed=discord.Embed(
                title=f"Setting: {key}",
                description=f"Current value: `{value}`\n{schema['description']}",
                color=discord.Color.blurple()
            ))

        elif action == "set":
            if not ctx.author.guild_permissions.administrator:
                return await ctx.send(embed=ErrorEmbed("You must be a server administrator to change settings."))
            if args.value is None:
                return await ctx.send(embed=ErrorEmbed("You must provide a value to set."))

            raw_value = args.value
            try:
                # Type conversion
                if schema["type"] == "bool":
                    parsed = raw_value.lower() in ("true", "1", "yes", "on")
                elif schema["type"] == "list":
                    parsed = [x.strip() for x in raw_value.split(",") if x.strip()]
                elif schema["type"] == "value":
                    if raw_value.lower() not in schema["options"]:
                        raise ValueError()
                    parsed = raw_value.lower()
                elif schema["type"] == "string":
                    parsed = raw_value
                else:
                    raise TypeError(f"Unsupported type: {schema['type']}")
            except Exception:
                return await ctx.send(embed=ErrorEmbed(f"Invalid value for setting `{key}`."))

            try:
                manager.set(server_id, key, parsed)
                return await ctx.send(embed=discord.Embed(
                    title="Setting Updated",
                    description=f"`{key}` has been updated to `{parsed}`.",
                    color=0x00FF00
                ))
            except Exception as e:
                return await ctx.send(embed=ErrorEmbed(f"Failed to update setting: {e}"))

    @settings.error
    async def settings_error(ctx: Context, error: Exception):
        await ctx.send(embed=ErrorEmbed("Use the command like this:\n-settings get <setting_name>\n-settings set <setting_name> <value>"))
        print(error)

    @valor.help_override.command()
    async def settings(ctx: Context):
        await LongTextEmbed.send_message(valor, ctx, "Settings Help", desc, color=0x00AAFF)
