
from config import *
from logic import *
import discord
from discord.ext import commands
from config import TOKEN
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.colors import ListedColormap
import random
from io import BytesIO
import geopandas as gpd




command_prefix = "!"
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=command_prefix, intents=intents)

min_lon = -180
max_lon = 180
min_lat = -90
max_lat = 90

# Default marker colors
city_marker_color = "blue"
point_marker_color = "red"

# Continent and ocean colors
continent_colors = ["lightgreen", "tan", "lightblue", "pink", "orange"]
ocean_color = "lightblue"


continents = [

    [
        (-160, 80), (-60, 80), (-60, 10), (-160, 10), (-160, 80),
    ],

    [
        (-80, 10), (-80, -60), (-30, -60), (-30, 10), (-80, 10),
    ],

]

oceans = [

    [
        (-180, 80), (-180, -90), (180, -90), (180, 80), (-180, 80)
    ]

]

# Geographic features
geographic_features = {
    "mountains": {"color": "gray", "marker": "^"},
    "rivers": {"color": "blue", "marker": "-"},
    "forests": {"color": "green", "marker": "s"},
    "deserts": {"color": "yellow", "marker": "o"},
}


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
    await interaction.response.send_message(
        f"Привет {interaction.user.mention}! Список Команд : /show_city /help /remember_city /show_my_cities /set_color /show_map /add_feature")


@bot.tree.command(name='show_city', description='The city that you would choose')
async def show_city(interaction: discord.Integration, city_name: str):
    coordinates = manager.get_coordinates(city_name)
    if coordinates:
        manager.create_graph("city_map.png", [city_name], city_marker_color, point_marker_color)
        await interaction.response.send_message(file=discord.File("city_map.png"))
    else:
        await interaction.response.send_message("Город не найден.")


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


@bot.tree.command(name='set_color', description='Set the color for markers')
async def set_color(interaction: discord.Integration, type: str, color: str):
    global city_marker_color, point_marker_color
    if type == "city":
        city_marker_color = color
        await interaction.response.send_message(f"Цвет маркера для городов изменен на {color}")
    elif type == "point":
        point_marker_color = color
        await interaction.response.send_message(f"Цвет маркера для точек изменен на {color}")
    else:
        await interaction.response.send_message("Неверный тип маркера. Используйте 'city' или 'point'.")


@bot.tree.command(name='show_map', description='Show a map with continents and oceans')
async def show_map(interaction: discord.Integration):
    fig, ax = plt.subplots()

    # Load a world map dataset from geopandas
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

    # Filter for continents
    continents = world[world['continent'] != 'Antarctica']

    # Create the plot
    fig, ax = plt.subplots(figsize=(10, 5))
    continents.plot(ax=ax, color='lightgreen', edgecolor='black')

    # Customize the plot (if needed)
    ax.set_title("World Map")
    ax.set_xlim(min_lon, max_lon)
    ax.set_ylim(min_lat, max_lat)

    # Display the map
    plt.show()

    # Send the image to Discord
    await interaction.response.send_message(file=discord.File(buffer, 'world_map.png'))




@bot.tree.command(name='add_feature', description='Add a geographic feature to the map')
async def add_feature(interaction: discord.Integration, feature: str, location: str):
    global geographic_features

    # Get coordinates for the feature
    coordinates = manager.get_coordinates(location)
    if not coordinates:
        await interaction.response.send_message("Местоположение не найдено.")
        return

    # Validate feature type
    if feature.lower() not in geographic_features:
        await interaction.response.send_message(
            "Неверный тип географического объекта. Допустимые варианты: mountains, rivers, forests, deserts.")
        return

    # Get feature color and marker
    color = geographic_features[feature.lower()]["color"]
    marker = geographic_features[feature.lower()]["marker"]

    # Create the map
    fig, ax = plt.subplots()

    # Draw continents
    for continent in continents:
        polygon = Polygon(continent, closed=True, facecolor=random.choice(continent_colors), edgecolor="black")
        ax.add_patch(polygon)

    # Draw oceans
    for ocean in oceans:
        polygon = Polygon(ocean, closed=True, facecolor=ocean_color, edgecolor="black")
        ax.add_patch(polygon)

    # Add the feature
    ax.plot(coordinates[1], coordinates[0], marker=marker, color=color, markersize=10)

    # Set plot limits and title
    ax.set_xlim(min_lon, max_lon)
    ax.set_ylim(min_lat, max_lat)
    ax.set_title("World Map")

    # Save the plot as an image
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # Send the image to Discord
    await interaction.response.send_message(file=discord.File(buffer, 'world_map.png'))


if __name__ == "__main__":
    manager = DB_Map(DATABASE)
    bot.run(TOKEN)
