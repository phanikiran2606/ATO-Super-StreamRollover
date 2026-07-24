import streamlit as st
import requests
import time


# ==========================================================
# Configuration
# ==========================================================

FASTAPI_URL = (
    "https://atosuperstreamrollover-exceg8h8d5d5hcae."
    "australiaeast-01.azurewebsites.net"
)


# ==========================================================
# Page Configuration
# ==========================================================

st.set_page_config(
    page_title="ATO SuperStream Digital Rollover",
    page_icon="🔄",
    layout="wide"
)



# ==========================================================
# Header
# ==========================================================

st.markdown(
    """
    <h1 style="text-align:center;">
    🔄 ATO SuperStream Digital Rollover Platform
    </h1>

    <p style="text-align:center;font-size:18px;">
    Intelligent Workflow Automation using Camunda 8 + UiPath
    </p>
    """,
    unsafe_allow_html=True
)


st.divider()



# ==========================================================
# Session State
# ==========================================================

session_defaults = {

    "process_key": None,

    "started": False,

    "current_step": 0,

    "status": "NOT STARTED"

}


for key, value in session_defaults.items():

    if key not in st.session_state:

        st.session_state[key] = value



# ==========================================================
# Workflow Definition
# ==========================================================

workflow_steps = [

    {
        "name": "Rollover Request Received",
        "icon": "📥"
    },

    {
        "name": "Validate Member Details",
        "icon": "👤"
    },

    {
        "name": "Eligibility Check",
        "icon": "✅"
    },

    {
        "name": "Operations Approval",
        "icon": "👨‍💼"
    },

    {
        "name": "Execute UiPath Robot",
        "icon": "🤖"
    },

    {
        "name": "Rollover Completed",
        "icon": "🎉"
    }

]



# ==========================================================
# Layout
# ==========================================================

left, right = st.columns(
    [1, 1]
)



# ==========================================================
# Rollover Request Form
# ==========================================================

with left:


    st.subheader(
        "📄 Rollover Request Details"
    )


    with st.form(
        "rollover_form"
    ):


        member_id = st.text_input(
            "Member ID",
            "1234567890"
        )


        member_name = st.text_input(
            "Member Name",
            "John Doe"
        )


        source_fund = st.text_input(
            "Source Fund",
            "Fund A"
        )


        destination_fund = st.text_input(
            "Destination Fund",
            "Fund B"
        )


        amount = st.number_input(
            "Rollover Amount",
            min_value=0.0,
            value=50000.00
        )


        submit = st.form_submit_button(
            "🚀 Start Rollover"
        )



        if submit:


            payload = {


                "memberId":
                    member_id,


                "memberName":
                    member_name,


                "sourceFund":
                    source_fund,


                "destinationFund":
                    destination_fund,


                "amount":
                    amount

            }



            try:


                response = requests.post(

                    f"{FASTAPI_URL}/rollover",

                    json=payload,

                    timeout=30

                )


                response.raise_for_status()


                result = response.json()



                st.session_state.process_key = (

                    result["processInstanceKey"]

                )


                st.session_state.started = True


                st.session_state.current_step = 0


                st.session_state.status = "RUNNING"



                st.success(
                    "✅ Rollover Process Started"
                )



            except Exception as e:


                st.error(
                    f"API Error: {e}"
                )





# ==========================================================
# Process Monitoring Dashboard
# ==========================================================

with right:


    st.subheader(
        "📊 Live Process Monitoring"
    )


    if st.session_state.started:



        st.metric(

            "Process Instance ID",

            st.session_state.process_key

        )



        st.metric(

            "Process Status",

            st.session_state.status

        )



        st.divider()



        # Refresh Button


        if st.button(
            "🔄 Refresh Status"
        ):


            if (
                st.session_state.current_step
                <
                len(workflow_steps)-1
            ):


                st.session_state.current_step += 1


                time.sleep(1)



            if (
                st.session_state.current_step
                ==
                len(workflow_steps)-1
            ):


                st.session_state.status = "COMPLETED"



        # ==================================================
        # Workflow Timeline
        # ==================================================


        st.subheader(
            "Workflow Timeline"
        )



        for index, step in enumerate(workflow_steps):


            # Completed previous steps

            if index < st.session_state.current_step:


                st.success(

                    f"✅ {step['icon']} {step['name']}"

                )



            # Final completed state

            elif (

                index == len(workflow_steps)-1

                and

                st.session_state.current_step == index

            ):


                st.success(

                    f"🎉 {step['name']} Successfully Completed"

                )



            # Current running step

            elif index == st.session_state.current_step:


                st.warning(

                    f"🟡 {step['icon']} {step['name']} - In Progress"

                )



            # Pending steps

            else:


                st.info(

                    f"⚪ {step['icon']} {step['name']}"

                )



        st.divider()



        if st.session_state.status == "COMPLETED":


            st.balloons()


            st.success(

                "🎉 Rollover Completed Successfully"

            )



    else:


        st.info(

            "Submit a rollover request to start monitoring"

        )




# ==========================================================
# Architecture Footer
# ==========================================================

st.divider()


st.subheader(
    "🏗️ Solution Architecture"
)


col1, col2, col3 = st.columns(3)



with col1:

    st.info(
        """
        🔹 Camunda 8

        BPMN Workflow

        DMN Decision Engine
        """
    )



with col2:

    st.info(
        """
        🔹 UiPath

        Robotic Process Automation

        Transaction Execution
        """
    )



with col3:

    st.info(
        """
        🔹 Azure

        FastAPI

        Cloud Hosting
        """
    )