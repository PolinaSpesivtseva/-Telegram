from .config import check_auth_url
import requests
import streamlit as st

st.set_option('client.showErrorDetails', True)

def get_all_cookies():
    """
    WARNING: This uses unsupported feature of Streamlit
    Returns the cookies as a dictionary of kv pairs
    """
    from streamlit.web.server.websocket_headers import _get_websocket_headers
    from urllib.parse import unquote

    headers = _get_websocket_headers()
    if headers is None:
        return {}

    if "Cookie" not in headers:
        return {}

    cookie_string = headers["Cookie"]
    cookie_kv_pairs = cookie_string.split(";")

    cookie_dict = {}
    for kv in cookie_kv_pairs:
        k_and_v = kv.split("=")
        k = k_and_v[0].strip()
        v = k_and_v[1].strip()
        cookie_dict[k] = unquote(
            v
        )    
    return cookie_dict

def check_auth():
    cookies = get_all_cookies()
    response = requests.get(check_auth_url, cookies=cookies)
    response = response.json()
    if response["detail"] == "authenticated":
        return True
    else:
        return False

def authentication_middleware():
    try:
        authenticated = check_auth()
    except Exception as e:
        authenticated = False

    return authenticated
