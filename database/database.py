import os

from dotenv import load_dotenv

load_dotenv()

mysql_credentials = {'host': 'localhost',
                     'port': int(os.getenv('MYSQL_PORT')),
                     'database': 'airport_taxi_bot',
                     'user': 'root',
                     'password': os.getenv('MYSQL_ROOT_PASSWORD')}
