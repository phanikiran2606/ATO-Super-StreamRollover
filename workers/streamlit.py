import streamlit as st
import requests


st.set_page_config(
    page_title="ATO SuperStream Rollover",
    layout="centered"
)


st.title("ATO SuperStream Rollover Request")


memberId = st.text_input(
    "Member ID",
    "M001"
)


memberName = st.text_input(
    "Member Name",
    "John Smith"
)


sourceFund = st.text_input(
    "Source Fund",
    "FundA"
)


destinationFund = st.text_input(
    "Destination Fund",
    "FundB"
)


amount = st.number_input(
    "Amount",
    value=50000.0
)



if st.button("Submit Rollover"):


    payload = {

        "memberId": memberId,

        "memberName": memberName,

        "sourceFund": sourceFund,

        "destinationFund": destinationFund,

        "amount": amount

    }


    try:


        response = requests.post(

            "http://127.0.0.1:8000/rollover",

            json=payload

        )


        if response.status_code == 200:


            st.success(
                "Rollover process started"
            )


            st.json(
                response.json()
            )


        else:


            st.error(
                response.text
            )



    except Exception as e:


        st.error(
            str(e)
        )