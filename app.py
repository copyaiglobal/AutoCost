import streamlit as st
import pandas as pd
import datetime

# --- 🎨 AUTOCOST LÜKS GECƏ REJİMİ VƏ PEŞƏKAR VİZUAL AYARLAR ---
st.set_page_config(page_title="AutoCost - Car Expenses Log", page_icon="🚗", layout="centered")

st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] { 
    background-color: #0f172a !important; 
    color: #ffffff !important; 
}

h2, h3 { color: #3b82f6 !important; font-family: 'Helvetica Neue', sans-serif; font-weight: bold; }

/* 🌟 XANALARIN DAXİLİ VƏ İSTİFADƏÇİ YAZISI TAM QAPQARA OLUŞUR */
.stTextInput>div>div>input, .stSelectbox>div>div>div, .stNumberInput>div>div>input, .stDateInput>div>div>input {
    background-color: #ffffff !important;
    border: 2px solid #cbd5e1 !important;
    border-radius: 8px !important;
    color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
    font-size: 15px !important;
    font-weight: 600 !important;
}

/* 🌟 DÜNƏNKİ O SEHRBAZLIQ: ARXA FONDAKI İPUCU SÖZLƏRİ TAM YUMŞAQ AÇIQ BOZ OLUŞUR 🎉 */
::placeholder { color: #cbd5e1 !important; opacity: 1 !important; -webkit-text-fill-color: #cbd5e1 !important; }
input::placeholder { color: #cbd5e1 !important; opacity: 1 !important; -webkit-text-fill-color: #cbd5e1 !important; }
.stTextInput>div>div>input::placeholder { color: #cbd5e1 !important; -webkit-text-fill-color: #cbd5e1 !important; }

.stTextInput label, .stSelectbox label, .stNumberInput label, .stDateInput label {
    color: #ffffff !important;
    font-size: 16px !important;
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
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.4);
}
.stButton>button:hover { background-color: #1d4ed8 !important; }

.report-section {
    background-color: #ffffff !important; 
    padding: 25px; 
    border-radius: 12px; 
    color: #0f172a !important; 
    margin-bottom: 20px;
    border-left: 6px solid #2563eb;
}
</style>
""", unsafe_allow_html=True)

# --- 👑 BAŞLIQ PANƏLİ ---
st.markdown("<h2>🚗 AutoCost — Car Expenses Log</h2>", unsafe_allow_html=True)
st.markdown("<p style='color: #94a3b8; font-size: 15px;'>Smart financial vehicle diary tailored for modern drivers. Track your fuel consumption, unexpected repairs, and insurance assets with detailed matrix analytics loops.</p>", unsafe_allow_html=True)
st.write("---")
# --- 📥 SÜRÜCÜ GİRİŞ XANALARI ---
# --- 📥 DRIVER INPUT FIELDS ---
col1, col2 = st.columns(2)

with col1:
    car_model = st.text_input("1. Vehicle Model / Brand:", placeholder="e.g., Prius, Mercedes, Hyundai")
    expense_type = st.selectbox("2. Expense Category:", ["Fuel ⛽", "Repair 🔧", "Insurance 📜", "Other 📦"])

with col2:
    expense_amount = st.number_input("3. Expense Amount ($):", min_value=0.0, value=0.0, step=1.0)
    expense_date = st.date_input("4. Transaction Date:", datetime.date.today())

st.write(" ")
add_button = st.button("Add Expense to Log ✨", use_container_width=True)
st.write("---")
# Xərcləri siyahıya əlavə etmək üçün lüks mavi düyməmiz
add_button = st.button("Xərci Jurnala Əlavə Et ✨", use_container_width=True)
st.write("---")
# --- 💾 DAXİLİ YADDAŞ (SESSION STATE) SİSTEMİ ---
# --- 💾 INTERNAL SESSION STORAGE ---
if "expenses_list" not in st.session_state:
    st.session_state["expenses_list"] = []

if add_button:
    if car_model.strip() == "" or expense_amount <= 0:
        st.error("⚠️ Please enter the vehicle model and ensure the amount is greater than 0!")
    else:
        new_data = {
            "Vehicle Model": car_model.strip(),
            "Expense Category": expense_type,
            "Amount ($)": expense_amount,
            "Date": expense_date.strftime("%Y-%m-%d")
        }
        st.session_state["expenses_list"].append(new_data)
        st.success("✅ Expense successfully logged to your diary!")

# --- 📊 LIVE EXPENSE TRACKING MATRIX ---
if st.session_state["expenses_list"]:
    st.write("### 📋 Current Vehicle Expenses Log Matrix")
    df = pd.DataFrame(st.session_state["expenses_list"])
    st.table(df)
    
    total_cost = df["Amount ($)"].sum()
    st.markdown(f"<h4 style='color: #2563eb !important;'>💰 Total Cumulative Vehicle Expenditure: {total_cost:,.2f} $</h4>", unsafe_allow_html=True)
else:
    st.info("💡 No expenses registered yet. Input your core parameters above to initialize track logs.")
# --- 🍕 SEHRBBAZ VİZUAL QRAFİK MATRIX (SƏNİN İSTƏDİYİN HƏMİN O LÜKS ELEMENT! 🎉) ---
    st.write("---")
    st.write("### 📊 Expense Distribution Analytics Horizon")
    
    # Kateqoriyalara görə məbləğləri qruplaşdırıb bəbə dili ilə dairəvi qrafikə ötürürük
    chart_data = df.groupby("Expense Category")["Amount ($)"].sum()
    
    # Dünyanın ən asan və ən lüks canlı qrafik düyməsi!
    st.pie_chart(chart_data)