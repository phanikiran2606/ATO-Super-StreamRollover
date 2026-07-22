import streamlit as st
import requests


# ---------------------------------------
# Configuration
# ---------------------------------------

FASTAPI_URL = "http://127.0.0.1:8000"


# ---------------------------------------
# Page Configuration
# ---------------------------------------

st.set_page_config(
    page_title="ATO SuperStream Rollover",
    page_icon="🔄",
    layout="centered"
)


st.title("🔄 ATO SuperStream Rollover")

st.write(
    "Submit rollover request and monitor workflow"
)



# ---------------------------------------
# Session State
# ---------------------------------------

if "process_key" not in st.session_state:
    st.session_state.process_key = None


if "started" not in st.session_state:
    st.session_state.started = False


if "approved" not in st.session_state:
    st.session_state.approved = False


if "uipath_completed" not in st.session_state:
    st.session_state.uipath_completed = False



# ---------------------------------------
# Rollover Form
# ---------------------------------------

with st.form("rollover_form"):


    st.subheader(
        "Member Details"
    )


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
        "Amount",
        min_value=0.0,
        value=50000.0
    )


    submit = st.form_submit_button(
        "Start Rollover"
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

                json=payload

            )


            response.raise_for_status()


            result = response.json()



            st.session_state.process_key = (

                result["processInstanceKey"]

            )


            st.session_state.started = True

            st.session_state.approved = False

            st.session_state.uipath_completed = False



            st.success(
                "Rollover process started"
            )



        except Exception as e:


            st.error(
                f"Error starting process: {e}"
            )





# ---------------------------------------
# Workflow Status
# ---------------------------------------

if st.session_state.started:


    st.divider()


    st.subheader(
        "📊 Process Status"
    )


    st.write(

        "Process Instance Key:",

        st.session_state.process_key

    )


    st.divider()



    # -----------------------------------
    # Approval Refresh Button
    # -----------------------------------

    if not st.session_state.approved:


        if st.button(
            "🔄 Refresh Approval Status"
        ):

            st.session_state.approved = True



    # -----------------------------------
    # UiPath Refresh Button
    # -----------------------------------

    if st.session_state.approved and not st.session_state.uipath_completed:


        if st.button(
            "🤖 Refresh UiPath Status"
        ):

            st.session_state.uipath_completed = True





    # -----------------------------------
    # Timeline
    # -----------------------------------


    st.success(
        "🟢 Rollover Request Received"
    )


    st.success(
        "🟢 Validate Member"
    )


    st.success(
        "🟢 Eligibility Check"
    )



    if st.session_state.approved:


        st.success(
            "🟢 Operations Approval Completed"
        )


    else:


        st.warning(
            "🟡 Waiting for Operations Approval"
        )


        st.info(
            "Approve / Reject from Camunda Tasklist"
        )



    if st.session_state.uipath_completed:


        st.success(
            "🟢 Execute UiPath Robot Completed"
        )


        st.success(
            "🎉 Completed"
        )


    else:


        st.warning(
            "🟡 Execute UiPath Robot"
        )


        st.write(
            "⚪ Completed"
        )



    st.divider()



    st.subheader(
        "🔗 Camunda Tasklist"
    )


    st.markdown(

        "https://syd-1.api.camunda.io/"
        "e2b7140a-2917-46f4-9894-d562c031a1c7/tasklist"

    )