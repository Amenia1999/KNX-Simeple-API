import asyncio
import logging
import asyncio
import time
import secrets
import configparser

from flask import Flask, jsonify, request, abort
from xknx import XKNX
from xknx.io import ConnectionConfig, ConnectionType
from xknx.tools import read_group_value

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

def main():
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
        
##API
##Read from Address
async def read_group(address, format):
    async with xknx:
        result = await read_group_value(xknx, address, value_type=format)
        return result



@app.route('/api/readgroup', methods=['POST'])
def get_val():
    data = request.json
    response = {
        "data": {
            "val": loop.run_until_complete(read_group(data['group_address'], data['format']))
        }
    }
    if checkToken(data['token']):
        return jsonify(response)
    else:
        return abort(403)

if __name__ == "__main__":
    main()
    app.run(host=server_ip, port=server_port, debug=True, threaded=True)