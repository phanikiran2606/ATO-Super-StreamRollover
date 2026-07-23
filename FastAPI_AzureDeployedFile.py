from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

import os

from pyzeebe import ZeebeClient
from pyzeebe.channel.oauth_channel import create_camunda_cloud_channel


# =====================================================
# Load Environment Variables
# =====================================================

# Local development only (.env)
# Azure will use Application Settings
load_dotenv()


# =====================================================
# FastAPI Application
# =====================================================

app = FastAPI(
    title="ATO SuperStream Rollover API",
    description="API to start and monitor ATO SuperStream rollover process",
    version="1.0.0"
)


# =====================================================
# Enable CORS
# =====================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================================================
# Camunda Cloud Configuration
# =====================================================

CAMUNDA_CLIENT_ID = os.getenv("CAMUNDA_CLIENT_ID")
CAMUNDA_CLIENT_SECRET = os.getenv("CAMUNDA_CLIENT_SECRET")
CAMUNDA_CLUSTER_ID = os.getenv("CAMUNDA_CLUSTER_ID")
CAMUNDA_REGION = os.getenv("CAMUNDA_REGION")


zeebe_client = None


try:

    if all([
        CAMUNDA_CLIENT_ID,
        CAMUNDA_CLIENT_SECRET,
        CAMUNDA_CLUSTER_ID,
        CAMUNDA_REGION
    ]):

        channel = create_camunda_cloud_channel(

            client_id=CAMUNDA_CLIENT_ID,

            client_secret=CAMUNDA_CLIENT_SECRET,

            cluster_id=CAMUNDA_CLUSTER_ID,

            region=CAMUNDA_REGION

        )

        zeebe_client = ZeebeClient(channel)


except Exception as e:

    print(
        "Camunda connection failed:",
        str(e)
    )


# =====================================================
# Temporary Process Status Storage
# =====================================================

# For production replace with:
# Azure SQL / Cosmos DB / Redis

process_status = {}


# =====================================================
# Request Model
# =====================================================

class RolloverRequest(BaseModel):

    memberId: str

    memberName: str

    sourceFund: str

    destinationFund: str

    amount: float



# =====================================================
# Health Check
# =====================================================

@app.get("/")
async def health_check():

    return {

        "application":
            "ATO SuperStream Rollover API",

        "status":
            "RUNNING"

    }



# =====================================================
# Start Rollover Process
# =====================================================

@app.post("/rollover")
async def start_rollover(
        request: RolloverRequest
):


    if zeebe_client is None:

        raise HTTPException(

            status_code=500,

            detail="Camunda client not configured"

        )


    variables = {


        "memberId":
            request.memberId,


        "memberName":
            request.memberName,


        "sourceFund":
            request.sourceFund,


        "destinationFund":
            request.destinationFund,


        "amount":
            request.amount,


        "approvalStatus":
            "",


        "approvalComments":
            ""

    }


    try:


        process_instance = await zeebe_client.run_process(

            bpmn_process_id=
                "ato_superstream_rollover",

            variables=
                variables

        )


        process_key = str(

            process_instance.process_instance_key

        )


        process_status[process_key] = {


            "status":
                "RUNNING",


            "currentActivity":
                "Validate Member"

        }


        return {


            "status":
                "STARTED",


            "processInstanceKey":
                process_key

        }


    except Exception as e:


        raise HTTPException(

            status_code=500,

            detail=str(e)

        )



# =====================================================
# Update Process Status
# =====================================================

@app.post("/update-status/{process_key}")
async def update_status(

        process_key: str,

        activity: str,

        status: str = "RUNNING"

):


    process_status[process_key] = {


        "status":
            status,


        "currentActivity":
            activity

    }


    return {


        "message":
            "Status updated"

    }



# =====================================================
# Get Process Status
# =====================================================

@app.get("/status/{process_key}")
async def get_status(

        process_key: str

):


    status = process_status.get(

        process_key,

        {

            "status":
                "UNKNOWN",


            "currentActivity":
                "UNKNOWN"

        }

    )


    return {


        "processInstanceKey":
            process_key,


        "status":
            status["status"],


        "currentActivity":
            status["currentActivity"]

    }