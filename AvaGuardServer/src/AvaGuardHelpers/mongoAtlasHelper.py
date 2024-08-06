##########################################################################################################
##########################################################################################################
# MongoDB Atlas Related
##########################################################################################################
##########################################################################################################
# for mongodb


# --------------------------------------------------
# MongoDB atlas Helpers
# --------------------------------------------------
def init_mangodb_connection():
    import pymongo
    import sys

    try:
        client = pymongo.MongoClient(
            "mongodb+srv://username:password@servername.uwanzqc.mongodb.net/?retryWrites=true&w"
            "=majority&appName=AvaGuardMongoDB01"
        )

    # return a friendly error if a URI error is thrown
    except pymongo.errors.ConfigurationError:
        print("An Invalid URI host error was received. Is your Atlas host name correct in your connection string?")
        sys.exit(1)

    # use database AVALANCHEGUARD
    db = client.AVALANCHEGUARD

    return db
