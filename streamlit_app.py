import streamlit as st
from snowflake.snowpark.session import Session
import requests

# Set page title and description
st.title("👑 Customize Your Smoothie! 👑")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input for smoothie name
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Load Snowflake connection from secrets
connection_parameters = st.secrets["snowflake"]

try:
    session = Session.builder.configs(connection_parameters).create()
except Exception as e:
    st.error("Failed to connect to Snowflake: " + str(e))
    st.stop()

# Fetch available fruits from Snowflake
try:
    my_dataframe = session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS").select("FRUIT_NAME").to_pandas()
except Exception as e:
    st.error("Failed to fetch fruit options: " + str(e))
    st.stop()

# Multi-select for ingredients
ingredients_list = st.multiselect('Choose up to 5 ingredients:', my_dataframe['FRUIT_NAME'], max_selections=5)

if ingredients_list:
    ingredients_string = ', '.join(ingredients_list)

    for fruit_chosen in ingredients_list:
        st.subheader(f"{fruit_chosen} Nutrition Information")
        try:
            smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{fruit_chosen.lower()}")
            if smoothiefroot_response.status_code == 200:
                sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
            else:
                st.error(f"No data available for {fruit_chosen}.")
        except Exception as e:
            st.error(f"Failed to fetch nutrition data for {fruit_chosen}: {str(e)}")

    submit_order = st.button("Submit Order")

    if submit_order:
        try:
            session.sql(f"INSERT INTO SMOOTHIES.PUBLIC.ORDERS (INGREDIENTS, NAME_ON_ORDER) VALUES ('{ingredients_string}', '{name_on_order}')").collect()
            st.success("Your Smoothie is ordered! 🎉")
        except Exception as e:
            st.error("Failed to submit order: " + str(e))
else:
    st.write("Please select ingredients for your smoothie.")
