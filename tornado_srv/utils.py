# -*- coding: utf-8 -*-

import base64
import pickle
import bson
from django.utils import timezone
from rek.mango.auth import User
from rek.mongo.conn_manager import mongodb_connection_manager

def decode(session_data):
    encoded_data = base64.decodestring(session_data)
    try:
        # could produce ValueError if there is no ':'
        hash, pickled = encoded_data.split(':', 1)
        return pickle.loads(pickled)
    except Exception:
        return {}

def get_authenticated_user(session_key):
    session_collection = mongodb_connection_manager.database['sessions']
    session_data = session_collection.find_one({'session_key' : session_key})
    if not session_data or session_data['expire_date'] <= timezone.now():
        return None

    encoded_data = decode(session_data['session_data'])

    if '_auth_user_id' not in encoded_data:
        return None

    try:
        user_id = bson.ObjectId(encoded_data['_auth_user_id'])
        user = User.collection.find_one(user_id)
        if not user:
            raise Exception("Can't find user")

        return user
    except Exception:
        return None
