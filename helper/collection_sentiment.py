import datetime
import os
from multiprocessing import Process, Queue
from pprint import pprint
from time import sleep
from typing import Any, Dict, List
from urllib.parse import urlparse

from pymongo import MongoClient, UpdateOne
from pymongo.errors import BulkWriteError
from textblob import TextBlob


def consumer(queue) -> None:
    pid = os.getpid()
    print(f"Started Consumer #{pid}")
    count = 0
    while True:
        sleep(0.1)
        docs_batch = queue.get()
        if docs_batch is None:
            queue.put(None)
            break
        print(f"Consumer {pid} fetched job")
        bulk_ops: List[UpdateOne] = []
        for doc in docs_batch:
            if doc["text"] != "":
                blob = TextBlob(doc["text"])
                bulk_ops.append(
                    UpdateOne(
                        {"_id": doc["_id"]},
                        {
                            "$set": {
                                "nouns": blob.noun_phrases,
                                "sentiment": {
                                    "polarity": blob.sentiment.polarity,  # type: ignore
                                    "subjectivity": blob.sentiment.subjectivity,  # type: ignore
                                },
                                "updated_at": datetime.datetime.utcnow(),
                            },
                        },
                    )
                )
        try:
            if len(bulk_ops) > 0:
                coll.bulk_write(bulk_ops, ordered=False)
                count += len(bulk_ops)
                print(f"Consumer {pid}: {count} [{docs_batch[0]['_id']}]")
            else:
                print("! No jobs found, sleeping.")
                sleep(0.1)
        except BulkWriteError as bwe:
            pprint(bwe.details)


def producer(queue) -> None:
    print("Started Producer")
    batch_size = 1000
    doc_batch: List[Dict[str, Any]] = []
    cursor = coll.find({"sentiment": {"$exists": False}})
    for doc in cursor:
        if len(doc_batch) >= batch_size:
            print(f"added {len(doc_batch)} records")
            task_queue.put(doc_batch[:])
            doc_batch = []
        doc_batch.append(doc)
    task_queue.put(doc_batch[:])
    queue.put(None)
    print("Producer Finished")


task_queue = Queue(maxsize=100)
client: MongoClient[Dict[str, Any]] = MongoClient("mongodb://172.20.176.1:27017")
db = client["cs415_production"]
coll = db["twitter_stream"] # repeat for reddit_stream_submissions and reddit_stream_comments
consumer_procs = [Process(target=consumer, args=(task_queue,)) for i in range(20)]
for consumer_thread in consumer_procs:
    consumer.daemon = True
    consumer_thread.start()
producer_proc = Process(target=producer, args=(task_queue,))
producer_proc.start()
producer_proc.join()
for consumer_thread in consumer_procs:
    consumer_thread.join()
