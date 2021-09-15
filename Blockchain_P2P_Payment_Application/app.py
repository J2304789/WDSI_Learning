import streamlit as st
st.set_page_config(page_title='Loft Customer Analytics Tool', layout='wide', initial_sidebar_state='auto')
import datetime


# Custom imports 
from multiapp import MultiPage
from pages import home, login, signup

# Create an instance of the app 
app = MultiPage()


# Title of the main page
st.title("P2P Payment app")
#st.header("")
st.markdown('---')

custom_green = 'rgb(124, 230, 110)'
custom_red = 'rgb(230, 134, 110)'
custom_blue = 'rgb(110, 186, 230)'
custom_orange = 'rgb(230, 172, 110)'

# Add all your applications (pages) here
app.add_page("Home", home.app)
app.add_page("Login", login.app)
app.add_page("Sign Up", signup.app)

# The main app
app.run()