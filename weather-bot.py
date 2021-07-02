from telegram.ext import MessageHandler, Filters
from telegram.ext import CommandHandler
from telegram.ext import Updater
from configuration import DEFAULT_LOCATION_LON, DEFAULT_LOCATION_LAT, SUPPORTED_USER, TELEGRAM_TOKEN, WEATHER_API_KEY
import logging
import requests

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


WEATHER_API_FORECAST = 'http://api.weatherapi.com/v1/forecast.json?key={0}&q={1}&days=7&aqi=no&alerts=no'
WEATHER_API_CURRENT = 'http://api.weatherapi.com/v1/current.json?key={0}&q={1}&aqi=no&alerts=no'


SUN = '☀️'
MOON = '🌙'
CLOUD = '☁️'
SUN_WITH_CLOUD = '⛅'
SUN_WITH_LARGE_CLOUD = '🌥'
SUN_WITH_SMALL_CLOUD = '🌤️'
SUN_WITH_RAIN_CLOUD = '🌦'
SUNRISE = '🌅'
FOG = '🌫️'
SNOW = '❄️'
WIND = '🌬'
RAIN = '☔'
THUNDER = '⚡'
CLOUD_WITH_LIGHTNING = '🌩️'
CLOUD_WITH_LIGHTNING_RAIN = '⛈️'
CLOUD_WITH_RAIN = '🌧️'
CLOUD_WITH_SNOW = '🌨️'
THERMOMETER = '🌡️'
TORNADO = '🌪️'

EMOJ_MAP = {
    'Sunny': SUN,
    'Clear': MOON,
    'Partly cloudy': SUN_WITH_CLOUD,
    'Cloudy': CLOUD,
    'Overcast': CLOUD,
    'Mist': FOG,
    'Patchy rain possible': CLOUD_WITH_RAIN,
    'Patchy snow possible': CLOUD_WITH_SNOW,
    'Patchy sleet possible': CLOUD_WITH_SNOW,
    'Patchy freezing drizzle possible': CLOUD_WITH_RAIN,
    'Thundery outbreaks possible': CLOUD_WITH_LIGHTNING_RAIN,
    'Blowing snow': CLOUD_WITH_SNOW,
    'Moderate rain': CLOUD_WITH_RAIN,
    'Patchy light rain with thunder': CLOUD_WITH_LIGHTNING_RAIN,
    'Moderate or heavy rain shower': CLOUD_WITH_RAIN,
    'Torrential rain shower': CLOUD_WITH_RAIN,
    'Blizzard': SNOW,
    'Fog': FOG,
    'Freezing fog': FOG,
    'Patchy light drizzle': CLOUD,
    'Light drizzle': CLOUD,
    'Freezing drizzle': CLOUD,
    'Heavy freezing drizzle': CLOUD_WITH_RAIN,
    'Patchy light rain': CLOUD_WITH_RAIN,
    'Light rain': CLOUD_WITH_RAIN,
    'Moderate rain at times': SUN_WITH_RAIN_CLOUD,
    'Moderate rain': CLOUD_WITH_RAIN,
    'Heavy rain at times': SUN_WITH_RAIN_CLOUD,
    'Heavy rain': RAIN,
    'Light freezing rain': CLOUD_WITH_RAIN,
    'Moderate or heavy freezing rain': RAIN,
    'Light sleet': CLOUD,
    'Moderate or heavy sleet': CLOUD_WITH_SNOW,
    'Patchy light snow': CLOUD,
    'Light snow': CLOUD_WITH_SNOW,
    'Patchy moderate snow': CLOUD_WITH_SNOW,
    'Moderate snow': CLOUD_WITH_SNOW,
    'Patchy heavy snow': CLOUD_WITH_SNOW,
    'Heavy snow': SNOW,
    'Ice pellets': SNOW,
    'Light rain shower': CLOUD_WITH_RAIN,
    'Moderate or heavy rain shower': CLOUD_WITH_RAIN,
    'Torrential rain shower': RAIN,
    'Light sleet showers': CLOUD_WITH_RAIN,
    'Moderate or heavy sleet showers': CLOUD_WITH_RAIN,
    'Light snow showers': CLOUD_WITH_SNOW,
    'Moderate or heavy snow showers': SNOW,
    'Light showers of ice pellets': CLOUD_WITH_SNOW,
    'Moderate or heavy showers of ice pellets': SNOW,
    'Patchy light rain with thunder': CLOUD_WITH_LIGHTNING_RAIN,
    'Moderate or heavy rain with thunder': CLOUD_WITH_LIGHTNING_RAIN,
    'Patchy light snow with thunder': CLOUD_WITH_SNOW,
    'Moderate or heavy snow with thunder': CLOUD_WITH_LIGHTNING,
}

