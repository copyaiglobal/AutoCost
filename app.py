import streamlit as st
import datetime
from supabase import create_client
import pandas as pd
import plotly.express as px
import resend

try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(url, key)
except Exception as e:
    st.error(f"Supabase connection failed. Please check your secrets configuration. Error: {e}")
    st.stop()

# --- 🎨 SƏHİFƏ AYARLARI VƏ DİZAYN ---
st.set_page_config(page_title="AutoCost - Cloud SaaS", page_icon="🚗", layout="centered")

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

# --- 📧 RESEND EMAIL GÖNDƏRMƏ FUNKSİYASI ---
resend.api_key = st.secrets["RESEND_API_KEY"]

def send_alert_email(user_email, doc_name, expiry_date):
    try:
        params = {
            "from": "AutoCost <onboarding@resend.dev>",
            "to": [user_email],
            "subject": f"⚠️ AutoCost Alert: Your {doc_name} is expiring soon!",
            "html": f"""
            <div style="font-family: Arial, sans-serif; color: #0f172a; padding: 20px;">
                <h2 style="color: #1e3a8a;">AutoCost Document Alert 🚗</h2>
                <p>Hello,</p>
                <p>This is an automated reminder from your vehicle diary.</p>
                <p>Your document <b>"{doc_name}"</b> is scheduled to expire on <b style="color: #dc2626;">{expiry_date}</b>.</p>
                <p>Please take action to renew it on time.</p>
                <br>
                <p>Best regards,<br><b>AutoCost Team 🚀</b></p>
            </div>
            """
        }
        resend.Emails.send(params)
        return True, None
    except Exception as e:
        return False, str(e)

# --- 🔐 SESSION STATE (İSTİFADƏÇİ GİRİŞİ) ---
if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    st.markdown("<h2 style='text-align: center; color: #1e3a8a;'>🚗 AutoCost Cloud SaaS</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #475569;'>Please sign in or create an account to manage your secure vehicle diary.</p>", unsafe_allow_html=True)
    
    auth_tab1, auth_tab2 = st.tabs(["🔑 Sign In", "📝 Register"])
    
    with auth_tab1:
        st.markdown("### Sign In to Your Account")
        login_email = st.text_input("Email Address", placeholder="name@example.com", key="login_email")
        login_password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Sign In ✨", key="login_btn"):
            try:
                res = supabase.auth.sign_in_with_password({"email": login_email, "password": login_password})
                st.session_state.user = res.user
                st.success("🎉 Successfully signed in!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Login failed: {e}")
                
    with auth_tab2:
        st.markdown("### Create New Account")
        reg_email = st.text_input("Email Address", placeholder="name@example.com", key="reg_email")
        reg_password = st.text_input("Password", type="password", key="reg_pass")
        
        if st.button("Register Account 🚀", key="reg_btn"):
            try:
                res = supabase.auth.sign_up({"email": reg_email, "password": reg_password})
                st.success("✅ Account created successfully! You can now sign in.")
            except Exception as e:
                st.error(f"❌ Registration failed: {e}")
                
        st.stop()

# --- 👑 ƏSAS TƏTBİQ ---
user_id = st.session_state.user.id
user_email = st.session_state.user.email

with st.sidebar:
    st.markdown(f"👤 Logged in as:\n{user_email}")
    st.write("---")
    if st.button("🚪 Sign Out", use_container_width=True):
        supabase.auth.sign_out()
        st.session_state.user = None
        st.rerun()

st.markdown("<h2>🚗 AutoCost — Car Expenses & Documents Diary</h2>", unsafe_allow_html=True)
st.markdown("<p style='color: #475569; font-size: 15px;'>Smart cloud financial vehicle diary. Track your fuel, repairs, and documents securely.</p>", unsafe_allow_html=True)
st.write("---")

tab1, tab2, tab3 = st.tabs(["💰 Add Expense", "🔍 Filter, Search & Analytics", "📜 Document Expiry Alerts"])

