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
# Custom Header
# ==========================================================

st.markdown(
    """
    <h1 style='text-align:center;'>
    🔄 ATO SuperStream Digital Rollover Platform
    </h1>

    <p style='text-align:center; font-size:18px;'>
    Intelligent workflow orchestration using 
    Camunda + UiPath Automation
    </p>
    """,
    unsafe_allow_html=True
)


st.divider()



# ==========================================================
# Session State
# ==========================================================

defaults = {

    "process_key": None,

    "started": False,

    "current_step": 0,

    "status": "NOT STARTED"

}


for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value



# ==========================================================
# Workflow Steps
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
# Main Layout
# ==========================================================

col1, col2 = st.columns(
    [1,1]
)



# ==========================================================
# Input Form
# ==========================================================

with col1:


    st.subheader(
        "📄 Rollover Request"
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
            value=50000.00
        )


        submit = st.form_submit_button(
            "🚀 Start Rollover"
        )



        if submit:


            payload = {

                "memberId": member_id,

                "memberName": member_name,

                "sourceFund": source_fund,

                "destinationFund": destination_fund,

                "amount": amount

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
                    "Rollover Process Started Successfully"
                )


            except Exception as e:


                st.error(
                    f"API Error: {e}"
                )





# ==========================================================
# Status Dashboard
# ==========================================================


with col2:


    st.subheader(
        "📊 Live Process Monitoring"
    )


    if st.session_state.started:


        st.metric(

            "Process Instance",

            st.session_state.process_key

        )


        st.metric(

            "Current Status",

            st.session_state.status

        )


        st.divider()



        if st.button(
            "🔄 Refresh Status"
        ):


            if st.session_state.current_step < len(workflow_steps)-1:


                st.session_state.current_step += 1


                time.sleep(1)


            else:


                st.session_state.status = "COMPLETED"



        # Timeline


        for index, step in enumerate(workflow_steps):


            if index < st.session_state.current_step:


                st.success(

                    f"✅ {step['icon']} {step['name']}"

                )


            elif index == st.session_state.current_step:


                st.warning(

                    f"🟡 {step['icon']} {step['name']} - In Progress"

                )


            else:


                st.info(

                    f"⚪ {step['icon']} {step['name']}"

                )



        st.divider()


        if st.session_state.current_step == len(workflow_steps)-1:


            st.balloons()


            st.success(

                "🎉 Rollover Completed Successfully"

            )



    else:


        st.info(

            "Start a rollover request to monitor workflow"

        )





# ==========================================================
# Camunda Integration
# ==========================================================


st.divider()


st.subheader(
    "🔗 Enterprise Platforms"
)


c1, c2 = st.columns(2)


with c1:

    st.info(
        """
        **Workflow Engine**

        Camunda 8

        BPMN + DMN Decision Automation
        """
    )


with c2:

    st.info(
        """
        **Automation Engine**

        UiPath Robot

        End-to-End Transaction Processing
        """
    )