MAP_USER_LOCATION = {
    SUPPORTED_USER: (DEFAULT_LOCATION_LON, DEFAULT_LOCATION_LAT)
}


def format_current(weather_value, _):
    location = weather_value['location']
    location_value = location['name'] + ' ' + \
        location['region'] + ' ' + location['country'] + '\n'
    result = location_value
    current_value = weather_value['current']
    current_temp = current_value['temp_c']
    current_condition = current_value['condition']['text']
    current_feellike = current_value['feelslike_c']
    result += f'Now: {current_condition} - {current_temp} ({current_feellike})\n'
    return result


def format_forecast(weather_value, day_index):
    print(day_index)
    result = format_current(weather_value, day_index)
    forecast_value = weather_value['forecast']['forecastday']
    print(len(forecast_value))
    day = forecast_value[day_index]
    date = day['date']
    day_value = day['day']
    avg_temp = day_value['avgtemp_c']
    condition = day_value['condition']['text']
    result += f'{date}: {condition} - {avg_temp}\n'
    hours_value = day['hour']
    temp_img_condition = None
    for hour_value in hours_value:
        hour_value_hours = hour_value['time'].split()[1]
        condition = hour_value['condition']['text']
        image_condition = EMOJ_MAP[condition]
        temp = hour_value['temp_c']
        feellike = hour_value['feelslike_c']
        if temp_img_condition != image_condition:
            temp_img_condition = image_condition
            result += f'{hour_value_hours}: {temp_img_condition} - {temp} ({feellike})\n'
    return result


MAP_API_FORMAT = {
    WEATHER_API_CURRENT: format_current,
    WEATHER_API_FORECAST: format_forecast
}


def weather_info_message(api_link, username, longitude, latitude, day):
    if username != SUPPORTED_USER:
        return 'User is not supported.'
    weather_api_url = api_link.format(
        WEATHER_API_KEY,
        str(latitude) + ',' + str(longitude))
    result = requests.get(weather_api_url)
    if result.ok:
        weather_value = result.json()
        return MAP_API_FORMAT[api_link](weather_value, day)
    return 'Not able to connect to Weather API'

# bot handlers


def validate_location(update):
    if update.message.location:
        lon = update.message.location.longitude
        lat = update.message.location.latitude
        MAP_USER_LOCATION[update.message.from_user.username] = (lon, lat)
    elif update.message.from_user.username in MAP_USER_LOCATION and MAP_USER_LOCATION[update.message.from_user.username]:
        lon, lat = MAP_USER_LOCATION[update.message.from_user.username]
    else:
        return None
    return lon, lat


def send_weather_info(update, context):
    try:
        cmn = int(update.message.text[1:])
    except ValueError:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text='Not able to parse command')
        return
    result = validate_location(update)
    if result is None:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text='Not able to identify your location')
        return
    lon, lat = result
    message = weather_info_message(
        WEATHER_API_FORECAST,
        update.message.from_user.username,
        lon,
        lat,
        cmn)
    context.bot.send_message(
        chat_id=update.effective_chat.id, text=message)


def send_current_weather_info(update, context):
    result = validate_location(update)
    if result is None:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text='Not able to identify your location')
        return
    lon, lat = result
    message = weather_info_message(
        WEATHER_API_CURRENT,
        update.message.from_user.username,
        lon,
        lat,
        None)

    context.bot.send_message(
        chat_id=update.effective_chat.id, text=message)


def show_help(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="I'm a weather bot, please send me your location!")

# main


updater = Updater(token=TELEGRAM_TOKEN, use_context=True)

dispatcher = updater.dispatcher

help_handler = CommandHandler('help', show_help)
dispatcher.add_handler(help_handler)
day_handler1 = CommandHandler('1', send_weather_info)
dispatcher.add_handler(day_handler1)
day_handler2 = CommandHandler('2', send_weather_info)
dispatcher.add_handler(day_handler2)
day_handler3 = CommandHandler('3', send_weather_info)
dispatcher.add_handler(day_handler3)
day_handler4 = CommandHandler('4', send_weather_info)
dispatcher.add_handler(day_handler4)
day_handler5 = CommandHandler('5', send_weather_info)
dispatcher.add_handler(day_handler5)
day_handler6 = CommandHandler('6', send_weather_info)
dispatcher.add_handler(day_handler6)
day_handler7 = CommandHandler('7', send_weather_info)
dispatcher.add_handler(day_handler7)

text_handler = MessageHandler(
    Filters.text & (~Filters.command), send_current_weather_info)
dispatcher.add_handler(text_handler)

location_handler = MessageHandler(Filters.location, send_current_weather_info)
dispatcher.add_handler(location_handler)

updater.start_polling()

updater.idle()
