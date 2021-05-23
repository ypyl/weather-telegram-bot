from paramiko import SSHClient, AutoAddPolicy
from configuration import IP, NAME, PASSWORD
import time

client = SSHClient()
client.set_missing_host_key_policy(AutoAddPolicy())
client.connect(IP, username=NAME, password=PASSWORD)

client_sftp = client.open_sftp()

stdin, stdout, stderr = client.exec_command(
    'pip3 install python-telegram-bot --upgrade')
stdin, stdout, stderr = client.exec_command(
    'sudo systemctl stop weather-bot.service')
stdin, stdout, stderr = client.exec_command(
    'sudo systemctl disable weather-bot.service')
# give time raspberry to disable service
time.sleep(5)

client_sftp.put('./weather-bot.py', './weather-bot.py')
client_sftp.put('./configuration.py', './configuration.py')
client_sftp.put('./weather-bot.service',
                './weather-bot.service')

stdin, stdout, stderr = client.exec_command(
    'sudo rm /lib/systemd/system/weather-bot.service')
stdin, stdout, stderr = client.exec_command(
    'sudo cp -R ./weather-bot.service /lib/systemd/system/weather-bot.service')
stdin, stdout, stderr = client.exec_command(
    'sudo chmod 644 /lib/systemd/system/weather-bot.service')
stdin, stdout, stderr = client.exec_command('chmod +x /home/pi/weather-bot.py')
stdin, stdout, stderr = client.exec_command('sudo systemctl daemon-reload')
stdin, stdout, stderr = client.exec_command(
    'sudo systemctl enable weather-bot.service')
stdin, stdout, stderr = client.exec_command(
    'sudo systemctl start weather-bot.service')
