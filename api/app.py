import logging
from flask import Flask, Response
from flask_nameko import FlaskPooledClusterRpcProxy
import csv
import json
import ast
import atexit

DATAFILE = 'data/sample_us_users.csv'

rpc = FlaskPooledClusterRpcProxy()
csv_file = open(DATAFILE, 'r')
input_data_reader = csv.DictReader(csv_file)

def on_exit_app(csv_file):
    csv_file.close()

atexit.register(on_exit_app, csv_file)

def create_app():
    app = Flask(__name__)
    app.config.update(dict(
        NAMEKO_AMQP_URI='amqp://rabbit'
        )
    )

    rpc.init_app(app)
    
    return app

app = create_app()

@app.route('/healthcheck')
def healthcheck():
    return 'All good from api!'

@app.route('/report', methods=["GET"])
def get_report():
    result = rpc.userstats.report()
    return Response(json.dumps(result), status=200)

@app.route('/submit/<int:num_users>', methods=["GET"])
def submit(num_users):
    """ Entry point to submit users """
    n = 0
    for row in input_data_reader:
        if n >= num_users:
            break
        address_dict_str = row.get('address')
        try:
            address = ast.literal_eval(address_dict_str)
        except Exception as e:
            logging.error(f'Wrong record {address_dict_str}')
            raise e

        message = {
            'id': row.get('id',''),
            'address': {
                'city': address.get('city',''),
                'state': address.get('state',''),
                'country': address.get('country',''),
                'postCode': address.get('postCode','')
            },
            'datetime': row.get('inserted_at','')
        }
        rpc.userevents.send(message)
        n += 1
    return Response(f'Sent {n} new events', status=200)

    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)