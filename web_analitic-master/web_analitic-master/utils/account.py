from utils.config import DEBUG

import streamlit as st

# st.set_option('client.showErrorDetails', False)
def page_account():
    def nav_to(url):
        nav_script = """
            <meta http-equiv="refresh" content="0; url='%s'">
        """ % (
            url
        )
        st.write(nav_script, unsafe_allow_html=True)
    nav_path = "http://localhost:8002/accounts/email" if DEBUG else "/accounts/email"
    nav_to(nav_path)
