import streamlit as st
import requests

from snowflake.snowpark.functions import col

st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie.")

name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()


my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe,
    max_selections=5
)



if ingredients_list:
    ingredients_string = ', '.join(ingredients_list)

    my_insert_stmt = f"""
        insert into smoothies.public.orders(ingredients, name_on_order, order_filled)
        values ('{ingredients_string}', '{name_on_order}', FALSE)
    """

    st.write(my_insert_stmt)

    # Removed st.stop() to allow the button and insertion code to execute
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")


# Call the SmoothieFroot API
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")

# Display the JSON response (optional)
# st.text(smoothiefroot_response.json())

# Display the data as a DataFrame in Streamlit
sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
