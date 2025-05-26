import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from function import generate_barcode_image, render_qz_image_html
import base64
from io import BytesIO

# Load the config.yaml file
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Initialize the authenticator
authenticator = stauth.Authenticate(config['credentials'],
                                    config['cookie']['name'],
                                    config['cookie']['key'],
                                    config['cookie']['expiry_days'])

# Sidebar navigation
page = st.sidebar.selectbox(
    "Navigate", ["Login", "Register", "Forgot Password", "Forgot Username"])

# ---------------- LOGIN PAGE ----------------
if page == "Login":
    authenticator.login('main')
    if st.session_state["authentication_status"]:
        authenticator.logout('Logout', 'main')
        st.write(f'Welcome *{st.session_state["name"]}*')

        st.title('Tracking Number Printer')

        @st.cache_data
        def load_data(filename):
            if filename.name.endswith(('.xlsx', '.xls')):
                return pd.read_excel(filename, header=1)
            return None

        uploaded_file = st.file_uploader("Choose a file")
        if uploaded_file:
            data = load_data(uploaded_file)
            if data is not None:
                customer_code = st.text_input('Enter Customer Code', '')
                if customer_code:
                    matchup_code = data[data['原条码'] == customer_code]['新条码']
                    matchup_des = data[data['原条码'] == customer_code]['标注']

                    if not matchup_code.empty:
                        tracking_number = matchup_code.iloc[0]
                        description = matchup_des.iloc[0]
                        st.success(f"新条形码: {tracking_number}")
                        st.success(f"标注: {description}")

                        barcode_img_buffer = generate_barcode_image(
                            tracking_number, description)
                        if barcode_img_buffer:
                            base64_img = base64.b64encode(
                                barcode_img_buffer.getvalue()).decode()
                            render_qz_image_html(base64_img)
                    else:
                        st.error('No tracking number found')
            else:
                st.error("Please upload a valid Excel file.")
    elif st.session_state["authentication_status"] is False:
        st.error('Username/password is incorrect')
    elif st.session_state["authentication_status"] is None:
        st.warning('Please enter your credentials')

# ---------------- REGISTER PAGE ----------------
elif page == "Register":
    st.subheader("Register New User")
    try:
        email, username, name = authenticator.register_user(
            pre_authorized=False)
        if email:
            st.success('User registered successfully')
    except Exception as e:
        st.error(e)

# ---------------- FORGOT PASSWORD PAGE ----------------
elif page == "Forgot Password":
    st.subheader("Reset Your Password")
    try:
        username, email, new_password = authenticator.forgot_password()
        if username:
            st.success('New password to be sent securely')
        elif username is False:
            st.error('Username not found')
    except Exception as e:
        st.error(e)

# ---------------- FORGOT USERNAME PAGE ----------------
elif page == "Forgot Username":
    st.subheader("Recover Username")
    try:
        username, email = authenticator.forgot_username()
        if username:
            st.success('Username to be sent securely')
        elif username is False:
            st.error('Email not found')
    except Exception as e:
        st.error(e)

# ---------------- SAVE UPDATED CONFIG ----------------
with open('config.yaml', 'w') as file:
    yaml.dump(config, file, default_flow_style=False)
