import streamlit as st
import pandas as pd
import datetime
import sqlite3

# --- 🗄️ MƏLUMAT BAZASI BAĞLANTISI (SQLite) ---
conn = sqlite3.connect('autocost.db', check_same_thread=False)
cursor = conn.cursor()

# Cədvəl mövcud deyilsə, avtomatik yaradırıq
cursor.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehicle_model TEXT,
        expense_type TEXT,
        amount REAL,
        date TEXT,
        fuel_liters REAL,
        km_driven REAL,
        cost_per_100km REAL
    )
''')
conn.commit()

# --- 🎨 AUTOCOST LÜKS AĞ REJİMİ VƏ PEŞƏKAR VİZUAL AYARLAR ---
st.set_page_config(page_title="AutoCost - Car Expenses Log", page_icon="🚗", layout="centered")

st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] { 
    background-color: #f8fafc !important; 
    color: #0f172a !important; 
}
h2, h3 { color: #1e3a8a !important; font-family: 'Helvetica Neue', sans-serif; font-weight: bold; }
h4 { color: #1e3a8a !important; font-weight: bold !important; margin-top: 15px !important; }

.stTextInput>div>div>input, .stSelectbox>div>div>div, .stNumberInput>div>div>input, .stDateInput>div>div>input {
    background-color: #ffffff !important;
    border: 2px solid #cbd5e1 !important;
    border-radius: 8px !important;
    color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
    font-size: 15px !important;
    font-weight: 600 !important;
}

::placeholder { color: #94a3b8 !important; opacity: 1 !important; -webkit-text-fill-color: #94a3b8 !important; }
input::placeholder { color: #94a3b8 !important; opacity: 1 !important; -webkit-text-fill-color: #94a3b8 !important; }

.stTextInput label, .stSelectbox label, .stNumberInput label, .stDateInput label {
    color: #334155 !important;
    font-size: 15px !important;
    font-weight: bold;
}

.stButton>button { 
    background-color: #2563eb !important; 
    color: white !important; 
    border-radius: 10px; 
    font-weight: bold; 
    border: none;
    padding: 12px;
    font-size: 16px;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
}
.stButton>button:hover { background-color: #1d4ed8 !important; }
</style>
""", unsafe_allow_html=True)

# --- 👑 BAŞLIQ PANƏLİ ---
st.markdown("<h2>🚗 AutoCost — Car Expenses Log</h2>", unsafe_allow_html=True)
st.markdown("<p style='color: #475569; font-size: 15px;'>Smart financial vehicle diary tailored for modern drivers. Track your fuel consumption, unexpected repairs, and insurance assets with detailed matrix analytics loops.</p>", unsafe_allow_html=True)
st.write("---")

# --- 📥 DRIVER INPUT FIELDS ---
col1, col2 = st.columns(2)

with col1:
    car_model = st.text_input("1. Vehicle Model / Brand:", placeholder="e.g., Prius, Mercedes, Hyundai")
    expense_type = st.selectbox("2. Expense Category:", ["Fuel ⛽", "Repair 🔧", "Insurance 📜", "Other 📦"])

with col2:
    expense_amount = st.number_input("3. Expense Amount ($):", min_value=0.0, value=0.0, step=1.0)
    expense_date = st.date_input("4. Transaction Date:", datetime.date.today())

# --- ⛽ DİNAMİK YANACAQ HESABLAYICI SAHƏLƏRİ ---
fuel_liters = 0.0
km_driven = 0.0

if "Fuel" in expense_type:
    st.markdown("<div style='background-color: #eff6ff; padding: 15px; border-radius: 10px; border: 1px solid #bfdbfe; margin-top: 10px;'>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: #1e40af !important; margin-bottom: 10px;'>⛽ Fuel Consumption Calculator Matrix</h4>", unsafe_allow_html=True)
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        fuel_liters = st.number_input("Fuel Liters (L):", min_value=0.0, value=0.0, step=0.5)
    with f_col2:
        km_driven = st.number_input("Kilometers Driven (km):", min_value=0.0, value=0.0, step=1.0)
    st.markdown("</div>", unsafe_allow_html=True)

st.write(" ")
add_button = st.button("Add Expense to Log ✨", use_container_width=True)
st.write("---")
if add_button:
    if car_model.strip() == "" or expense_amount <= 0:
        st.error("⚠️ Please enter the vehicle model and ensure the amount is greater than 0!")
    else:
        cost_per_100km = 0.0
        liters_per_100km = 0.0
        if "Fuel" in expense_type and km_driven > 0:
            cost_per_100km = (expense_amount / km_driven) * 100
            if fuel_liters > 0:
                liters_per_100km = (fuel_liters / km_driven) * 100
        
        cursor.execute('''
            INSERT INTO expenses (vehicle_model, expense_type, amount, date, fuel_liters, km_driven, cost_per_100km)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (car_model.strip(), expense_type, expense_amount, str(expense_date), fuel_liters, km_driven, round(cost_per_100km, 2)))
        conn.commit()
        
        if "Fuel" in expense_type and km_driven > 0:
            st.success(f"✅ Fuel logged to database! 100 km-ə sərfiyyat: {cost_per_100km:.2f} $ ({liters_per_100km:.2f} L / 100km)")
        else:
            st.success("✅ Expense successfully logged to your database diary!")

