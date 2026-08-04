import streamlit as st
import pandas as pd
import datetime
import sqlite3

# --- 🗄️ MƏLUMAT BAZASI BAĞLANTISI (SQLite) ---
conn = sqlite3.connect('autocost.db', check_same_thread=False)
cursor = conn.cursor()

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

cursor.execute('''
    CREATE TABLE IF NOT EXISTS vehicle_documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehicle_model TEXT,
        doc_name TEXT,
        expiry_date TEXT
    )
''')
conn.commit()

# --- 🎨 AUTOCOST LÜKS AĞ REJİMİ VƏ PEŞƏKAR VİZUAL AYARLAR ---
st.set_page_config(page_title="AutoCost - Car Expenses & Documents Log", page_icon="🚗", layout="centered")

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

.stButton>button, div.stFormSubmitButton>button { 
    background-color: #2563eb !important; 
    color: white !important; 
    border-radius: 10px; 
    font-weight: bold; 
    border: none;
    padding: 12px;
    font-size: 16px;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    width: 100%;
}
.stButton>button:hover, div.stFormSubmitButton>button:hover { background-color: #1d4ed8 !important; }
</style>
""", unsafe_allow_html=True)

# --- 👑 BAŞLIQ PANƏLİ ---
st.markdown("<h2>🚗 AutoCost — Car Expenses & Documents Diary</h2>", unsafe_allow_html=True)
st.markdown("<p style='color: #475569; font-size: 15px;'>Smart financial vehicle diary tailored for modern drivers. Track your fuel consumption, unexpected repairs, insurance assets, and critical document expiration alerts.</p>", unsafe_allow_html=True)
st.write("---")

# --- 🗂️ 3 AYRI TAB (PƏNCƏRƏ) ---
tab1, tab2, tab3 = st.tabs(["💰 Add Expense", "🔍 Filter, Search & Analytics", "📜 Document Expiry Alerts"])

# --- TAB 1: XƏRC DAXİLMƏ ---
with tab1:
    st.markdown("### 💰 Log New Vehicle Expense")
    st.markdown("<p style='color: #475569; font-size: 14px;'>Fill out the core parameters below to record a new fuel, repair, or maintenance expense.</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)

    with col1:
        car_model = st.text_input("Vehicle Model / Brand:", placeholder="e.g., Prius, Mercedes, Hyundai")
        expense_type = st.selectbox("Expense Category:", ["Fuel ⛽", "Repair 🔧", "Insurance 📜", "Other 📦"])

    with col2:
        expense_amount = st.number_input("Expense Amount ($):", min_value=0.0, value=0.0, step=1.0)
        expense_date = st.date_input("Transaction Date:", datetime.date.today())

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
                st.success(f"✅ Fuel logged to database! Cost per 100km: {cost_per_100km:.2f} $ ({liters_per_100km:.2f} L / 100km)")
            else:
                st.success("✅ Expense successfully logged to your database diary!")

# --- TAB 2: FİLTR, AXTARIŞ, TARİX ARALIĞI VƏ GENİŞLƏNDİRİLMİŞ ANALİTİKA ---
with tab2:
    st.markdown("### 🔍 Filter, Search & Advanced Analytics Horizon")
    st.markdown("<p style='color: #475569; font-size: 14px;'>Filter records, select custom date ranges, explore key metrics, and analyze spending patterns.</p>", unsafe_allow_html=True)

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
        f_col1, f_col2 = st.columns(2)
        
        with f_col1:
            categories = ["All Categories"] + list(df["Expense Category"].unique())
            selected_category = st.selectbox("Filter by Category:", categories)
            
        with f_col2:
            search_query = st.text_input("Search by Vehicle Model:", placeholder="Type model name...")

        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
        d_col1, d_col2 = st.columns(2)
        
        df['parsed_date'] = pd.to_datetime(df['Date']).dt.date
        min_d = df['parsed_date'].min()
        max_d = df['parsed_date'].max()

        with d_col1:
            start_date = st.date_input("Start Date Horizon:", value=min_d, min_value=min_d, max_value=max_d)
        with d_col2:
            end_date = st.date_input("End Date Horizon:", value=max_d, min_value=min_d, max_value=max_d)

        filtered_df = df.copy()
        
        if selected_category != "All Categories":
            filtered_df = filtered_df[filtered_df["Expense Category"] == selected_category]
        if search_query.strip() != "":
            filtered_df = filtered_df[filtered_df["Vehicle Model"].str.contains(search_query, case=False, na=False)]
            
        filtered_df = filtered_df[(filtered_df['parsed_date'] >= start_date) & (filtered_df['parsed_date'] <= end_date)]
        filtered_df = filtered_df.drop(columns=['parsed_date'])

        st.write("---")
        
        if not filtered_df.empty:
            total_cost = filtered_df["Amount ($)"].sum()
            total_km = filtered_df["Km Driven"].sum()
            total_liters = filtered_df["Liters (L)"].sum()
            
            m1, m2, m3 = st.columns(3)
            m1.metric("💰 Total Expenditure", f"${total_cost:,.2f}")
            m2.metric("🛣️ Total Distance", f"{total_km:,.1f} km")
            m3.metric("⛽ Total Fuel", f"{total_liters:,.1f} L")
            
            st.write("---")
            st.markdown("#### 📋 Current Vehicle Expenses Log Matrix (SQLite Database)")
            df_display = filtered_df.copy()
            
            df_display["Amount ($)"] = df_display["Amount ($)"].map(lambda x: f"{x:,.2f}")
            df_display["Cost/100km ($)"] = df_display["Cost/100km ($)"].map(lambda x: f"{x:,.2f}")
            df_display["Liters (L)"] = df_display["Liters (L)"].map(lambda x: f"{x:,.2f}")
            df_display["Km Driven"] = df_display["Km Driven"].map(lambda x: f"{x:,.2f}")
                    
            st.table(df_display)
            
            st.download_button(
                label="📥 Download Filtered Expenses as Excel / CSV",
                data=filtered_df.to_csv(index=False).encode("utf-8-sig"),
                file_name="autocost_filtered_report.csv",
                mime="text/csv",
                use_container_width=True
            )
            
            st.write("---")
            st.markdown("#### 📊 Advanced Expense Analytics Horizon")
            
            g_col1, g_col2 = st.columns(2)
            
            with g_col1:
                st.markdown("<p style='font-weight: bold; color: #1e3a8a;'>By Category ($)</p>", unsafe_allow_html=True)
                category_chart = filtered_df.groupby("Expense Category")["Amount ($)"].sum()
                st.bar_chart(category_chart)
                
            with g_col2:
                st.markdown("<p style='font-weight: bold; color: #1e3a8a;'>By Vehicle Model ($)</p>", unsafe_allow_html=True)
                model_chart = filtered_df.groupby("Vehicle Model")["Amount ($)"].sum()
                st.bar_chart(model_chart)

            st.markdown("<p style='font-weight: bold; color: #1e3a8a; margin-top: 20px;'>Spending Timeline Trend</p>", unsafe_allow_html=True)
            timeline_chart = filtered_df.groupby("Date")["Amount ($)"].sum()
            st.line_chart(timeline_chart)

        else:
            st.warning("⚠️ No records found matching your filter, search or date range criteria.")
    else:
        st.info("💡 No expenses registered in the database yet. Add your first expense using the 'Add Expense' tab.")

# --- TAB 3: SƏNƏDLƏR VƏ XƏBƏRDARLIQLAR (FORM İLƏ TƏKMİLLƏŞDİRİLDİ) ---
with tab3:
    st.markdown("### 📜 Document & Expiry Alerts Matrix")
    st.markdown("<p style='color: #475569; font-size: 14px;'>Track your vehicle insurance, technical inspections, and critical document expiry dates with automated alerts.</p>", unsafe_allow_html=True)

    # st.form istifadə edərək təkrar kliklərin və dublikatların qarşısı alınır
    with st.form("document_form", clear_on_submit=True):
        doc_col1, doc_col2 = st.columns(2)
        with doc_col1:
            doc_car_model = st.text_input("Vehicle Model for Document:", placeholder="e.g., Prius, BMW")
            doc_name = st.selectbox("Document Type:", ["Insurance 📜", "Technical Inspection 🔍", "Road Tax 🛣️", "Other 📄"])
        with doc_col2:
            doc_expiry_date = st.date_input("Document Expiry Date:", datetime.date.today() + datetime.timedelta(days=30))
            st.write("") 
            st.write("")
            add_doc_button = st.form_submit_button("Add Document Alert 🔔", use_container_width=True)

    if add_doc_button:
        if doc_car_model.strip() == "":
            st.error("⚠️ Please enter the vehicle model for the document!")
        else:
            cursor.execute('''
                INSERT INTO vehicle_documents (vehicle_model, doc_name, expiry_date)
                VALUES (?, ?, ?)
            ''', (doc_car_model.strip(), doc_name, str(doc_expiry_date)))
            conn.commit()
            st.success("✅ Document alert successfully added to database!")
            st.rerun()

    docs_df = pd.read_sql_query("""
        SELECT id, vehicle_model AS 'Vehicle Model', 
               doc_name AS 'Document Type', 
               expiry_date AS 'Expiry Date' 
        FROM vehicle_documents
    """, conn)

    days_left_list = []

    if not docs_df.empty:
        st.write("---")
        st.markdown("#### Registered Documents & Status Horizon")
        today = datetime.date.today()
        
        status_list = []
        for idx, row in docs_df.iterrows():
            exp_date = datetime.datetime.strptime(row['Expiry Date'], "%Y-%m-%d").date()
            days_left = (exp_date - today).days
            days_left_list.append(days_left)
            if days_left < 0:
                status_list.append("🔴 Expired")
            elif days_left <= 30:
                status_list.append(f"⚠️ Expiring Soon ({days_left} days left)")
            else:
                status_list.append(f"🟢 Valid ({days_left} days left)")
                
        docs_display = docs_df.copy()
        docs_display['Status'] = status_list
        
        st.table(docs_display[['Vehicle Model', 'Document Type', 'Expiry Date', 'Status']])

    expired_count = sum(1 for d in days_left_list if d < 0)
    soon_count = sum(1 for d in days_left_list if 0 <= d <= 30)

    if expired_count > 0:
        st.error(f"🚨 Attention! You have {expired_count} expired document(s)! Please renew them immediately.")
    if soon_count > 0:
        st.warning(f"⚠️ Warning! You have {soon_count} document(s) expiring within the next 30 days.")