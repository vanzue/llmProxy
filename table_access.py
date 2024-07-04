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

    # partitionKey, rowKey should now be openId, 
    # profile done indicate whether the user has completed the profile.
    # <session_token> is now the token for the session of client side.
    # If user has onboarded while session_token is null, he will go find a new session_key, we should return all other things 
    # to the user in case things changed.
    
    # <user_description> is the description of the user, for generating new comics.
    # <seed> is used for dalle to maintain the characteristics of the user.
    # Style? Do we need style? Maybe leave here for now.
    def add(self, partition_key, row_key, session_token, profile_done, user_description, seed, style):
        entity = {
            'PartitionKey': partition_key,
            'RowKey': row_key,
            'SessionToken': session_token,
            'ProfileDone': profile_done,
            'UserDescription': user_description,
            'Seed': seed,
            'Style': style
        }
        self.table_client.create_entity(entity=entity)

    def update(self, partition_key, row_key, session_token, profile_done, user_description, seed, style):
        entity = {
            'PartitionKey': partition_key,
            'RowKey': row_key,
            'SessionToken': session_token,
            'ProfileDone': profile_done,
            'UserDescription': user_description,
            'Seed': seed,
            'Style': style
        }
        self.table_client.update_entity(entity=entity, mode=UpdateMode.REPLACE)

    def get(self, partition_key, row_key):
        entity = self.table_client.get_entity(
            partition_key=partition_key, row_key=row_key)
        return {
            'SessionToken': entity.get('SessionToken'),
            'ProfileDone': entity.get('ProfileDone'),
            'UserDescription': entity.get('UserDescription'),
            'Seed': entity.get('Seed'),
            'Style': entity.get('Style')
        }


# if __name__ == "__main__":
#     with JobStatusDataAccess() as data_access:
#         data_access.add('Partition1', '12345', '12345', 'Pending', '[]', 'done')

#         data_access.update('Partition1', '12345', '12345',
#                            'Completed', 'Success', 'done')

#         job_status = data_access.get('Partition1', '12345')
#         print(f"Job Status: {job_status}")
#         print(f"Job Result: {job_status['Result']}")

if __name__ == "__main__":
    with UserDataAccess() as data_access:
        #data_access.add('Partition1', 'Partition1', '12345', "True", 'black hair, blue eyes, glasses', '12345', 'cartoon')

        #data_access.update('user1', 'user1', '12345', "True", 'black hair, blue eyes, glasses', '123123123', 'cartoon')

        user = data_access.get('notexisted', 'notexisted')
        print(f"Description: {user.get('UserDescription')}")