# --- TAB 1: XƏRC DAXİLMƏ ---
with tab1:
    st.markdown("### 💰 Log New Vehicle Expense")
    
    col1, col2 = st.columns(2)
    with col1:
        car_model = st.text_input("Vehicle Model / Brand:", placeholder="e.g., Toyota Prius", key="car_model_input")
        expense_type = st.selectbox("Expense Category:", ["Fuel ⛽", "Repair 🔧", "Maintenance 🛠️", "Insurance 📄", "Tax 💰", "Other 📌"], key="expense_type_input")

    with col2:
        expense_amount = st.number_input("Expense Amount ($):", min_value=0.0, step=1.0, key="expense_amount_input")
        
        c_col1, c_col2 = st.columns(2)
        with c_col1:
            currency = st.selectbox("Currency", ["USD", "EUR", "AZN"], key="expense_currency")
        with c_col2:
            if currency == "USD":
                default_rate = 1.0
            elif currency == "EUR":
                default_rate = 1.08
            else:
                default_rate = 0.59
            
            exchange_rate = st.number_input("Exchange Rate to USD", value=default_rate, format="%.2f", key="exchange_rate_input")

    expense_date = st.date_input("Transaction Date:", datetime.date.today(), key="expense_date_input")
    final_amount = expense_amount * exchange_rate

    fuel_liters = 0.0
    km_driven = 0.0

    if "Fuel" in expense_type:
        st.markdown("<div style='background-color: #eff6ff; padding: 15px; border-radius: 10px; border: 1px solid #bfdbfe; margin-top: 10px;'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: #1e40af !important; margin-bottom: 10px;'>⛽ Fuel Consumption Calculator Matrix</h4>", unsafe_allow_html=True)
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            fuel_liters = st.number_input("Fuel Liters (L):", min_value=0.0, value=0.0, step=0.5, key="exp_liters")
        with f_col2:
            km_driven = st.number_input("Kilometers Driven (km):", min_value=0.0, value=0.0, step=1.0, key="exp_km")
        st.markdown("</div>", unsafe_allow_html=True)

    st.write(" ")
    add_expense_btn = st.button("Add Expense to Cloud Log ✨", use_container_width=True)
    if add_expense_btn:
        if car_model.strip() == "" or expense_amount <= 0:
            st.error("⚠️ Please enter the vehicle model and ensure the amount is greater than 0!")
        else:
            cost_per_100km = 0.0
            if "Fuel" in expense_type and km_driven > 0:
                cost_per_100km = (expense_amount / km_driven) * 100
            
            try:
                supabase.table("expenses").insert({
                    "user_id": user_id,
                    "vehicle_model": car_model.strip(),
                    "expense_type": expense_type,
                    "amount": round(final_amount, 2),
                    "date": str(expense_date),
                    "fuel_liters": fuel_liters,
                    "km_driven": km_driven,
                    "cost_per_100km": round(cost_per_100km, 2)
                }).execute()
                st.session_state["filter_end"] = expense_date
                st.success("✅ Expense successfully logged to your cloud database!")
            except Exception as e:
                st.error(f"❌ Error saving expense: {e}")

