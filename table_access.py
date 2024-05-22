from azure.identity import ClientSecretCredential
from azure.data.tables import TableServiceClient, UpdateMode
import os


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

    def add(self, partition_key, row_key, job_id, job_status, result):
        entity = {
            'PartitionKey': partition_key,
            'RowKey': row_key,
            'JobId': job_id,
            'JobStatus': job_status,
            'Result': result
        }
        self.table_client.create_entity(entity=entity)

    def update(self, partition_key, row_key, job_id, job_status, result):
        entity = {
            'PartitionKey': partition_key,
            'RowKey': row_key,
            'JobId': job_id,
            'JobStatus': job_status,
            'Result': result
        }
        self.table_client.update_entity(entity=entity, mode=UpdateMode.REPLACE)

    def get(self, partition_key, row_key):
        entity = self.table_client.get_entity(
            partition_key=partition_key, row_key=row_key)
        return {
            'JobId': entity.get('JobId'),
            'JobStatus': entity.get('JobStatus'),
            'Result': entity.get('Result')
        }


# Usage example
if __name__ == "__main__":
    # Example usage
    with JobStatusDataAccess() as data_access:
        # Add a new entity
        data_access.add('Partition1', '12345', '12345', 'Pending', '[]')

        # Update the entity
        data_access.update('Partition1', '12345', '12345',
                           'Completed', 'Success')

        # Get the entity
        job_status = data_access.get('Partition1', '12345')
        print(f"Job Status: {job_status}")
        print(f"Job Result: {job_status['Result']}")
