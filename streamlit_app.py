import streamlit as st
import requests
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(":crown: Customize Your Smoothie! :crown:")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

session = get_active_session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe,
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        st.subheader(fruit_chosen + " Nutrition Information")
        try:
            smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{fruit_chosen}")
            if smoothiefroot_response.status_code == 200:
                sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
            else:
                st.error("No data found for " + fruit_chosen)
        except Exception as e:
            st.error(f"Error retrieving data for {fruit_chosen}: {e}")

    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        my_insert_stmt = f"""INSERT INTO smoothies.public.orders (ingredients, name_on_order)
                           VALUES ('{ingredients_string.strip()}', '{name_on_order}')"""
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
else:
    st.info("Select ingredients to see nutrition information.")