# --- 📊 BAZADAN MƏLUMATLARIN OXUNMASI ---
df = pd.read_sql_query("""
    SELECT vehicle_model AS 'Vehicle Model', 
           expense_type AS 'Expense Category', 
           amount AS 'Amount ($)', 
           date AS 'Date', 
           fuel_liters AS 'Liters (L)', 
           km_driven AS 'Km Driven', 
           cost_per_100km AS 'Cost/100km ($)' 
    FROM expenses
""", conn)

if not df.empty:
    st.write("### 🔍 Filter & Search Horizon")
    f_col1, f_col2 = st.columns(2)
    
    with f_col1:
        # Kateqoriya filtri
        categories = ["All Categories"] + list(df["Expense Category"].unique())
        selected_category = st.selectbox("Filter by Category:", categories)
        
    with f_col2:
        # Model üzrə axtarış
        search_query = st.text_input("Search by Vehicle Model:", placeholder="Type model name...")

    # Filtrləmə məntiqi
    filtered_df = df.copy()
    if selected_category != "All Categories":
        filtered_df = filtered_df[filtered_df["Expense Category"] == selected_category]
        
    if search_query.strip() != "":
        filtered_df = filtered_df[filtered_df["Vehicle Model"].str.contains(search_query, case=False, na=False)]

    st.write("---")
    
    if not filtered_df.empty:
        total_cost = filtered_df["Amount ($)"].sum()
        chart_data = filtered_df.groupby("Expense Category")["Amount ($)"].sum()
        
        st.write("### 📋 Current Vehicle Expenses Log Matrix (SQLite Database)")
        df_display = filtered_df.copy()
        
        df_display["Amount ($)"] = df_display["Amount ($)"].map("{:,.2f}".format)
        df_display["Cost/100km ($)"] = df_display["Cost/100km ($)"].map("{:,.2f}".format)
        df_display["Liters (L)"] = df_display["Liters (L)"].map("{:,.2f}".format)
        df_display["Km Driven"] = df_display["Km Driven"].map("{:,.2f}".format)
                
        st.table(df_display)
        
        st.markdown(f"<h4 style='color: #2563eb !important;'>💰 Total Cumulative Vehicle Expenditure (Filtered): {total_cost:,.2f} $</h4>", unsafe_allow_html=True)
        
        @st.cache_data
        def convert_df_to_csv(dataframe):
            return dataframe.to_csv(index=False).encode("utf-8")

        csv_data = convert_df_to_csv(filtered_df)
        
        st.download_button(
            label="📥 Filtrlənmiş Xərcləri Excel / CSV olaraq yüklə",
            data=csv_data,
            file_name="autocost_filtrlənmiş_hesabat.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        st.write("---")
        st.write("### 📊 Expense Distribution Analytics Horizon")
        st.bar_chart(chart_data)
    else:
        st.warning("⚠️ No records found matching your filter or search criteria.")
else:
    st.info("💡 No expenses registered in the database yet. Input your core parameters above to initialize track logs.")