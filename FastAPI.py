from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

import os

from pyzeebe import ZeebeClient
from pyzeebe.channel.oauth_channel import create_camunda_cloud_channel


# ---------------------------------------
# Load Environment
# ---------------------------------------

load_dotenv()


# ---------------------------------------
# FastAPI App
# ---------------------------------------

app = FastAPI(
    title="ATO SuperStream Rollover API",
    version="1.0.0"
)


# ---------------------------------------
# Camunda Connection
# ---------------------------------------

channel = create_camunda_cloud_channel(

    client_id=os.getenv("CAMUNDA_CLIENT_ID"),

    client_secret=os.getenv("CAMUNDA_CLIENT_SECRET"),

    cluster_id=os.getenv("CAMUNDA_CLUSTER_ID"),

    region=os.getenv("CAMUNDA_REGION")

)


zeebe_client = ZeebeClient(channel)



# ---------------------------------------
# Temporary Process Status
# ---------------------------------------

process_status = {}



# ---------------------------------------
# Request Model
# ---------------------------------------

class RolloverRequest(BaseModel):

    memberId: str

    memberName: str

    sourceFund: str

    destinationFund: str

    amount: float




# ---------------------------------------
# Start Rollover
# ---------------------------------------

@app.post("/rollover")
async def start_rollover(
    request: RolloverRequest
):


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



    process_instance = await zeebe_client.run_process(

        bpmn_process_id="ato_superstream_rollover",

        variables=variables

    )



    process_key = str(

        process_instance.process_instance_key

    )



    # Initial status

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





# ---------------------------------------
# Update Process Status
# Called later by workers
# ---------------------------------------

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





# ---------------------------------------
# Get Process Status
# Streamlit calls this
# ---------------------------------------

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