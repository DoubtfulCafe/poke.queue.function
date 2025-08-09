import io
import os
import azure.functions as func
import datetime
import json
import logging
import requests
from dotenv import load_dotenv


app = func.FunctionApp()
load_dotenv()

logging.basicConfig( level=logging.INFO )
logger = logging.getLogger(__name__)

DOMAIN = os.getenv("DOMAIN")
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
BLOB_CONTAINER_NAME = os.getenv("BLOB_CONTAINER_NAME")
STORA_ACCOUNT_NAME = os.getenv("STORA_ACCOUNT_NAME")

@app.queue_trigger(
    arg_name="azqueue"
    , queue_name="requests"
    , connection="QueueAzureWebJobsStorage"
)
def QueueTriggerPokeReport(azqueue: func.QueueMessage):
    body = azqueue.get_body().decode('utf-8')
    record = json.loads(body)
    id = record[0]["id"]

    update_request(id, "inprogress")

    request_info = get_request(id)
    pokemons = get_pokemons(request_info[0]["type"])
    logging.info(pokemons)

    update_request(id, "completed")


def update_request( id: int, status: str, url: str = None ) -> dict:
    payload = {
        "status": status
        , "id": id
    }
    if url:
        payload["url"] = url

    reponse = requests.put( f"{DOMAIN}/api/request" , json=payload )
    return reponse.json()

def get_request(id: int) -> dict:
    reponse = requests.get( f"{DOMAIN}/api/request/{id}"  )
    return reponse.json()

def get_pokemons( type: str ) -> dict:
    pokeapi_url = f"https://pokeapi.co/api/v2/type/{type}"
    response = requests.get(pokeapi_url, timeout=3000)
    data = response.json()
    pokemon_entries = data.get("pokemon", [] )
    return [ p["pokemon"] for p in pokemon_entries ]