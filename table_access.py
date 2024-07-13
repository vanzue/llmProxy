import json
import uuid
from azure.identity import ClientSecretCredential
from azure.data.tables import TableServiceClient, UpdateMode
import os
from dotenv import load_dotenv

load_dotenv()


class JobStatusDataAccess:
    def __init__(self):
        CLIENT_ID = os.getenv('AZURE_CLIENT_ID', 'your_client_id')
        TENANT_ID = os.getenv('AZURE_TENANT_ID', 'your_tenant_id')
        CLIENT_SECRET = os.getenv('AZURE_CLIENT_SECRET', 'your_client_secret')
        STORAGE_ACCOUNT_NAME = "comicstorage"
        TABLE_NAME = "jobs"
        self.credential = ClientSecretCredential(
            tenant_id=TENANT_ID, client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
        self.table_service_client = TableServiceClient(
            endpoint=f"https://{STORAGE_ACCOUNT_NAME}.table.core.windows.net", credential=self.credential)
        self.table_name = TABLE_NAME

    def __enter__(self):
        self.table_client = self.table_service_client.get_table_client(
            table_name=self.table_name)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.table_client.close()
        self.table_service_client.close()

    def add(self, partition_key, row_key, job_id, job_status, stories, result):
        entity = {
            'PartitionKey': partition_key,
            'RowKey': row_key,
            'JobId': job_id,
            'JobStatus': job_status,
            'Stories': stories,
            'Result': result
        }
        self.table_client.create_entity(entity=entity)

    def update(self, partition_key, row_key, job_id, job_status, stories, result):
        entity = {
            'PartitionKey': partition_key,
            'RowKey': row_key,
            'JobId': job_id,
            'JobStatus': job_status,
            'Stories': stories,
            'Result': result
        }
        self.table_client.update_entity(entity=entity, mode=UpdateMode.REPLACE)

    def get(self, partition_key, row_key):
        entity = self.table_client.get_entity(
            partition_key=partition_key, row_key=row_key)
        return {
            'JobId': entity.get('JobId'),
            'JobStatus': entity.get('JobStatus'),
            'stories': entity.get('Stories'),
            'Result': entity.get('Result')
        }


class UserDataAccess:
    def __init__(self):
        CLIENT_ID = os.getenv('AZURE_CLIENT_ID', 'your_client_id')
        TENANT_ID = os.getenv('AZURE_TENANT_ID', 'your_tenant_id')
        CLIENT_SECRET = os.getenv('AZURE_CLIENT_SECRET', 'your_client_secret')
        STORAGE_ACCOUNT_NAME = "comicstorage"
        TABLE_NAME = "userprofile"
        self.credential = ClientSecretCredential(
            tenant_id=TENANT_ID, client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
        self.table_service_client = TableServiceClient(
            endpoint=f"https://{STORAGE_ACCOUNT_NAME}.table.core.windows.net", credential=self.credential)
        self.table_name = TABLE_NAME

    def __enter__(self):
        self.table_client = self.table_service_client.get_table_client(
            table_name=self.table_name)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.table_client.close()
        self.table_service_client.close()

    def add(self, partition_key, row_key, profile_done, user_description, seed, style):
        entity = {
            'PartitionKey': partition_key,
            'RowKey': row_key,
            'ProfileDone': profile_done,
            'UserDescription': user_description,
            'Seed': seed,
            'Style': style
        }
        self.table_client.create_entity(entity=entity)

    def upsert(self, partition_key, row_key, profile_done, user_description, seed, style):
        entity = {
            'PartitionKey': partition_key,
            'RowKey': row_key,
            'ProfileDone': profile_done,
            'UserDescription': user_description,
            'Seed': seed,
            'Style': style
        }
        self.table_client.upsert_entity(entity=entity)

    def get(self, partition_key, row_key):
        try:
            entity = self.table_client.get_entity(
                partition_key=partition_key, row_key=row_key)
            return {
                'ProfileDone': entity.get('ProfileDone'),
                'UserDescription': entity.get('UserDescription'),
                'Seed': entity.get('Seed'),
                'Style': entity.get('Style')
            }
        except:
            return None


def getUserProfile(openid):
    with UserDataAccess() as userDataAccess:
        user_profile = userDataAccess.get(openid, openid)
        return user_profile


def userSetupDone(openid):
    with UserDataAccess() as userDataAccess:
        user_profile = userDataAccess.get(openid, openid)
        if not user_profile:
            return False
        setup_done = user_profile.get('ProfileDone')
        return setup_done


class SessionDataAccess:
    def __init__(self):
        CLIENT_ID = os.getenv('AZURE_CLIENT_ID', 'your_client_id')
        TENANT_ID = os.getenv('AZURE_TENANT_ID', 'your_tenant_id')
        CLIENT_SECRET = os.getenv('AZURE_CLIENT_SECRET', 'your_client_secret')
        STORAGE_ACCOUNT_NAME = "comicstorage"
        TABLE_NAME = "session"
        self.credential = ClientSecretCredential(
            tenant_id=TENANT_ID, client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
        self.table_service_client = TableServiceClient(
            endpoint=f"https://{STORAGE_ACCOUNT_NAME}.table.core.windows.net", credential=self.credential)
        self.table_name = TABLE_NAME

    def __enter__(self):
        self.table_client = self.table_service_client.get_table_client(
            table_name=self.table_name)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.table_client.close()
        self.table_service_client.close()

    def add(self, session_token, openid):
        entity = {
            'PartitionKey': session_token,
            'RowKey': session_token,
            'OpenId': openid,
        }
        self.table_client.create_entity(entity=entity)

    # catch exception outside the function.
    def get(self, session_token):
        entity = self.table_client.get_entity(
            partition_key=session_token, row_key=session_token)
        return {
            'OpenId': entity.get('OpenId')
        }


class CollectionDataAccess:
    def __init__(self):
        CLIENT_ID = os.getenv('AZURE_CLIENT_ID', 'your_client_id')
        TENANT_ID = os.getenv('AZURE_TENANT_ID', 'your_tenant_id')
        CLIENT_SECRET = os.getenv('AZURE_CLIENT_SECRET', 'your_client_secret')
        STORAGE_ACCOUNT_NAME = "comicstorage"
        TABLE_NAME = "usercollection"
        self.credential = ClientSecretCredential(
            tenant_id=TENANT_ID, client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
        self.table_service_client = TableServiceClient(
            endpoint=f"https://{STORAGE_ACCOUNT_NAME}.table.core.windows.net", credential=self.credential)
        self.table_name = TABLE_NAME

    def __enter__(self):
        self.table_client = self.table_service_client.get_table_client(
            table_name=self.table_name)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.table_client.close()
        self.table_service_client.close()

    # compressed_comics is json list of urls of compressed images.
    # comics is json list of urls of original images.
    # open_id is the user's open_id.
    # collection_name is the name of the collection.
    def addCollection(self, openid, collection_name,  compressed_comics, comics):
        entity = {
            'PartitionKey': openid+collection_name,
            'RowKey': openid+collection_name,
            'OpenId': openid,
            'CollectionName': collection_name,
            'CompressedComics': json.dumps(compressed_comics),
            'Comics': json.dumps(comics)
        }
        self.table_client.create_entity(entity=entity)

    # get all collections of a user.
    # filter_query = f"OpenId eq '{openid}'"
    # entities = sessionDataAccess.table_client.query_entities(
    # query_filter=filter_query)
    def getCollections(self, openid):
        query_filter = f"OpenId eq '{openid}'"
        entities = self.table_client.query_entities(query_filter=query_filter)
        result = []

        for entity in entities:
            compressed_comics_json = entity.get('CompressedComics', '[]')
            comics_json = entity.get('Comics', '[]')
            result.append({
                'CollectionName': entity.get('CollectionName'),
                'CompressedComics': json.loads(compressed_comics_json),
                'Comics': json.loads(comics_json)
            })

        return result

    def addComicToCollection(self, openid, collection_name, compressed_comic, comic):
        entity = self.table_client.get_entity(
            partition_key=openid+collection_name, row_key=openid+collection_name)

        compressed_comics_json = entity.get('CompressedComics', '[]')
        comics_json = entity.get('Comics', '[]')

        # Parse the JSON strings into Python lists
        compressed_comics = json.loads(compressed_comics_json)
        comics = json.loads(comics_json)

        # Add the new items to the lists
        compressed_comics.append(compressed_comic)
        comics.append(comic)

        # Convert the lists back into JSON strings
        entity['CompressedComics'] = json.dumps(compressed_comics)
        entity['Comics'] = json.dumps(comics)

        # Update the entity in the table
        self.table_client.update_entity(entity)
        return True

    def updateCollection(self, openid, collection_name, compressed_comics, urls):
        entity = self.table_client.get_entity(
            partition_key=openid+collection_name, row_key=openid+collection_name)
        # Convert the lists back into JSON strings
        entity['CompressedComics'] = json.dumps(compressed_comics)
        entity['Comics'] = json.dumps(urls)

        # Update the entity in the table
        self.table_client.update_entity(entity)
        return True

################### PUBLICLY ACCESSIBLE FUNCTIONS####################


def get_openid_by_session(session_token):
    with SessionDataAccess() as sessionDataAccess:
        try:
            item = sessionDataAccess.get(session_token)
            return item.get('OpenId')
        except:
            return ""


def get_session_by_openid(openid):
    with SessionDataAccess() as sessionDataAccess:
        try:
            filter_query = f"OpenId eq '{openid}'"
            entities = sessionDataAccess.table_client.query_entities(
                que_firylter=filter_query)
            item = next(entities)
            return item.get('PartitionKey')
        except Exception as e:
            print(e)
            return ""


def generate_session_token():
    return str(uuid.uuid4())


def new_session(openid):
    with SessionDataAccess() as sessionDataAccess:
        session_token = generate_session_token()
        sessionDataAccess.add(session_token, openid)
        return session_token


if __name__ == "__main__":
    with CollectionDataAccess() as collectionDataAccess:
        new_session("12345")
