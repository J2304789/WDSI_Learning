from typing import Text
import streamlit as st

def app():
    st.sidebar.subheader('Login Section')
    with st.sidebar.form(key='my_form'):
        username = st.text_input('Username')
        password = st.text_input('Password', type='password')
        submit_button = st.form_submit_button(label='Login')

    if username == 'moxu':
        st.succes('luck')
    if __name__ == '__app__':
        app()