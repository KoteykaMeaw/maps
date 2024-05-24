from config import *
from logic import *
import discord
from discord.ext import commands
from config import TOKEN

command_prefix = "!"
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=command_prefix, intents=intents)







@bot.event
async def on_ready():
    print("Bot is Up and Ready!")
    try:
        synched = await bot.tree.sync()
        print(f'Synched {len(synched)} command(s)')
    except Exception as e:
        print(e)

@bot.tree.command(name='help', description='every command')
async def help(interaction: discord.Integration):
    await interaction.response.send_message(f"Привет {interaction.user.mention}! Список Команд : /show_city /help /remember_city /show_my_cities.")

@bot.tree.command(name='show_city', description='The city that you would choose')
async def show_city(interaction: discord.Integration, city_name: str):
    coordinates = manager.get_coordinates(city_name)
    if coordinates:
        manager.create_graph("city_map.png", [city_name])
        await interaction.response.send_message(file=discord.File("city_map.png"))
    else:
        await interaction.user("Город не найден.")


@bot.tree.command(name='remember_city', description='Add a city to the list')
async def remember_city(interaction: discord.Integration, city_name: str):
    user_id = interaction.user.id
    added = manager.add_city(user_id, city_name)
    if added:
        await interaction.response.send_message(f"Город {city_name} успешно добавлен в список избранных.")
    else:
        await interaction.response.send_message("Город не найден.")


@bot.tree.command(name='show_my_cities', description='Every city you have in the db')
async def show_my_cities(interaction: discord.Integration, city_name: str):
    user_id = interaction.user.id
    cities = manager.select_cities(user_id)
    if cities:
        await interaction.response.send_message("Ваши сохраненные города:")
        for city in cities:
            await interaction.response.send_message(city)
    else:
        await interaction.response.send_message("У вас нет сохраненных городов.")


if __name__ == "__main__":
    manager = DB_Map(DATABASE)
    bot.run(TOKEN)
