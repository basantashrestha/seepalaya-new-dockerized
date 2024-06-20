import psycopg2
from elasticsearch import Elasticsearch
from decouple import config

DB_HOST = config("POSTGRES_HOST")
DB_PORT = config("POSTGRES_PORT")
DB_USER = config("POSTGRES_USER")
DB_PASSWORD = config("POSTGRES_PASSWORD")
DB_NAME = "pustakalaya" 

ES_HOST = config("ES_HOST")
ES_PORT = config("ES_PORT")
ES_INDEX = "pustakalaya"

def connect_to_postgres():
    """Establishes a connection to the PostgreSQL database."""
    try:
        connection = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
        )
        return connection
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL:", error)
        return None

def connect_to_elasticsearch():
    """Establishes a connection to the Elasticsearch instance."""
    try:
        es = Elasticsearch([{"host": ES_HOST, "port": ES_PORT}])
        return es
    except Exception as error:
        print("Error while connecting to Elasticsearch:", error)
        return None

def recreate_index():
    """Drops the existing index if it exists and creates a new one."""
    es = connect_to_elasticsearch()
    if es:
        try:
            if es.indices.exists(index=ES_INDEX):
                es.indices.delete(index=ES_INDEX)
                print(f"Deleted existing index: {ES_INDEX}")
            
            es.indices.create(index=ES_INDEX)
            print(f"Created new index: {ES_INDEX}")
        except Exception as error:
            print("Error while recreating Elasticsearch index:", error)

def index_data(data):
    """Indexes data to the specified Elasticsearch index."""
    es = connect_to_elasticsearch()
    if es:
        try:
            response = es.index(index=ES_INDEX, id=data["id"], body=data)
            print("Document indexed successfully:", response)
        except Exception as error:
            print("Error while indexing data:", error)

def main():
    """
    Fetches specific columns from multiple PostgreSQL tables and indexes them to Elasticsearch in batches.
    """
    recreate_index()

    connection = connect_to_postgres()
    if connection:
        tables_to_index = {
            "document_document": ["id", "title", "created_date", "updated_date", "type", "thumbnail", "abstract"],
            "audio": ["id", "title", "created_date", "updated_date", "type", "thumbnail", "abstract"],
            "video_video": ["id", "title", "created_date", "updated_date", "type", "thumbnail", "abstract"]
        }
        for table, columns in tables_to_index.items():
            cursor = connection.cursor()
            column_list = ", ".join(columns)
            query = f"SELECT {column_list} FROM {table} where published='yes'"
            cursor.execute(query)

            data_to_index = []
            for row in cursor.fetchall():
                # Use 'id' column as _id and create a dictionary with other columns
                data = {col: value for col, value in zip(columns + ["id"], row)}
                data_to_index.append(data)

            # Batch indexing using a list comprehension
            batch_size = 1000
            data_chunks = [data_to_index[i:i + batch_size] for i in range(0, len(data_to_index), batch_size)]
            for data_batch in data_chunks:
                bulk_actions = [{"index": {"_index": ES_INDEX, "_id": doc["id"]}} | doc for doc in data_batch]
                es = connect_to_elasticsearch()
                response = es.bulk(body=bulk_actions)
                if response["errors"]:
                    print(f"Error indexing some documents from table {table}:", response)
                else:
                    print(f"Successfully indexed {len(data_batch)} documents from table {table}.")

        connection.close()
    else:
        print("Failed to connect to PostgreSQL")

if __name__ == "__main__":
    main()
