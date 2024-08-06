import pymongo


class ObservationHelper:
    import src.AvaGuardHelpers.avaguard_models as uMdl

    def __init__(self, db):
        self._db = db  # instance variable unique to each instance

    ##########################################################################################################
    ##########################################################################################################
    # Observation Related helpers
    ##########################################################################################################
    ##########################################################################################################
    # --------------------------------------------------
    # Get Observation Details (get an Observation based on Id)
    # --------------------------------------------------

    def get_all_observations(self, username: str):
        # use a collection named "Observation"
        #print(f"username = {username}")
        from bson import json_util
        import json
        from operator import itemgetter


        # use a collection named "Users"
        try:
            obs_doc_list = []
            observations_collection = self._db["OBSERVATIONS"]
            if username == "ALL_USERS":
                # We  find a single document. Let's find a document
                obs_docs = observations_collection.find().sort("datetime_taken_UTC",pymongo.DESCENDING)
            else:
                obs_docs = observations_collection.find({"submitted_user": username})\
                            .sort("datetime_taken_UTC",pymongo.DESCENDING)
            for obs_doc in obs_docs:
                #print(f'inside get all obs doc= {obs_doc}')
                obs_doc_json = json.loads(json_util.dumps(obs_doc))
                obs_doc_list.append(obs_doc_json)
                #print(f"inside get all obs {obs_doc_json}")
            #print(f"unsorted list is {len(obs_doc_list)}, time taken = {obs_doc_list[51]}")
            #obs_doc_list = sorted(obs_doc_list, key=itemgetter('datetime_taken_UTC').isoformat(), reverse=True)
            #print(f"sorted list is {len(obs_doc_list)}")

            return True, obs_doc_list

        except Exception as e:
            print(f"E$rror: {e}")
            return False, None

    def get_observation(self, obs_id: str):
        from bson import json_util
        import json
        # use a collection named "observations"
        observations_collection = self._db["OBSERVATIONS"]
        # We  find a single document. Let's find a document
        obs_doc = observations_collection.find_one({"observation_id": obs_id})
        obs_doc_json = json.loads(json_util.dumps(obs_doc))
        print("Inside obshelper, ",obs_doc_json)
        return obs_doc_json

    # --------------------------------------------------
    # Update Observation Details (#Update user details)
    # --------------------------------------------------
    def update_observation(self, p_observation: uMdl.Observation):
        _observation = p_observation
        # use a collection named "Users"
        observations_collection = self._db["OBSERVATIONS"]
        observation_doc = observations_collection.find_one_and_update({"observation_id": _observation.id},
                                                                      {"$set":
                                                                          {
                                                                              "timestamp_submitted_UTC": _observation.timestamp_submitted,
                                                                              "imagefile_url": _observation.imagefile_url,
                                                                              "image_notes": _observation.image_notes,
                                                                              "avalanche": _observation.avalanche,
                                                                              "cracking": _observation.cracking,
                                                                              "collapsing": _observation.collapsing,
                                                                              "lat": _observation.lat,
                                                                              "lng": _observation.lng,
                                                                              "username": _observation.username
                                                                          }},
                                                                      new=True)

        return observation_doc

    # --------------------------------------------------
    # Delete observation
    # --------------------------------------------------
    def delete_observation(self, observation_id: str):
        observations_collection = self._db["OBSERVATIONS"]
        query_filter = {'observation_id': observation_id}
        result = observations_collection.delete_many(query_filter)
        print("result count", result.deleted_count)
        print("result", result.raw_result)
        return observation_id

    # --------------------------------------------------
    # Update User Details (#Update user details) (pass a dict)
    # --------------------------------------------------
    def create_observation(self, p_observation):
        print("Creating observation .....................")
        observations_collection = self._db["OBSERVATIONS"]

        print("p_observation:", p_observation)
        result = None
        try:
            result = observations_collection.insert_one(p_observation)
            print("I inserted document")
        # return a friendly error if the operation fails
        except Exception as e:
            print("an error occured {0}".format(e))
        else:
            pass

        return result
