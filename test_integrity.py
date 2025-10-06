from pymongo import MongoClient

def test_data_integrity(db_name, collection_name, mongo_uri="mongodb://localhost:27017/"):
    """
    Performs data integrity tests on a MongoDB collection.

    :param db_name: Name of the MongoDB database.
    :param collection_name: Name of the MongoDB collection.
    :param mongo_uri: The MongoDB connection URI.
    """
    print("Starting data integrity tests...")
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]

    # 1. Check if the collection has documents
    document_count = collection.count_documents({})
    print(f"Test 1: Document count. Found {document_count} documents.")
    assert document_count > 0, "Test 1 Failed: No documents found in the collection."
    print("Test 1 Passed: Collection is not empty.")

    # 2. Verify that expected fields are present
    print("\nTest 2: Field presence.")
    expected_fields = ['Name', 'Age', 'Gender', 'Blood Type', 'Medical Condition', 'Date of Admission', 'Doctor', 'Hospital', 'Insurance Provider', 'Billing Amount', 'Room Number', 'Admission Type', 'Discharge Date', 'Medication', 'Test Results']
    sample_document = collection.find_one()
    missing_fields = [field for field in expected_fields if field not in sample_document]
    assert not missing_fields, f"Test 2 Failed: Missing fields: {missing_fields}"
    print("Test 2 Passed: All expected fields are present in a sample document.")

    # 3. Check for missing values in key fields
    print("\nTest 3: Check for null or empty values in the 'Name' field.")
    null_name_count = collection.count_documents({"Name": {"$in": [None, ""]}})
    assert null_name_count == 0, f"Test 3 Failed: Found {null_name_count} documents with null or empty names."
    print("Test 3 Passed: No documents with null or empty names.")

    # 4. Check for duplicates
    print("\nTest 4: Check for duplicate documents.")
    pipeline = [
        {
            "$group": {
                "_id": {key: f"${key}" for key in expected_fields}, 
                "count": {"$sum": 1}
            }
        },
        {
            "$match": {
                "count": {"$gt": 1}
            }
        }
    ]
    duplicates = list(collection.aggregate(pipeline))
    assert len(duplicates) == 0, f"Test 4 Failed: Found {len(duplicates)} duplicate documents."
    print("Test 4 Passed: No duplicate documents found.")

    print("\nAll data integrity tests passed!")
    client.close()

import os

if __name__ == "__main__":
    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
    DB_NAME = os.environ.get("DB_NAME", "healthcare")
    COLLECTION_NAME = os.environ.get("COLLECTION_NAME", "patients")
    test_data_integrity(DB_NAME, COLLECTION_NAME, MONGO_URI)
