import streamlit as st
import requests
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
from snowflake.snowpark import Session

st.title("👑 Customize Your Smoothie! 👑")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

try:
    session = get_active_session()
except:
    connection_parameters = {
        "account": "<your_account>",
        "user": "<your_user>",
        "password": "<your_password>",
        "warehouse": "<your_warehouse>",
        "database": "<your_database>",
        "schema": "<your_schema>"
    }
    session = Session.builder.configs(connection_parameters).create()

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
ingredients_list = st.multiselect('Choose up to 5 ingredients:', my_dataframe.to_pandas(), max_selections=5)

if ingredients_list:
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        st.subheader(fruit_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{fruit_chosen}")
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
        ingredients_string += fruit_chosen + ' '

    my_insert_stmt = f"insert into smoothies.public.orders(ingredients, name_on_order) values ('{ingredients_string.strip()}', '{name_on_order}')"
    if st.button('Submit Order'):
        try:
            session.sql(my_insert_stmt).collect()
            st.success('Your Smoothie is ordered!', icon="✅")
        except Exception as e:
            st.error(f"An error occurred: {e}")

session.close()
