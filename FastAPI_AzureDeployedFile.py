from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

import os
import logging

from pyzeebe import ZeebeClient
from pyzeebe.channel.oauth_channel import create_camunda_cloud_channel


# -------------------------------------------------
# Logging
# -------------------------------------------------

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


# -------------------------------------------------
# Load environment
# -------------------------------------------------

load_dotenv()


# -------------------------------------------------
# FastAPI App
# -------------------------------------------------

app = FastAPI(
    title="ATO SuperStream Rollover API",
    version="1.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# -------------------------------------------------
# Camunda Configuration
# -------------------------------------------------

CAMUNDA_CLIENT_ID = os.getenv("CAMUNDA_CLIENT_ID")
CAMUNDA_CLIENT_SECRET = os.getenv("CAMUNDA_CLIENT_SECRET")
CAMUNDA_CLUSTER_ID = os.getenv("CAMUNDA_CLUSTER_ID")
CAMUNDA_REGION = os.getenv("CAMUNDA_REGION")


zeebe_client = None



@app.on_event("startup")
async def startup_event():

    global zeebe_client


    try:

        logger.info("Connecting to Camunda Cloud...")


        if not all([
            CAMUNDA_CLIENT_ID,
            CAMUNDA_CLIENT_SECRET,
            CAMUNDA_CLUSTER_ID,
            CAMUNDA_REGION
        ]):

            raise Exception(
                "Missing Camunda environment variables"
            )


        channel = create_camunda_cloud_channel(

            client_id=CAMUNDA_CLIENT_ID,

            client_secret=CAMUNDA_CLIENT_SECRET,

            cluster_id=CAMUNDA_CLUSTER_ID,

            region=CAMUNDA_REGION

        )


        zeebe_client = ZeebeClient(

            channel

        )


        logger.info(
            "Connected to Camunda Cloud"
        )


    except Exception as e:

        logger.error(
            f"Camunda initialization failed: {e}"
        )




# -------------------------------------------------
# Request Model
# -------------------------------------------------

class RolloverRequest(BaseModel):

    memberId: str

    memberName: str

    sourceFund: str

    destinationFund: str

    amount: float



# -------------------------------------------------
# Health Check
# -------------------------------------------------

@app.get("/")
async def root():

    return {

        "application":
        "ATO SuperStream Rollover API",

        "status":
        "RUNNING"

    }



# -------------------------------------------------
# Start Process
# -------------------------------------------------

@app.post("/rollover")
async def start_rollover(
        request: RolloverRequest
):


    if zeebe_client is None:

        raise HTTPException(

            status_code=500,

            detail="Camunda client not initialized"

        )


    variables = {

        "memberId": request.memberId,

        "memberName": request.memberName,

        "sourceFund": request.sourceFund,

        "destinationFund": request.destinationFund,

        "amount": request.amount,

        "approvalStatus": "",

        "approvalComments": ""

    }


    try:


        result = await zeebe_client.run_process(

            bpmn_process_id="ato_superstream_rollover",

            variables=variables

        )


        return {


            "status":
            "STARTED",


            "processInstanceKey":
            str(
                result.process_instance_key
            )

        }



    except Exception as e:


        logger.error(
            str(e)
        )


        raise HTTPException(

            status_code=500,

            detail=str(e)

        )



# -------------------------------------------------
# Status
# -------------------------------------------------

process_status = {}



@app.get("/status/{process_key}")
async def status(process_key:str):


    return {


        "processInstanceKey":
        process_key,


        "status":
        process_status.get(
            process_key,
            "UNKNOWN"
        )


    }