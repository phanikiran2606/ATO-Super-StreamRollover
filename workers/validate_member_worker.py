import asyncio
import os
import requests

from dotenv import load_dotenv
from pyzeebe import ZeebeWorker, create_camunda_cloud_channel


load_dotenv()



# ------------------------------------------------
# Camunda Token
# ------------------------------------------------

def get_camunda_token():

    response = requests.post(

        "https://login.cloud.camunda.io/oauth/token",

        data={

            "grant_type": "client_credentials",

            "audience": "zeebe.camunda.io",

            "client_id": os.getenv(
                "CAMUNDA_CLIENT_ID"
            ),

            "client_secret": os.getenv(
                "CAMUNDA_CLIENT_SECRET"
            )

        },

        headers={

            "Content-Type":
                "application/x-www-form-urlencoded"

        }

    )


    response.raise_for_status()

    return response.json()["access_token"]





# ------------------------------------------------
# DMN Evaluation
# ------------------------------------------------

async def evaluate_eligibility(

        memberStatus,

        fundValid,

        amount

):


    endpoint = os.getenv(
        "CAMUNDA_REST_URL"
    )


    url = (

        f"{endpoint}"
        f"/decision-definitions/evaluation"

    )


    payload = {


        "decisionDefinitionId":

            os.getenv(
                "ELIGIBILITY_DECISION_ID"
            ),


        "variables": {


            "memberStatus":

                memberStatus,


            "fundValid":

                fundValid,


            "amount":

                amount

        }

    }



    token = get_camunda_token()



    response = requests.post(

        url,

        json=payload,

        headers={

            "Authorization":

                f"Bearer {token}",


            "Content-Type":

                "application/json"

        }

    )



    print("\n==============================")
    print("DMN RESPONSE")
    print("==============================")

    print(
        "Status:",
        response.status_code
    )

    print(
        response.text
    )



    response.raise_for_status()



    return response.json()






# ------------------------------------------------
# Worker
# ------------------------------------------------

async def main():


    print(
        "Starting Validate Member Worker..."
    )



    channel = create_camunda_cloud_channel(


        client_id=os.getenv(
            "CAMUNDA_CLIENT_ID"
        ),


        client_secret=os.getenv(
            "CAMUNDA_CLIENT_SECRET"
        ),


        cluster_id=os.getenv(
            "CAMUNDA_CLUSTER_ID"
        ),


        region=os.getenv(
            "CAMUNDA_REGION"
        )

    )



    print(
        "Connected to Camunda"
    )



    worker = ZeebeWorker(channel)





    @worker.task(

        task_type="validate-member"

    )

    async def validate_member(


        memberId,

        memberName,

        sourceFund,

        destinationFund,

        amount


    ):


        print("\n================================")
        print("Validate Member Job")
        print("================================")



        print(
            "Member ID        :",
            memberId
        )


        print(
            "Member Name      :",
            memberName
        )


        print(
            "Source Fund      :",
            sourceFund
        )


        print(
            "Destination Fund :",
            destinationFund
        )


        print(
            "Amount           :",
            amount
        )




        # --------------------------------
        # Member Validation
        # --------------------------------


        memberValidated = bool(
            memberId
        )



        if memberValidated:

            memberStatus = "ACTIVE"

        else:

            memberStatus = "INACTIVE"





        # --------------------------------
        # Fund Validation
        # --------------------------------


        fundValid = bool(

            sourceFund

            and

            destinationFund

        )



        print()

        print(
            "Member Status:",
            memberStatus
        )


        print(
            "Fund Valid:",
            fundValid
        )





        # --------------------------------
        # DMN Eligibility
        # --------------------------------


        dmn_response = await evaluate_eligibility(

            memberStatus,

            fundValid,

            amount

        )




        eligibility = (

            dmn_response

            .get(

                "output",

                "false"

            )

            .lower()

            == "true"

        )



        print()

        print(
            "Eligibility:",
            eligibility
        )





        # --------------------------------
        # Return BPMN Variables
        # --------------------------------


        return {


            "memberValidated":

                memberValidated,



            "validationStatus":

                "SUCCESS"

                if memberValidated and fundValid

                else "FAILED",



            "memberStatus":

                memberStatus,



            "fundValid":

                fundValid,



            "eligibility":

                eligibility,



            "eligibilityStatus":

                "ELIGIBLE"

                if eligibility

                else "NOT_ELIGIBLE",



            "currentActivity":

                "Operations Approval",



            "memberId":

                memberId,



            "memberName":

                memberName,



            "sourceFund":

                sourceFund,



            "destinationFund":

                destinationFund,



            "amount":

                amount,



            "approver":

                "operations.user"

        }





    print("==============================")
    print("validate-member worker started")
    print("==============================")


    await worker.work()






if __name__ == "__main__":

    asyncio.run(main())