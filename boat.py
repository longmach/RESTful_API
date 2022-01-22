import flask

#original
from flask import Blueprint, request, current_app
from google.cloud import datastore
import json
import constants
from google.oauth2 import id_token
from google.auth.transport import requests

encoding = 'utf-8'
client = datastore.Client()

bp = Blueprint('boats', __name__, url_prefix='/boats')

url = "https://project7-long-mach.ue.r.appspot.com/"

CLIENT_SECRETS_FILE = "client_secret_799383387107-9bolo900mbhd1kg2tasgchlen1r0k0as.apps.googleusercontent.com.json"

def verify_token():
    '''try:
        #get client_id from client_secret file
        with open(CLIENT_SECRETS_FILE) as f:
            data = json.load(f)
        CLIENT_ID = data['web']['client_id']

        # get token
        content = dict(request.headers)
        breakdown = content['Authorization'].split(' ')
        token = breakdown[1]

        #verify token
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)
        userid = idinfo['sub']
        return userid
    except ValueError:
        # Invalid token
        return None'''
    #get client_id from client_secret file
    with open(CLIENT_SECRETS_FILE) as f:
        data = json.load(f)
    CLIENT_ID = data['web']['client_id']

    # get token
    content = dict(request.headers)
    breakdown = content['Authorization'].split(' ')
    token = breakdown[1]

    #verify token
    idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)
    userid = idinfo['sub']
    return userid
        


@bp.route('', methods=['POST','GET'])
# Create a boat
def boats_get_post():
    if request.method == 'POST':
        content = request.get_json()
        try:
            userid = verify_token()
        except:
            userid = None
        if userid is not None:
            new_boat = datastore.entity.Entity(key=client.key(constants.boats))
            new_boat.update({"name": content["name"], "type": content["type"],
            "length": content["length"], "public": content["public"], "owner": userid})
            client.put(new_boat)
            new_boat["id"] = new_boat.key.id
            new_boat['self'] = request.base_url + "/" + str(new_boat["id"]) 
            return (json.dumps(new_boat), 201)    
        else:
            return (json.dumps({"Error": "Missing or invalid JWTs"}), 401)   

    elif request.method == 'GET':
        query = client.query(kind=constants.boats)
        results = list(query.fetch())
        try:
            userid = verify_token()
        except:
            userid = None
        if userid is not None:
            results[:] = [d for d in results if d['owner'] == userid]
            for e in results:
                e["id"] = e.key.id
                e['self'] = url + 'boats/'+ str(e.key.id) 
        else:
            results[:] = [d for d in results if d['public'] == True]
            for e in results:
                e["id"] = e.key.id
                e['self'] = url + 'boats/'+ str(e.key.id)
        return (json.dumps(results), 200)
    else:
        return 'Method not recogonized'

@bp.route('/<id>', methods=['DELETE'])
def boats_delete(id):
    if request.method == 'DELETE':
        try:
            userid = verify_token()
        except:
            userid = None
        if userid is not None:
            try:
                #delete boat
                boat_key = client.key(constants.boats, int(id))
                boat = client.get(key=boat_key)
                if userid == boat['owner']:
                    client.delete(boat_key)
                    return ('',204)
                else:
                    return (json.dumps({"Error": "JWT is valid but boat_id is owned by someone else"}), 403)
            except:
                return (json.dumps({"Error": "JWT is valid but no boat with this boat_id exists"}), 403)
            '''           
            #delete boat
            boat_key = client.key(constants.boats, int(id))
            boat = client.get(key=boat_key)
            if userid == boat['owner']:
                client.delete(boat_key)
            return (json.dumps(boat) ,200)
            '''
        else:
            return (json.dumps({"Error": "Missing or invalid JWTs"}), 401)
    else:
        return 'Method not recognized'

