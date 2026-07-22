import asyncio
import os
import uuid

from dotenv import load_dotenv

from pyzeebe import ZeebeWorker
from pyzeebe.channel.oauth_channel import create_camunda_cloud_channel


load_dotenv()



async def main():


    print("Starting UiPath Worker...")



    # ---------------------------------------
    # Camunda Connection
    # ---------------------------------------

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



    print("Connected to Camunda")



    worker = ZeebeWorker(channel)





    # ---------------------------------------
    # UiPath Worker
    # ---------------------------------------

    @worker.task(
        task_type="execute-uipath"
    )

    async def execute_uipath(

        memberId=None,

        memberName=None,

        sourceFund=None,

        destinationFund=None,

        amount=None

    ):


        print("\n==============================")
        print("UiPath Job Received")
        print("==============================")


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



        try:


            print()

            print(
                "Starting UiPath Robot..."
            )



            # --------------------------------
            # Replace this with real UiPath
            # Orchestrator API call later
            # --------------------------------

            await asyncio.sleep(5)



            robot_execution_id = (

                "SIM-"

                +

                str(uuid.uuid4())

            )



            print(
                "UiPath Robot Completed"
            )



            return {


                "robotStatus":

                    "SUCCESS",



                "robotExecutionId":

                    robot_execution_id,



                "robotErrorMessage":

                    "",



                "currentActivity":

                    "Completed",

                 "processStatus":
                 
                    "COMPLETED"

            }





        except Exception as e:


            print(
                "UiPath Failed:",
                str(e)
            )



            return {


                "robotStatus":

                    "FAILED",



                "robotExecutionId":

                    "",



                "robotErrorMessage":

                    str(e),



                "currentActivity":

                    "Execute UiPath Robot Failed"

            }





    print("==============================")
    print("Listening for execute-uipath jobs...")
    print("==============================")



    try:

        await worker.work()


    except asyncio.CancelledError:

        print(
            "Worker cancelled gracefully"
        )





if __name__ == "__main__":


    try:


        asyncio.run(main())


    except KeyboardInterrupt:


        print(
            "\nUiPath Worker stopped by user"
        )


    except asyncio.CancelledError:


        print(
            "\nUiPath Worker cancelled"
        )