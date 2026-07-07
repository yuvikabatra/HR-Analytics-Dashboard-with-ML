import json
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import joblib
import os

# -------------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------------

st.set_page_config(
    page_title="HR Analytics & Attrition Prediction",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------
# CUSTOM CSS
# -------------------------------------------------------

st.markdown("""
<style>

.main{
    background-color:#0B1727;
}

.block-container{
    padding-top:1rem;
    padding-bottom:1rem;
}

h1,h2,h3,h4,h5{
    color:white;
}

section[data-testid="stSidebar"]{
    background:#10233F;
}

div[data-testid="metric-container"]{
    background:#163A63;
    border-radius:15px;
    padding:15px;
    border:1px solid #295D93;
}

</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------
# LOAD DATA
# -------------------------------------------------------

@st.cache_data
def load_data():
    return pd.read_excel("HR Data.xlsx")

df = load_data()

# -------------------------------------------------------
# LOAD MODEL
# -------------------------------------------------------

@st.cache_resource
def load_model():

    if os.path.exists("rf_pipeline_fixed.pkl"):
        return joblib.load("rf_pipeline_fixed.pkl")

    if os.path.exists("rf_pipeline.pkl"):
        return joblib.load("rf_pipeline.pkl")

    return None


USER_FILE = os.path.join(os.getcwd(), "users.json")

DEFAULT_USERS = {
    "admin": "admin123",
    "hr": "hrpass"
}


def load_users():
    if os.path.exists(USER_FILE):
        try:
            with open(USER_FILE, "r", encoding="utf-8") as f:
                users = json.load(f)
            if isinstance(users, dict):
                return users
        except Exception:
            pass
    return DEFAULT_USERS.copy()


def save_users(users):
    try:
        with open(USER_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2)
    except Exception:
        pass


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.login_error = ""
    st.session_state.signup_error = ""
    st.session_state.signup_success = ""
    st.session_state.page = "🔒 Login"
    st.session_state.selected_page_widget = "🔒 Login"
    st.session_state.next_page = None


USERS = load_users()


model = load_model()


def is_leave_prediction(pred):
    if isinstance(pred, str):
        return pred.strip().lower() == "yes"
    try:
        return int(pred) == 1
    except Exception:
        return False


def get_leave_probability(model, X):
    proba = model.predict_proba(X)
    classes = getattr(model, "classes_", None)
    if classes is not None:
        classes = list(classes)
        if 1 in classes:
            idx = classes.index(1)
        elif "Yes" in classes:
            idx = classes.index("Yes")
        elif "yes" in classes:
            idx = classes.index("yes")
        else:
            idx = 1 if proba.shape[1] > 1 else 0
    else:
        idx = 1 if proba.shape[1] > 1 else 0
    return proba[0, idx]


model = load_model()

# -------------------------------------------------------
# SIDEBAR
# -------------------------------------------------------

st.sidebar.title("🏢 HR Analytics")

if st.session_state.next_page:
    st.session_state.selected_page_widget = st.session_state.next_page
    st.session_state.page = st.session_state.next_page
    st.session_state.next_page = None

if st.session_state.logged_in:
    page_options = ["🏠 Dashboard", "🔮 Single Prediction", "📁 Batch Prediction", "🚪 Logout"]
    if st.session_state.page not in page_options:
        st.session_state.page = "🏠 Dashboard"
else:
    page_options = ["🔒 Login", "📝 Sign Up"]
    if st.session_state.page not in page_options:
        st.session_state.page = "🔒 Login"

page = st.sidebar.radio(
    "Navigation",
    page_options,
    key="selected_page_widget"
)

st.session_state.page = page

st.sidebar.markdown("---")

if st.session_state.logged_in and page not in ["🔒 Login", "📝 Sign Up"]:
    st.sidebar.markdown(f"**Signed in as:** {st.session_state.username}")

if not st.session_state.logged_in and page == "🔒 Login":
    st.title("🔒 Login")
    st.markdown("Please sign in to access the HR analytics dashboard.")

    with st.form("login_form"):
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        submitted = st.form_submit_button("Login")

    if submitted:
        if username in USERS and USERS[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.login_error = ""
            st.session_state.signup_success = ""
            # Defer changing the widget-backed selection to avoid mutating
            # widget-backed keys after widget creation. Set next_page and
            # allow the normal widget flow to pick it up on the next run.
            st.session_state.next_page = "🏠 Dashboard"
            st.success("Login successful")
        else:
            st.session_state.login_error = "Invalid username or password"
            st.session_state.signup_success = ""

    if st.session_state.login_error:
        st.error(st.session_state.login_error)

    if st.session_state.signup_success:
        st.success(st.session_state.signup_success)

    st.stop()

if not st.session_state.logged_in and page == "📝 Sign Up":
    st.title("📝 Sign Up")
    st.markdown("Create an account to access the HR analytics dashboard.")

    with st.form("signup_form"):
        new_username = st.text_input("Choose a username", key="signup_username")
        new_password = st.text_input("Choose a password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm password", type="password", key="signup_confirm_password")
        submitted = st.form_submit_button("Create account")

    if submitted:
        st.session_state.signup_error = ""
        st.session_state.signup_success = ""

        if not new_username or not new_password or not confirm_password:
            st.session_state.signup_error = "Please complete all fields."
        elif new_username in USERS:
            st.session_state.signup_error = "Username already exists. Please choose another."
        elif new_password != confirm_password:
            st.session_state.signup_error = "Passwords do not match."
        elif len(new_password) < 4:
            st.session_state.signup_error = "Password must be at least 4 characters."
        else:
            USERS[new_username] = new_password
            save_users(USERS)
            st.session_state.signup_success = "Account created successfully. Please login."
            # Defer widget selection change to `next_page` to avoid mutating
            # widget-backed session keys after widget creation.
            st.session_state.next_page = "🔒 Login"
            st.success(st.session_state.signup_success)
            

    if st.session_state.signup_error:
        st.error(st.session_state.signup_error)

    if st.session_state.signup_success:
        st.success(st.session_state.signup_success)

    st.stop()

if st.session_state.logged_in and page == "🚪 Logout":
    st.session_state.logged_in = False
    st.session_state.username = ""
    # Only set next_page; the sidebar widget will be updated at the top
    # of the script when `next_page` is observed.
    st.session_state.next_page = "🔒 Login"
    st.success("Logged out")

department_filter = st.sidebar.multiselect(
    "Department",
    sorted(df["Department"].unique()),
    default=sorted(df["Department"].unique())
)

gender_filter = st.sidebar.multiselect(
    "Gender",
    sorted(df["Gender"].unique()),
    default=sorted(df["Gender"].unique())
)

education_filter = st.sidebar.multiselect(
    "Education Field",
    sorted(df["Education Field"].unique()),
    default=sorted(df["Education Field"].unique())
)

filtered_df = df[
    (df["Department"].isin(department_filter))
    &
    (df["Gender"].isin(gender_filter))
    &
    (df["Education Field"].isin(education_filter))
]

# ==========================================================
# DASHBOARD
# ==========================================================

if page == "🏠 Dashboard":

    st.title("🏢 HR Analytics Dashboard")
    if st.session_state.logged_in:
        st.markdown(f"### Welcome, {st.session_state.username}!")

    st.markdown("---")

    total_employee = len(filtered_df)

    attrition_count = len(
        filtered_df[
            filtered_df["Attrition"]=="Yes"
        ]
    )

    active_employee = total_employee-attrition_count

    attrition_rate = round(
        attrition_count/total_employee*100,
        2
    )

    avg_age = round(filtered_df["Age"].mean(),1)

    c1,c2,c3,c4,c5 = st.columns(5)

    with c1:
        st.metric(
            "Employee Count",
            total_employee
        )

    with c2:
        st.metric(
            "Attrition Count",
            attrition_count
        )

    with c3:
        st.metric(
            "Attrition Rate",
            f"{attrition_rate}%"
        )

    with c4:
        st.metric(
            "Active Employees",
            active_employee
        )

    with c5:
        st.metric(
            "Average Age",
            avg_age
        )

    st.markdown("---")
    # ==========================================================
    # ROW 1
    # ==========================================================

    col1, col2 = st.columns(2)

    # --------------------------------------------------
    # Department Wise Attrition
    # --------------------------------------------------

    with col1:

        dept = (
            filtered_df[filtered_df["Attrition"]=="Yes"]
            .groupby("Department")
            .size()
            .reset_index(name="Count")
        )

        fig = px.pie(
            dept,
            names="Department",
            values="Count",
            hole=0.45,
            title="Department Wise Attrition"
        )

        fig.update_layout(
            template="plotly_dark",
            height=420
        )

        st.plotly_chart(fig,use_container_width=True)


    # --------------------------------------------------
    # Education Field Wise Attrition
    # --------------------------------------------------

    with col2:

        edu = (
            filtered_df[filtered_df["Attrition"]=="Yes"]
            .groupby("Education Field")
            .size()
            .reset_index(name="Count")
            .sort_values("Count")
        )

        fig = px.bar(
            edu,
            x="Count",
            y="Education Field",
            orientation="h",
            text="Count",
            color="Count"
        )

        fig.update_layout(
            template="plotly_dark",
            title="Education Field Wise Attrition",
            height=420
        )

        st.plotly_chart(fig,use_container_width=True)

    # ==========================================================
    # ROW 2
    # ==========================================================

    col3,col4 = st.columns(2)

    # --------------------------------------------------
    # Gender Wise Attrition
    # --------------------------------------------------

    with col3:

        gender = (
            filtered_df[filtered_df["Attrition"]=="Yes"]
            .groupby("Gender")
            .size()
            .reset_index(name="Count")
        )

        fig = px.pie(
            gender,
            names="Gender",
            values="Count",
            hole=0.60,
            title="Gender Wise Attrition"
        )

        fig.update_layout(
            template="plotly_dark",
            height=420
        )

        st.plotly_chart(fig,use_container_width=True)


    # --------------------------------------------------
    # Age Band Distribution
    # --------------------------------------------------

    with col4:

        age = (
            filtered_df.groupby("CF_age band")
            .size()
            .reset_index(name="Employees")
        )

        fig = px.bar(
            age,
            x="CF_age band",
            y="Employees",
            color="Employees",
            text="Employees"
        )

        fig.update_layout(
            template="plotly_dark",
            title="Employees by Age Group",
            height=420
        )

        st.plotly_chart(fig,use_container_width=True)

    # ==========================================================
    # ROW 3
    # ==========================================================

    col5, col6 = st.columns(2)

    # --------------------------------------------------
    # Job Role Wise Attrition
    # --------------------------------------------------

    with col5:

        job_role = (
            filtered_df[filtered_df["Attrition"] == "Yes"]
            .groupby("Job Role")
            .size()
            .reset_index(name="Attrition Count")
            .sort_values("Attrition Count", ascending=False)
        )

        fig = px.bar(
            job_role,
            x="Job Role",
            y="Attrition Count",
            color="Attrition Count",
            text="Attrition Count"
        )

        fig.update_layout(
            template="plotly_dark",
            title="Job Role Wise Attrition",
            height=450,
            xaxis_tickangle=-30
        )

        st.plotly_chart(fig, use_container_width=True)


    # --------------------------------------------------
    # Business Travel Analysis
    # --------------------------------------------------

    with col6:

        travel = (
            filtered_df
            .groupby("Business Travel")
            .size()
            .reset_index(name="Employees")
        )

        fig = px.pie(
            travel,
            names="Business Travel",
            values="Employees",
            hole=0.45
        )

        fig.update_layout(
            template="plotly_dark",
            title="Business Travel Distribution",
            height=450
        )

        st.plotly_chart(fig, use_container_width=True)

    # ==========================================================
    # ROW 4
    # ==========================================================

    col7, col8 = st.columns(2)

    # --------------------------------------------------
    # Monthly Income Distribution
    # --------------------------------------------------

    with col7:

        fig = px.histogram(
            filtered_df,
            x="Monthly Income",
            nbins=25,
            color="Attrition"
        )

        fig.update_layout(
            template="plotly_dark",
            title="Monthly Income Distribution",
            height=450
        )

        st.plotly_chart(fig, use_container_width=True)

    # --------------------------------------------------
    # Years At Company
    # --------------------------------------------------

    with col8:

        fig = px.box(
            filtered_df,
            x="Attrition",
            y="Years At Company",
            color="Attrition"
        )

        fig.update_layout(
            template="plotly_dark",
            title="Years At Company vs Attrition",
            height=450
        )

        st.plotly_chart(fig, use_container_width=True)

    # ==========================================================
    # ROW 5
    # ==========================================================

    col9, col10 = st.columns(2)

    # --------------------------------------------------
    # Job Satisfaction Heatmap
    # --------------------------------------------------

    with col9:

        heatmap = pd.crosstab(
            filtered_df["Job Satisfaction"],
            filtered_df["Attrition"]
        )

        fig = px.imshow(
            heatmap,
            text_auto=True,
            color_continuous_scale="Blues",
            aspect="auto"
        )

        fig.update_layout(
            title="Job Satisfaction vs Attrition",
            template="plotly_dark",
            height=450
        )

        st.plotly_chart(fig, use_container_width=True)


    # --------------------------------------------------
    # Overtime Analysis
    # --------------------------------------------------

    with col10:

        overtime = (
            filtered_df
            .groupby(["Over Time", "Attrition"])
            .size()
            .reset_index(name="Employees")
        )

        fig = px.bar(
            overtime,
            x="Over Time",
            y="Employees",
            color="Attrition",
            barmode="group",
            text="Employees"
        )

        fig.update_layout(
            template="plotly_dark",
            title="Over Time Analysis",
            height=450
        )

        st.plotly_chart(fig, use_container_width=True)


    # ==========================================================
    # ROW 6
    # ==========================================================

    col11, col12 = st.columns(2)

    # --------------------------------------------------
    # Age Distribution
    # --------------------------------------------------

    with col11:

        fig = px.histogram(
            filtered_df,
            x="Age",
            color="Attrition",
            nbins=20
        )

        fig.update_layout(
            template="plotly_dark",
            title="Age Distribution",
            height=450
        )

        st.plotly_chart(fig, use_container_width=True)


    # --------------------------------------------------
    # Performance Rating
    # --------------------------------------------------

    with col12:

        performance = (
            filtered_df
            .groupby("Performance Rating")
            .size()
            .reset_index(name="Employees")
        )

        fig = px.bar(
            performance,
            x="Performance Rating",
            y="Employees",
            color="Employees",
            text="Employees"
        )

        fig.update_layout(
            template="plotly_dark",
            title="Performance Rating",
            height=450
        )

        st.plotly_chart(fig, use_container_width=True)

    # ==========================================================
    # FOOTER
    # ==========================================================

    st.markdown("---")

    st.markdown(
    """
    <div style="text-align:center; color:gray;">
        <h4>HR Analytics Dashboard</h4>
        <p>Developed using Streamlit | Plotly | Machine Learning</p>
        </div>
    """,
    unsafe_allow_html=True
    )

# =====================================================
# SINGLE EMPLOYEE PREDICTION
# =====================================================
elif page == "🔮 Single Prediction":
    st.title("🔮 Employee Attrition Prediction")
    if st.session_state.logged_in:
        st.markdown(f"### Welcome, {st.session_state.username}!")
    st.markdown(
        "Enter employee information below to predict whether the employee is likely to leave the organization."
    )

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("Employee Details")

        age = st.number_input(
            "Age",
            min_value=18,
            max_value=60,
            value=30
        )

        daily_rate = st.number_input(
            "Daily Rate",
            value=800
        )

        distance = st.number_input(
            "Distance From Home",
            value=5
        )

        hourly_rate = st.number_input(
            "Hourly Rate",
            value=60
        )

        monthly_income = st.number_input(
            "Monthly Income",
            value=5000
        )

        monthly_rate = st.number_input(
            "Monthly Rate",
            value=12000
        )

        companies = st.number_input(
            "Number of Companies Worked",
            value=2
        )

        salary_hike = st.number_input(
            "Percent Salary Hike",
            value=15
        )

        total_work = st.number_input(
            "Total Working Years",
            value=10
        )

        training = st.number_input(
            "Training Times Last Year",
            value=3
        )

        years_company = st.number_input(
            "Years At Company",
            value=5
        )

        current_role = st.number_input(
            "Years In Current Role",
            value=3
        )

        promotion = st.number_input(
            "Years Since Last Promotion",
            value=1
        )

        manager = st.number_input(
            "Years With Curr Manager",
            value=3
        )

    with col2:

        st.subheader("Professional Details")

        business = st.selectbox(
            "Business Travel",
            sorted(df["Business Travel"].unique())
        )

        department = st.selectbox(
            "Department",
            sorted(df["Department"].unique())
        )

        education_field = st.selectbox(
            "Education Field",
            sorted(df["Education Field"].unique())
        )

        gender = st.selectbox(
            "Gender",
            sorted(df["Gender"].unique())
        )

        job_role = st.selectbox(
            "Job Role",
            sorted(df["Job Role"].unique())
        )

        marital = st.selectbox(
            "Marital Status",
            sorted(df["Marital Status"].unique())
        )

        overtime = st.selectbox(
            "Over Time",
            sorted(df["Over Time"].unique())
        )

        education = st.selectbox(
            "Education",
            sorted(df["Education"].unique())
        )

        environment = st.selectbox(
            "Environment Satisfaction",
            sorted(df["Environment Satisfaction"].unique())
        )

        involvement = st.selectbox(
            "Job Involvement",
            sorted(df["Job Involvement"].unique())
        )

        level = st.selectbox(
            "Job Level",
            sorted(df["Job Level"].unique())
        )

        satisfaction = st.selectbox(
            "Job Satisfaction",
            sorted(df["Job Satisfaction"].unique())
        )

        performance = st.selectbox(
            "Performance Rating",
            sorted(df["Performance Rating"].unique())
        )

        relationship = st.selectbox(
            "Relationship Satisfaction",
            sorted(df["Relationship Satisfaction"].unique())
        )

        worklife = st.selectbox(
            "Work Life Balance",
            sorted(df["Work Life Balance"].unique())
        )

        age_band = st.selectbox(
            "Age Band",
            sorted(df["CF_age band"].unique())
        )

        current_employee = st.selectbox(
            "Current Employee",
            sorted(df["CF_current Employee"].unique())
        )

    st.markdown("---")

    predict = st.button(
        "Predict Attrition",
        use_container_width=True
    )

    if predict:
        if model is not None:
            try:
                input_data = pd.DataFrame([[
                    age, daily_rate, distance, hourly_rate, monthly_income,
                    monthly_rate, companies, salary_hike, total_work, training,
                    years_company, current_role, promotion, manager,
                    business, department, education_field, gender, job_role,
                    marital, overtime, education, environment, involvement,
                    level, satisfaction, performance, relationship, worklife,
                    age_band, current_employee
                ]], columns=[
                    "Age", "Daily Rate", "Distance From Home", "Hourly Rate",
                    "Monthly Income", "Monthly Rate", "Num Companies Worked",
                    "Percent Salary Hike", "Total Working Years",
                    "Training Times Last Year", "Years At Company",
                    "Years In Current Role", "Years Since Last Promotion",
                    "Years With Curr Manager", "Business Travel", "Department",
                    "Education Field", "Gender", "Job Role", "Marital Status",
                    "Over Time", "Education", "Environment Satisfaction",
                    "Job Involvement", "Job Level", "Job Satisfaction",
                    "Performance Rating", "Relationship Satisfaction",
                    "Work Life Balance", "CF_age band", "CF_current Employee"
                ])

                prediction = model.predict(input_data)[0]
                proba = get_leave_probability(model, input_data)

                if is_leave_prediction(prediction):
                    st.error(f"⚠️ Employee is LIKELY to leave (Risk: {proba:.1%})")
                else:
                    st.success(f"✅ Employee is LIKELY to stay (Risk: {proba:.1%})")

            except Exception as e:
                st.error(f"Prediction error: {e}")
        else:
            st.warning("Model not found. Please ensure 'rf_pipeline.pkl' is in the working directory.")

# =====================================================
# BATCH PREDICTION
# =====================================================
elif page == "📁 Batch Prediction":
    st.title("📁 Batch Attrition Prediction")
    if st.session_state.logged_in:
        st.markdown(f"### Welcome, {st.session_state.username}!")
    st.markdown("Upload a CSV or Excel file with employee data for bulk prediction.")

    st.markdown("---")

    uploaded_file = st.file_uploader(
        "Upload Employee Data File",
        type=["csv", "xlsx"]
    )

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                batch_df = pd.read_csv(uploaded_file)
            else:
                batch_df = pd.read_excel(uploaded_file, engine="openpyxl")

            st.subheader("Uploaded Data Preview")
            st.dataframe(batch_df.head())

            if model is not None:
                predictions = model.predict(batch_df)
                proba_batch = model.predict_proba(batch_df)
                classes = getattr(model, "classes_", None)
                if classes is not None:
                    classes = list(classes)
                    if 1 in classes:
                        idx = classes.index(1)
                    elif "Yes" in classes:
                        idx = classes.index("Yes")
                    elif "yes" in classes:
                        idx = classes.index("yes")
                    else:
                        idx = 1 if proba_batch.shape[1] > 1 else 0
                else:
                    idx = 1 if proba_batch.shape[1] > 1 else 0
                probabilities = proba_batch[:, idx]

                batch_df["Attrition Prediction"] = ["Yes" if is_leave_prediction(p) else "No" for p in predictions]
                batch_df["Attrition Probability"] = (probabilities * 100).round(2)

                st.subheader("Prediction Results")
                st.dataframe(batch_df)

                csv = batch_df.to_csv(index=False)
                st.download_button(
                    "Download Results as CSV",
                    csv,
                    "attrition_predictions.csv",
                    "text/csv"
                )
            else:
                st.warning("Model not found. Please ensure 'rf_pipeline.pkl' is in the working directory.")

        except Exception as e:
            st.error(f"Error processing file: {e}")
