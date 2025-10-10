import os
import time
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

MONGO_URI = os.getenv("MONGO_URI", "mongodb://root:password@mongodb:27017/")

def wait_for_mongo(uri, timeout=60):
    start_time = time.time()
    while True:
        try:
            client = MongoClient(uri, serverSelectionTimeoutMS=2000)
            client.admin.command("ping")  # test rapide de connexion
            print("✅ MongoDB est prêt !")
            return True
        except ServerSelectionTimeoutError as e:
            elapsed = int(time.time() - start_time)
            if elapsed > timeout:
                print("❌ Timeout : MongoDB n'a pas démarré dans le délai imparti")
                raise e
            print(f"⏳ MongoDB pas encore prêt... nouvelle tentative dans 2s ({elapsed}/{timeout}s)")
            time.sleep(2)

if __name__ == "__main__":
    wait_for_mongo(MONGO_URI)

