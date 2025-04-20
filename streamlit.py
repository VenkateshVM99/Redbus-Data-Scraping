import streamlit as st
import pandas as pd
import pymysql

# --- Database Connection ---
def get_connection():
    return  pymysql.connect(
            host="localhost",
            user="root",
            password="He007#W=Got765ked",  # Update with your database password
            database = "foundation" ,
            cursorclass=pymysql.cursors.DictCursor
        )

def get_city_options():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT from_city FROM Redbus")
    from_cities = sorted([row['from_city'] for row in cursor.fetchall()])

    cursor.execute("SELECT DISTINCT to_city FROM Redbus")
    to_cities = sorted([row['to_city'] for row in cursor.fetchall()])

    cursor.close()
    conn.close()
    return from_cities, to_cities

# --- Fetch Data with Filters ---
def get_filtered_data(filters):
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT from_city,to_city, route_link, busname, bustype, departing_time, duration, reaching_time, star_rating, price, seats_available FROM Redbus WHERE 1=1"
    params = []

    if filters['from_city']:
        query += " AND from_city = %s"
        params.append(filters['from_city'])
    if filters['to_city']:
        query += " AND to_city = %s"
        params.append(filters['to_city'])
    if filters['busname']:
        query += " AND busname = %s"
        params.append(filters['busname'])
    if filters['bustype']:
        query += " AND bustype LIKE %s"
        #params.append(filters['bustype'])
        params.append(f"%{filters['bustype']}%")
    if filters['min_price'] is not None:
        query += " AND price >= %s"
        params.append(filters['min_price'])
    if filters['max_price'] is not None:
        query += " AND price <= %s"
        params.append(filters['max_price'])
    if filters['rating'] is not None:
        query += " AND star_rating >= %s"
        params.append(filters['rating'])
    if filters['seats'] is not None:
        query += " AND seats_available >= %s"
        params.append(filters['seats'])

    cursor.execute(query, params)
    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return pd.DataFrame(data)

# --- Sidebar Filters ---
st.sidebar.header("🧭 Filter Buses")
from_cities, to_cities = get_city_options()

with st.sidebar.form("bus_filter_form"):
    from_city = st.selectbox("From City", [""] + from_cities)
    to_city = st.selectbox("To City", [""] + to_cities)
    busname = st.text_input("Bus Name")
    bustype = st.selectbox("Bus Type", ["", "A/C", "Non A/C", "Sleeper", "Seater"])
    min_price = st.number_input("Min Price", min_value=0, value=0)
    max_price = st.number_input("Max Price", min_value=0, value=10000)
    rating = st.number_input("Rating", min_value=0.0, max_value = 5.0 ,value=0.1)
    seats = st.number_input("No.of seats", min_value=0,max_value = 100, value=1)
    
    submit_button = st.form_submit_button(label="🔍 Search Buses")

# --- Main Content ---
st.title("🚌 Redbus")

if submit_button:
    filters = {
        "from_city": from_city,
        "to_city": to_city,
        "busname": busname,
        "bustype": bustype,
        "min_price": min_price,
        "max_price": max_price,
        "rating" : rating,
        "seats" : seats
    }

    df = get_filtered_data(filters)

    if not df.empty:
        st.dataframe(df)
    else:
        st.warning("No buses match your filters.")
else:
    st.info("Use the filters on the left and click 'Search Buses' to view results.")
