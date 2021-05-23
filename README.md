Tiny Telegram Bot to send weather info based on user location

# Source Code

`configuration.py` contains the following constants:

- SUPPORTED_USER = show info for only this user
- DEFAULT_LOCATION_LON = default longitude
- DEFAULT_LOCATION_LAT = default latitude
- TELEGRAM_TOKEN = [telegram](https://core.telegram.org/bots) token
- WEATHER_API_KEY = [weather api](https://www.weatherapi.com) key

`weather-bot.py` contains the logic of the bot
`deploy.py` is a small helper to deploy the bot to raspberry pi (as I am using it to host the bot)

# Dependencies

- `python 3`
- `python-telegram-bot` - https://python-telegram-bot.org

# Helpers to debug on raspberry

See the status of service on raspberry:

`systemctl status weather-bot`

See logs of the service:

`journalctl -u weather-bot.service | tail -n 30`
