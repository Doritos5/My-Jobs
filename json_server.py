
## Description: Home assignment.
## Author: Dor Mordechai.

import json
from marshmallow import Schema, fields
from flask import Flask, request
from marshmallow.validate import OneOf


# Class that defines a JSON accepted schema, using Marshmallow package.
# Fields: id, os, price, sdk_version - all of them from String type.
class JsonSchema(Schema):

    id = fields.String(required=True)
    os = fields.String(required=True, validate=OneOf(['Android', 'iOS', 'Windows']))
    price = fields.String(required=True)
    sdk_version = fields.String(required=True)


# Initialize flask app
app = Flask(__name__)

# Initialize Marshmallow's Schema object
schema = JsonSchema()

@app.route("/check_schema", methods=["GET", "POST"])
def check_scheme():

    global schema

    if request.method == 'GET':

        # Getting the ID from the GET requests.
        strID = request.args.get('id')

        # Open the json file using the message ID.
        with open('{}.json'.format(strID), 'r') as infile:

            # Opening the file and getting the JSON data.
            json_from_file = json.loads(infile.read())
            infile.close()


        # validate the JSON data from the file, according to the pre-maid schema
        result = schema.load(json_from_file)

        # if Errors = Schema validation failed.
        if(result.errors):
            return "False"

        return "True"


    else:
        try:
            # Get the JSON data from the POST request, if NOT getting JSON data = fail and send 400 http code.
            received_json_data = request.get_json()

            # print(received_json_data)
            # print(type(received_json_data))

            # Create a new JSON file, with the name of the accepted JSON ID.
            with open('{}.json'.format(received_json_data["id"]), 'w') as outfile:
                json.dump(received_json_data, outfile, ensure_ascii=False)


            # Return good http status code.
            return "", 200

        # In case of failure in any of the steps above (probably data type failure) - send "Bad request", 400 httpd code.
        except:
            return "", 400




if __name__ == "__main__":
    app.run(host='0.0.0.0', threaded=True)
	