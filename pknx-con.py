import asyncio
import logging
import time
import configparser
import argparse
import secrets

from flask import Flask, jsonify, request
from xknx import XKNX
from xknx.io import ConnectionConfig, ConnectionType
from xknx.tools import read_group_value
from xknx.tools import group_value_write

##CONFIG
config = configparser.ConfigParser()
config.read('config.ini')

knx_ip = config['KNX']['ip']

server_ip = config['Server']['ip']
server_port = config['Server']['port']
server_log = config['Server']['log_file']
server_token = config['Server']['token']


app = Flask(__name__)
version = "0.0.1"
xknx = None
response = None



#logging.basicConfig(level=logging.INFO)
#logging.getLogger("xknx.log").level = logging.DEBUG
#logging.getLogger("xknx.knx").level = logging.DEBUG


async def main() -> None:
    global xknx
    connection_config = ConnectionConfig(
        connection_type=ConnectionType.TUNNELING,
        gateway_ip="192.168.178.153",
        individual_address="3.1.0",
        # local_ip="10.1.0.123",
        # route_back=True,

    )
    xknx = XKNX(connection_config=connection_config)

    async with xknx:
        start_time = time.time()
        result = await read_group_value(xknx, "0/0/6", value_type="temperature")
        print(f"Value: {result} - took {(time.time() - start_time):0.3f} seconds")

asyncio.run(main())