# --- TAB 2: FILTER, SEARCH & ANALYTICS ---
with tab2:
    st.markdown("### 🔍 Filter, Search & Advanced Analytics Horizon")

    try:
        res = supabase.table("expenses").select("*").eq("user_id", user_id).execute()
        data = res.data
        
        if data:
            df = pd.DataFrame(data)
            
            df = df.rename(columns={
                "vehicle_model": "Vehicle Model",
                "expense_type": "Expense Category",
                "amount": "Amount ($)",
                "date": "Date",
                "fuel_liters": "Liters (L)",
                "km_driven": "Km Driven",
                "cost_per_100km": "Cost/100km ($)"
            })
            
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                categories = ["All Categories"] + list(df["Expense Category"].unique())
                selected_category = st.selectbox("Filter by Category", categories, key="filter_cat")
            with f_col2:
                model_query = st.text_input("Search by Vehicle Model:", placeholder="Type model name...", key="filter_model")
            
            df["Date"] = pd.to_datetime(df["Date"])
            min_date = df["Date"].min().date()
            max_date = df["Date"].max().date()
            
            if "filter_end" not in st.session_state:
                st.session_state["filter_end"] = max_date
            
            d_col1, d_col2 = st.columns(2)
            with d_col1:
                start_date = st.date_input("Start Date Horizon", min_date, key="filter_start")
            with d_col2:
                end_date = st.date_input("End Date Horizon", key="filter_end")
                
            filtered_df = df.copy()
            if selected_category != "All Categories":
                filtered_df = filtered_df[filtered_df["Expense Category"] == selected_category]
            if model_query.strip():
                filtered_df = filtered_df[filtered_df["Vehicle Model"].str.contains(model_query, case=False, na=False)]
            
            filtered_df = filtered_df[(filtered_df["Date"].dt.date >= start_date) & (filtered_df["Date"].dt.date <= end_date)]
            
            if not filtered_df.empty:
                total_cost = filtered_df["Amount ($)"].sum()
                total_km = filtered_df["Km Driven"].sum()
                total_liters = filtered_df["Liters (L)"].sum()
                
                m1, m2, m3 = st.columns(3)
                m1.metric("💰 Total Expenditure", f"${total_cost:,.2f}")
                m2.metric("🛣️ Total Distance", f"{total_km:,.1f} km")
                m3.metric("⛽ Total Fuel", f"{total_liters:,.1f} L")
                
                st.write("---")
                st.markdown("#### 📋 Current Vehicle Expenses Log Matrix (Cloud Database)")
                
                df_display = filtered_df.copy()
                df_display["Date"] = df_display["Date"].dt.strftime("%Y-%m-%d")
                df_display["Amount ($)"] = df_display["Amount ($)"].map(lambda x: f"{x:,.2f}")
                df_display["Cost/100km ($)"] = df_display["Cost/100km ($)"].map(lambda x: f"{x:,.2f}")
                df_display["Liters (L)"] = df_display["Liters (L)"].map(lambda x: f"{x:,.2f}")
                df_display["Km Driven"] = df_display["Km Driven"].map(lambda x: f"{x:,.2f}")
                
                st.table(df_display[['Vehicle Model', 'Expense Category', 'Amount ($)', 'Date', 'Liters (L)', 'Km Driven', 'Cost/100km ($)']])
                
                df_export = filtered_df[['Vehicle Model', 'Expense Category', 'Amount ($)', 'Date', 'Liters (L)', 'Km Driven', 'Cost/100km ($)']].copy()
                
                st.download_button(
                    label="📥 Download Filtered Expenses as CSV",
                    data=df_export.to_csv(index=False).encode("utf-8-sig"),
                    file_name="autocost_cloud_report.csv",
                    mime="text/csv",
                    use_container_width=True
                )

                st.write("---")
                st.markdown("#### 📊 Advanced Expense Analytics Horizon")
                g_col1, g_col2 = st.columns(2)
                with g_col1:
                    st.markdown("<p style='font-weight: bold; color: #1e3a8a;'>By Category ($)</p>", unsafe_allow_html=True)
                    st.bar_chart(filtered_df.groupby("Expense Category")["Amount ($)"].sum())
                with g_col2:
                    st.markdown("<p style='font-weight: bold; color: #1e3a8a;'>By Vehicle Model ($)</p>", unsafe_allow_html=True)
                    st.bar_chart(filtered_df.groupby("Vehicle Model")["Amount ($)"].sum())

                st.markdown("<p style='font-weight: bold; color: #1e3a8a; margin-top: 20px;'>Spending Timeline Trend</p>", unsafe_allow_html=True)
                
                timeline_df = filtered_df.groupby("Date")["Amount ($)"].sum().reset_index()
                timeline_df["Date"] = pd.to_datetime(timeline_df["Date"])
                timeline_df = timeline_df.sort_values("Date")
                timeline_df["Date_Str"] = timeline_df["Date"].dt.strftime("%b %d, %Y")
                
                fig = px.line(
                    timeline_df, 
                    x="Date_Str", 
                    y="Amount ($)", 
                    markers=True,
                    labels={"Amount ($)": "Amount ($)", "Date_Str": "Transaction Date"}
                )
                fig.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#1e3a8a", size=12),
                    xaxis=dict(showgrid=True, gridcolor="#e2e8f0"),
                    yaxis=dict(showgrid=True, gridcolor="#e2e8f0")
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("⚠️ No records found matching your filter criteria.")
        else:
            st.info("💡 No expenses registered in the cloud database yet.")
            
    except Exception as e:
        st.error(f"Error loading data: {e}")

