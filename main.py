import asyncio
import logging
import asyncio
import time
import secrets
import configparser
import argparse

from flask import Flask, jsonify, request, abort, render_template
from xknx import XKNX
from xknx.io import ConnectionConfig, ConnectionType
from xknx.tools import read_group_value, group_value_write

##CONFIG
config = configparser.ConfigParser()
config.read('config.ini')

knx_ip = config['KNX']['ip']

knx_address = config['Server']['knx_address']
server_ip = config['Server']['ip']
server_port = config['Server']['port']
server_log = config['Server']['log_file']
server_token = config['Server']['token']



app = Flask(__name__)
version = "0.0.1"
xknx = None

loop = asyncio.get_event_loop()


def connection():
    global xknx
    connection_config = ConnectionConfig(
        connection_type=ConnectionType.TUNNELING,
        gateway_ip=knx_ip,
        individual_address=knx_address,
    )
    xknx = XKNX(connection_config=connection_config)
    logging.basicConfig(filename=server_log, level=logging.INFO)

##HELPERS
def checkToken(token):
    return token == server_token

def validateToken(token):
    if checkToken(token):
        return True
    else:
        return abort(403)


@app.route('/')
def route_root():
    return render_template('welcome.html', version=version, knx_ip=knx_ip, server_ip=server_ip, server_port=server_port)

##Busmonitor
##On
##OFF

@app.route('/api/writegroup', methods=['POST'])
async def route_write_group():
    async with xknx:
        data = request.json
        await group_value_write(xknx, data['group_address'], data['val'], value_type=data['format'])
        response = {"data": {"success": "true"}}

        if validateToken(data['token']):
            return jsonify(response)



@app.route('/api/readgroup', methods=['POST'])
async def route_read_group():
    async with xknx:
        data = request.json
        response_val = await read_group_value(xknx, data['group_address'], value_type=data['format'])

        if response_val is None:
            response = {"data": {"success": "false"}}
        else:
            response = {"data": {"success": "true","val": response_val}}

        if validateToken(data['token']):
            return jsonify(response)



if __name__ == "__main__":
    connection()
    app.run(host=server_ip, port=server_port, debug=False, threaded=True)