import streamlit as st
import pandas as pd
import datetime

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

# --- 💾 DAXİLİ YADDAŞ (SESSION STATE) SİSTEMİ ---
if "expenses_list" not in st.session_state:
    st.session_state["expenses_list"] = []

# --- 📥 DRIVER INPUT FIELDS ---
col1, col2 = st.columns(2)

with col1:
    car_model = st.text_input("1. Vehicle Model / Brand:", placeholder="e.g., Prius, Mercedes, Hyundai")
    expense_type = st.selectbox("2. Expense Category:", ["Fuel ⛽", "Repair 🔧", "Insurance 📜", "Other 📦"])

with col2:
    expense_amount = st.number_input("3. Expense Amount ($):", min_value=0.0, value=0.0, step=1.0)
    expense_date = st.date_input("4. Transaction Date:", datetime.date.today())

# --- ⛽ DİNAMİK YANACAQ HESABLAYICI SAHƏLƏRİ (Dəyişənlər əvvəlcədən 0 təyin olunur) ---
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
        new_data = {
            "Vehicle Model": car_model.strip(),
            "Expense Category": expense_type,
            "Amount ($)": expense_amount,
            "Date": str(expense_date),
            "Liters (L)": fuel_liters if "Fuel" in expense_type else 0.0,
            "Km Driven": km_driven if "Fuel" in expense_type else 0.0,
            "Cost/100km ($)": round(cost_per_100km, 2) if "Fuel" in expense_type else 0.0
        }
        st.session_state["expenses_list"].append(new_data)
        
        if "Fuel" in expense_type and km_driven > 0:
            st.success(f"✅ Fuel logged! 100 km-ə sərfiyyat: {cost_per_100km:.2f} $ ({liters_per_100km:.2f} L / 100km)")
        else:
            st.success("✅ Expense successfully logged to your diary!")
        st.rerun()

# --- 📊 LIVE EXPENSE TRACKING MATRIX ---
if st.session_state["expenses_list"]:
    df = pd.DataFrame(st.session_state["expenses_list"])
    total_cost = df["Amount ($)"].sum()
    chart_data = df.groupby("Expense Category")["Amount ($)"].sum()
    
    st.write("### 📋 Current Vehicle Expenses Log Matrix")
    df_display = df.copy()
    df_display["Amount ($)"] = df_display["Amount ($)"].map("{:,.2f}".format)
    st.table(df_display)
    
    st.markdown(f"<h4 style='color: #2563eb !important;'>💰 Total Cumulative Vehicle Expenditure: {total_cost:,.2f} $</h4>", unsafe_allow_html=True)
    
    st.write("---")
    st.write("### 📊 Expense Distribution Analytics Horizon")
    st.bar_chart(chart_data)
else:
    st.info("💡 No expenses registered yet. Input your core parameters above to initialize track logs.")