# --- TAB 3: DOCUMENT EXPIRY ALERTS ---
with tab3:
    st.markdown("### 📜 Document & Expiry Alerts Matrix")
    
    with st.form("document_form", clear_on_submit=True):
        doc_col1, doc_col2 = st.columns(2)
        with doc_col1:
            doc_car_model = st.text_input("Vehicle Model for Document:", placeholder="e.g., Prius, BMW")
            doc_name = st.selectbox("Document Type:", ["Insurance 📜", "Technical Inspection 🔍", "Road Tax 🛣️", "Other 📄"])
        with doc_col2:
            doc_expiry_date = st.date_input("Document Expiry Date:", datetime.date.today() + datetime.timedelta(days=30))
            
            alert_days = st.number_input(
                "Alert Days Before Expiry:", 
                min_value=1, 
                max_value=90, 
                value=7,
                help="How many days in advance would you like to receive an email alert?"
            )
            
            add_doc_button = st.form_submit_button("Add Document Alert 🔔", use_container_width=True)

    if add_doc_button:
        if doc_car_model.strip() == "":
            st.error("⚠️ Please enter the vehicle model for the document!")
        else:
            try:
                supabase.table("vehicle_documents").insert({
                    "user_id": user_id,
                    "vehicle_model": doc_car_model.strip(),
                    "doc_name": doc_name,
                    "expiry_date": str(doc_expiry_date),
                    "alert_days": alert_days
                }).execute()
                st.success("✅ Document alert successfully added to cloud database!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error saving document: {e}")

    try:
        docs_res = supabase.table("vehicle_documents").select("*").eq("user_id", user_id).execute()
        docs_data = docs_res.data
    except Exception as e:
        st.error(f"Supabase detallı xəta: {e}")
        docs_data = []
    
    if docs_data:
        docs_df = pd.DataFrame(docs_data)
        docs_df = docs_df.rename(columns={
            "vehicle_model": "Vehicle Model",
            "doc_name": "Document Type",
            "expiry_date": "Expiry Date",
            "alert_days": "Alert Days"
        })
        
        st.write("---")
        st.markdown("#### Registered Documents & Status Horizon")
        today = datetime.date.today()
        
        status_list = []
        days_left_list = []
        expired_count = 0
        soon_count = 0
        
        for idx, row in docs_df.iterrows():
            exp_date = datetime.datetime.strptime(row['Expiry Date'], "%Y-%m-%d").date()
            days_left = (exp_date - today).days
            days_left_list.append(days_left)
            
            alert_threshold = row.get('Alert Days', 7)
            if pd.isna(alert_threshold):
                alert_threshold = 7
            else:
                alert_threshold = int(alert_threshold)

            if days_left < 0:
                status_list.append("🔴 Expired")
                expired_count += 1
            elif days_left <= alert_threshold:
                status_list.append(f"⚠️ Expiring Soon ({days_left} days left)")
                soon_count += 1
            else:
                status_list.append(f"🟢 Valid ({days_left} days left)")
                
        docs_display = docs_df.copy()
        docs_display['Status'] = status_list
        
        st.table(docs_display[['Vehicle Model', 'Document Type', 'Expiry Date', 'Alert Days', 'Status']])

        if expired_count > 0:
            st.error(f"🚨 Attention! You have {expired_count} expired document(s)!")
        if soon_count > 0:
            st.warning(f"⚠️ Warning! You have {soon_count} document(s) reaching their alert threshold.")
            
        st.write("---")
        
        if st.button("📧 Send Email Alerts for Due Documents", key="send_expiry_emails", use_container_width=True):
            sent_count = 0
            last_error = None
            
            for idx, row in docs_df.iterrows():
                exp_date = datetime.datetime.strptime(row['Expiry Date'], "%Y-%m-%d").date()
                days_left = (exp_date - today).days
                
                alert_threshold = row.get('Alert Days', 7)
                if pd.isna(alert_threshold):
                    alert_threshold = 7
                else:
                    alert_threshold = int(alert_threshold)
                
                if days_left <= alert_threshold:
                    doc_title = f"{row['Vehicle Model']} - {row['Document Type']}"
                    success, err_msg = send_alert_email(user_email, doc_title, str(exp_date))
                    if success:
                        sent_count += 1
                    else:
                        last_error = err_msg
            
            if sent_count > 0:
                st.success(f"✅ Successfully sent {sent_count} email alert(s) to {user_email}!")
            elif last_error:
                st.error(f"❌ Email sending failed. Error details: {last_error}")
            else:
                st.info("ℹ️ No documents require urgent email alerts at the moment.")
    else:
        st.info("💡 No documents registered yet.")