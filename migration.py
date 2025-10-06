import csv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from bson.decimal128 import Decimal128
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
import re
import os

def migrate_csv_to_mongodb(csv_file_path, db_name, collection_name, mongo_uri):
    """
    Migrates data from a CSV file to a MongoDB collection.

    :param csv_file_path: Path to the CSV file.
    :param db_name: Name of the MongoDB database.
    :param collection_name: Name of the MongoDB collection.
    :param mongo_uri: The MongoDB connection URI.
    """
    print("Starting the migration process...")

    try:
        # Establish connection to MongoDB
        client = MongoClient(mongo_uri)
        # Test the connection
        client.admin.command('ping')
        print("Successfully connected to MongoDB.")
    except ConnectionFailure as e:
        print(f"Could not connect to MongoDB: {e}")
        return

    db = client[db_name]
    collection = db[collection_name]

    # Clear existing data in the collection to avoid duplicates on re-runs
    print(f"Clearing existing data from collection: {collection_name}...")
    collection.delete_many({})

    print(f"Reading data from {csv_file_path} and inserting into MongoDB...")
    try:
        with open(csv_file_path, mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            
            # 1. Initial cleaning and collection
            data_to_process = []
            for row in csv_reader:
                try:
                    # Clean text fields
                    name = row['Name']
                    name = re.sub(r'^(Mr\.|Mrs\.|Dr\.|Miss)\s*', '', name, flags=re.IGNORECASE)
                    row['Name'] = name.strip().title()
                    row['Gender'] = row['Gender'].title()
                    row['Medical Condition'] = row['Medical Condition'].title()
                    row['Admission Type'] = row['Admission Type'].title()
                    row['Medication'] = row['Medication'].title()
                    row['Test Results'] = row['Test Results'].title()
                    row['Doctor'] = row['Doctor'].title()
                    row['Hospital'] = row['Hospital'].title()
                    row['Insurance Provider'] = row['Insurance Provider'].title()

                    # Convert types that are hashable
                    row['Age'] = int(row['Age'])
                    # Keep Billing Amount and dates as strings for now for deduplication
                    
                    data_to_process.append(row)
                except (ValueError, TypeError) as e:
                    print(f"Skipping row during initial processing: {row} - Error: {e}")
                    continue
            
            # 2. Deduplication
            unique_data_intermediate = []
            seen = set()
            for row in data_to_process:
                row_tuple = tuple(row.items())
                if row_tuple not in seen:
                    seen.add(row_tuple)
                    unique_data_intermediate.append(row)
            
            print(f"Removed {len(data_to_process) - len(unique_data_intermediate)} duplicate rows.")

            # 3. Final type conversion for non-hashable types
            final_data_to_insert = []
            for row in unique_data_intermediate:
                try:
                    # Convert Billing Amount to Decimal128
                    billing_amount_decimal = Decimal(row['Billing Amount']).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                    row['Billing Amount'] = Decimal128(billing_amount_decimal)
                    
                    # Convert date fields
                    row['Date of Admission'] = datetime.strptime(row['Date of Admission'], '%Y-%m-%d')
                    row['Discharge Date'] = datetime.strptime(row['Discharge Date'], '%Y-%m-%d')
                    
                    final_data_to_insert.append(row)
                except (ValueError, TypeError) as e:
                    print(f"Skipping row during final conversion: {row} - Error: {e}")
                    continue

            # 4. Insert data in bulk
            if final_data_to_insert:
                collection.insert_many(final_data_to_insert)
                print(f"Successfully inserted {len(final_data_to_insert)} unique documents into the collection.")
            else:
                print("No data to insert.")

    except FileNotFoundError:
        print(f"Error: The file {csv_file_path} was not found.")
    except Exception as e:
        print(f"An error occurred during the migration: {e}")
    finally:
        # Close the connection
        client.close()
        print("MongoDB connection closed.")

import time

def wait_for_mongo(mongo_uri, timeout=120):
    """
    Waits for the MongoDB service to be available.

    :param mongo_uri: The MongoDB connection URI.
    :param timeout: The maximum time to wait in seconds.
    """
    print("Waiting for MongoDB to be available...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            client = MongoClient(mongo_uri, serverSelectionTimeoutMS=2000)
            client.admin.command('ping')
            print("MongoDB is available.")
            client.close()
            return True
        except ConnectionFailure:
            print("MongoDB not available yet, retrying in 5 seconds...")
            time.sleep(5)
    print("Failed to connect to MongoDB after several retries.")
    return False

if __name__ == "__main__":
    # Get configuration from environment variables
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://root:password@mongodb:27017/')
    DB_NAME = os.environ.get('DB_NAME', 'healthcare')
    COLLECTION_NAME = os.environ.get('COLLECTION_NAME', 'patients')
    CSV_FILE = os.environ.get('OUTPUT_CSV_FILE', 'healthcare_dataset_cleaned.csv')

    # Wait for MongoDB to be ready
    if wait_for_mongo(MONGO_URI):
        # Run the migration
        migrate_csv_to_mongodb(CSV_FILE, DB_NAME, COLLECTION_NAME, MONGO_URI)
