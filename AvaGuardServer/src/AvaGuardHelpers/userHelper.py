import src.AvaGuardHelpers.avaguard_models as uMdl
from datetime import datetime, timedelta, timezone

from pydantic import BaseModel, Extra

from src.AvaGuardHelpers.avaguard_models import Token, User, TokenData, UserInDB
from src.AvaGuardHelpers.commonHelper import Dict2Class


class UserHelper:

    def __init__(self, db):
        from passlib.context import CryptContext

        self._db = db  # instance variable unique to each instance

    ##########################################################################################################
    ##########################################################################################################
    # User Login and Registration Related helpers
    ##########################################################################################################
    ##########################################################################################################
    # --------------------------------------------------
    # Get User Details (get a user based on userName)
    # --------------------------------------------------

    def get_user(self, username: str) -> (bool, dict):
        from bson import json_util
        import json

        # use a collection named "Users"
        try:
            users_collection = self._db["Users"]
            # We  find a single document. Let's find a document
            # that has the email in the email  .
            user_doc = users_collection.find_one({"username": username})
            user_doc_json = json.loads(json_util.dumps(user_doc))
            #print(f'inside get_user= {user_doc}')
            del user_doc_json['_id']
            #print('timestmp', user_doc_json["timestamp_lastlogged"])
            user_doc_json["timestamp_lastlogged"] = user_doc_json["timestamp_lastlogged"]["$date"]
            if 'admin_user_flag' not in user_doc_json.keys():
                user_doc_json["admin_user_flag"] = False
            if 'hashed_password' not in user_doc_json.keys():
                user_doc_json["hashed_password"] = ""
            #print(f'inside get_user= {user_doc_json}')
            user = UserInDB(**user_doc_json)
            return user
        except Exception as e:
            print(e)
            return False

    # --------------------------------------------------
    # Get All Users
    # --------------------------------------------------
    def get_all_users(self) -> (bool, [dict]):
        from bson import json_util
        import json
        #print(f"inside get all users")
        # use a collection named "Users"
        try:
            user_doc_list = []
            users_collection = self._db["Users"]
            # We  find a single document. Let's find a document
            # that has the email in the email  .
            user_docs = users_collection.find()
            for user_doc in user_docs:
                #print(f'inside get all users doc= {user_doc}')
                user_doc_json = json.loads(json_util.dumps(user_doc))
                user_doc_list.append(user_doc_json)
                #print(f"inside get all users {user_doc_json}")
            #print(f"list is {user_doc_list}")
            return True, user_doc_list

        except Exception as e:
            print(f"E$rror: {e}")
            return False, None

    # --------------------------------------------------
    # Update User Details (#Update user details)
    # --------------------------------------------------
    def update_user(self, _user) -> str:
        from bson import json_util
        import json

        # use a collection named "Users"
        users_collection = self._db["Users"]
        try:
            user_doc = users_collection.find_one_and_update({"username": _user.username},
                                                            {"$set":
                                                                 {"password": _user.password,
                                                                  "hashed_password": _user.hashed_password,
                                                                  "firstName": _user.firstName,
                                                                  "lastName": _user.lastName,
                                                                  "email": _user.email,
                                                                  "active": _user.active,
                                                                  "admin_user_flag": _user.admin_user_flag
                                                                  }},
                                                            new=True)
            user_doc_json = json.loads(json_util.dumps(user_doc))
        except Exception as e:
            print(e)
            return None

        return user_doc_json

    # --------------------------------------------------
    # Create User Details (#craeate user details)
    # --------------------------------------------------
    def create_user(self, p_user) -> (bool, str):

        from datetime import datetime
        import json
        _user = p_user
        _user_doc = {
            "username": _user.username,
            "password": _user.password,
            "hashed_password": _user.hashed_password,
            "email": _user.email,
            "firstName": _user.firstName,
            "lastName": _user.lastName,
            "active": 1,
            "timestamp_lastlogged": datetime.now(),
            "admin_user_flag": _user.admin_user_flag
        }

        users_collection = self._db["Users"]
        alreadyExisting = False;
        try:
            # We  find a single document. Let's find a document that has the userName in the userName  .
            rslt = users_collection.find_one({"username": _user_doc["username"]})
            print(f"trying to find user, result = {rslt}")
            if rslt is None:
                alreadyExisting = False
            else:
                alreadyExisting = True
                return False, f'User {_user_doc["username"]} already exists'
        except Exception as e:
            print(e)
            return False, f'User {_user_doc["username"]} , Error = {e}'

        try:
            print(f"all good, inserting -- {_user_doc}")
            result = users_collection.insert_one(_user_doc)
            return True, f'User {_user_doc["username"]} successfully created'
        # return a friendly error if the operation fails
        except Exception as e:
            print(e)
            return False, f'Erorr in creating User {_user_doc["username"]}, error = {e} '

    # --------------------------------------------------
    # Delete user
    # --------------------------------------------------
    def delete_user(self, username: str):
        users_collection = self._db["Users"]
        print("delete user:",username)

        result = users_collection.find_one({"username": username})
        if result:
            query_filter = {'username': username}
            result = users_collection.delete_many(query_filter)
            print("result", result)

        return username
