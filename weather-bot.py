from telegram.ext import MessageHandler, Filters
from telegram.ext import CommandHandler
from telegram.ext import Updater
from configuration import DEFAULT_LOCATION_LON, DEFAULT_LOCATION_LAT, SUPPORTED_USER, TELEGRAM_TOKEN, WEATHER_API_KEY
import logging
import requests

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


WEATHER_API = 'http://api.weatherapi.com/v1/forecast.json?key={0}&q={1}&days=3&aqi=no&alerts=no'


# utility

def format_message(weather_value):
    location = weather_value['location']
    location_value = location['name'] + ' ' + \
        location['region'] + ' ' + location['country'] + '\n'
    result = location_value
    current_value = weather_value['current']
    forecast_value = weather_value['forecast']['forecastday']
    current_temp = current_value['temp_c']
    current_condition = current_value['condition']['text']
    current_feellike = current_value['feelslike_c']
    result += f'{current_condition} - {current_temp} ({current_feellike})\n'
    for day in forecast_value:
        date = day['date']
        day_value = day['day']
        avg_temp = day_value['avgtemp_c']
        condition = day_value['condition']['text']
        result += f'{date}: {condition} - {avg_temp} ({current_feellike})\n'
        hours_value = day['hour']
        for hour_value in hours_value:
            hour_value_hours = hour_value['time'].split()[1]
            condition = hour_value['condition']['text']
            temp = hour_value['temp_c']
            feellike = hour_value['feelslike_c']
            result += f'{hour_value_hours}: {condition} - {temp} ({feellike})\n'
    return result


def weather_info_message(username, longitude, latitude):
    if username != SUPPORTED_USER:
        return 'User is not supported.'
    weather_api_url = WEATHER_API.format(
        WEATHER_API_KEY,
        str(latitude) + ',' + str(longitude))
    result = requests.get(weather_api_url)
    if result.ok:
        weather_value = result.json()
        return format_message(weather_value)
    return 'Not able to connect to Weather API'

# bot handlers


def send_default_weather_info(update, context):
    message = weather_info_message(
        update.message.from_user.username,
        DEFAULT_LOCATION_LON,
        DEFAULT_LOCATION_LAT)
    context.bot.send_message(
        chat_id=update.effective_chat.id, text=message)


def send_weather_info(update, context):
    message = weather_info_message(
        update.message.from_user.username,
        update.message.location.longitude,
        update.message.location.latitude)
    context.bot.send_message(
        chat_id=update.effective_chat.id, text=message)


def start(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="I'm a weather bot, please send me your location!")

# main


updater = Updater(token=TELEGRAM_TOKEN, use_context=True)

dispatcher = updater.dispatcher

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

text_handler = MessageHandler(
    Filters.text & (~Filters.command), send_default_weather_info)
dispatcher.add_handler(text_handler)

location_handler = MessageHandler(Filters.location, send_weather_info)
dispatcher.add_handler(location_handler)

updater.start_polling()

updater.idle()
