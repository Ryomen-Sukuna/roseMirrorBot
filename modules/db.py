from config import db, OWNER_ID

auth = db["bot"].auth

AUTH = []


def is_auth(chat_id):
    return chat_id in AUTH or chat_id == OWNER_ID


def add_auth(chat_id):
    AUTH.append(chat_id)
    AUTH = list(set(AUTH))
    auth.insert_one({"_id": chat_id})


def remove_auth(chat_id):
    AUTH.remove(chat_id)
    auth.delete_one({"_id": chat_id})


def get_auth():
    return AUTH


def get_auth_list():
    return list(auth.find())


def load_auth():
    for chat_id in get_auth_list():
        AUTH.append(chat_id["_id"])
