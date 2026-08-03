import streamlit as st
import pandas as pd
import datetime


# --- 🎨 AUTOCOST LÜKS AĞ REJİMİ VƏ PEŞƏKAR VİZUAL AYARLAR ---
st.set_page_config(page_title="AutoCost - Car Expenses Log", page_icon="🚗", layout="centered")

st.markdown("""
<style>
/* FONY TAMAMİLƏ AĞAPPAQ LÜKS EDİRİK */
html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] { 
    background-color: #f8fafc !important; 
    color: #0f172a !important; 
}

h2, h3 { color: #1e3a8a !important; font-family: 'Helvetica Neue', sans-serif; font-weight: bold; }
h4 { color: #1e3a8a !important; font-weight: bold !important; margin-top: 15px !important; }

/* XANALARIN DAXİLİ VƏ YAZISI TAM SƏLİQƏLİ OLUŞUR */
.stTextInput>div>div>input, .stSelectbox>div>div>div, .stNumberInput>div>div>input, .stDateInput>div>div>input {
    background-color: #ffffff !important;
    border: 2px solid #cbd5e1 !important;
    border-radius: 8px !important;
    color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
    font-size: 15px !important;
    font-weight: 600 !important;
}

/* Zərif və yumşaq açıq boz ipucu (placeholder) rəngləri */
::placeholder { color: #94a3b8 !important; opacity: 1 !important; -webkit-text-fill-color: #94a3b8 !important; }
input::placeholder { color: #94a3b8 !important; opacity: 1 !important; -webkit-text-fill-color: #94a3b8 !important; }

/* Xanaların yuxarıdakı ad yazıları tam tünd lüks boz olur */
.stTextInput label, .stSelectbox label, .stNumberInput label, .stDateInput label {
    color: #334155 !important;
    font-size: 15px !important;
    font-weight: bold;
}

/* Lüks Göy Düyməmiz */
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

/* Cari jurnal cədvəlinin peşəkar ağ blok nizamı */
.report-section {
    background-color: #ffffff !important; 
    padding: 25px; 
    border-radius: 12px; 
    color: #0f172a !important; 
    margin-bottom: 20px;
    border-left: 6px solid #2563eb;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
}
</style>
""", unsafe_allow_html=True)

# --- 👑 BAŞLIQ PANƏLİ ---
st.markdown("<h2>🚗 AutoCost — Car Expenses Log</h2>", unsafe_allow_html=True)
st.markdown("<p style='color: #475569; font-size: 15px;'>Smart financial vehicle diary tailored for modern drivers. Track your fuel consumption, unexpected repairs, and insurance assets with detailed matrix analytics loops.</p>", unsafe_allow_html=True)
st.write("---")
# --- 📥 DRIVER INPUT FIELDS (İNDİ DƏYİŞƏNLƏR PEŞƏKARCA TƏYİN EDİLDİ 🎉) ---
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

# --- 📊 LIVE EXPENSE TRACKING MATRIX (CƏDVƏL BİRİNCİ, QRAFİK SONRA 🎉) ---
if st.session_state["expenses_list"]:
    # 1. İlk öncə xalis riyazi cədvəli arxa fonda qururuq
    df = pd.DataFrame(st.session_state["expenses_list"])
    
    # 2. Toplam xərci rəqəmlərlə hesablayırıq
    total_cost = df["Amount ($)"].sum()
    
    # 3. Qrafik üçün lazımi təmiz datanı bura kopyalayırıq (Cədvəl mətnə çevrilmədən öncə)
    chart_data = df.groupby("Expense Category")["Amount ($)"].sum()
    
    # 4. 🌟 CƏDVƏL ARTIQ BİRİNCİ ÇIXIR VƏ ARXASINDAKI 4 SIFIR SİLİNİR 🎉 🌟
    st.write("### 📋 Current Vehicle Expenses Log Matrix")
    df["Amount ($)"] = df["Amount ($)"].map("{:,.2f}".format)
    st.table(df)
    
    st.markdown(f"<h4 style='color: #2563eb !important;'>💰 Total Cumulative Vehicle Expenditure: {total_cost:,.2f} $</h4>", unsafe_allow_html=True)
    
    # 5. 🌟 QRAFİK TAM PEŞƏKAR YERİNƏ — CƏDVƏLİN ALTINA OTURDU 🎉 🌟
    st.write("---")
    st.write("### 📊 Expense Distribution Analytics Horizon")
    st.bar_chart(chart_data)
else:
    st.info("💡 No expenses registered yet. Input your core parameters above to initialize track logs.")
# --- 🍕 SEHRBBAZ VİZUAL QRAFİK MATRIX (SƏNİN İSTƏDİYİN HƏMİN O LÜKS ELEMENT! 🎉) ---
    # --- 🍕 SEHRBBAZ VİZUAL QRAFİK MATRIX (SƏNİN İSTƏDİYİN HƏMİN O LÜKS ELEMENT! 🎉) ---
    st.write("---")
    st.write("### 📊 Expense Distribution Analytics Horizon")
    
    