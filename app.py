
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
import html

from database import (
    create_user,
    authenticate_user,
    add_transaction,
    get_transactions,
    delete_transaction
)


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="FinTrack | Personal Finance",
    page_icon="💸",
    layout="wide"
)


# ==================================================
# SESSION STATE
# ==================================================

if "user" not in st.session_state:
    st.session_state.user = None


# ==================================================
# CUSTOM CSS
# ==================================================

st.markdown("""
<style>
.stApp {
    background: #f3f7fb;
}

.block-container {
    padding-top: 2rem;
    max-width: 1400px;
}

h1, h2, h3 {
    color: #102a43;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #102a43, #164e63);
}

section[data-testid="stSidebar"] * {
    color: white;
}

div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #e5edf3;
    border-radius: 18px;
    padding: 22px;
    box-shadow: 0 5px 20px rgba(15, 41, 61, 0.05);
}

div[data-testid="stMetricLabel"] {
    color: #64748b;
    font-weight: 600;
}

div[data-testid="stMetricValue"] {
    color: #102a43;
    font-weight: 800;
}

div[data-testid="stForm"] {
    background: white;
    border: 1px solid #e5edf3;
    border-radius: 18px;
    padding: 24px;
}

div.stButton > button,
div.stFormSubmitButton > button {
    background: #0d9488;
    color: white;
    border: none;
    border-radius: 12px;
    font-weight: 700;
    min-height: 45px;
}

div.stButton > button:hover,
div.stFormSubmitButton > button:hover {
    background: #0f766e;
    color: white;
}

div[data-testid="stDataFrame"] {
    border-radius: 14px;
    overflow: hidden;
}

div[data-testid="stAlert"] {
    border-radius: 12px;
}

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)


# ==================================================
# REUSABLE HTML BANNER
# ==================================================

def show_banner(title, subtitle, eyebrow="FINTRACK"):

    safe_title = html.escape(title)
    safe_subtitle = html.escape(subtitle)
    safe_eyebrow = html.escape(eyebrow)

    banner_html = f"""
<div style="background:linear-gradient(120deg,#102a43,#0f766e);padding:30px;border-radius:20px;margin-bottom:25px;">
    <div style="color:#99f6e4;font-size:12px;font-weight:700;letter-spacing:1.5px;">
        {safe_eyebrow}
    </div>
    <div style="color:white;font-size:32px;font-weight:800;margin-top:10px;">
        {safe_title}
    </div>
    <div style="color:#d1fae5;font-size:16px;margin-top:8px;">
        {safe_subtitle}
    </div>
</div>
"""

    st.markdown(
        banner_html,
        unsafe_allow_html=True
    )


# ==================================================
# LOGIN AND SIGNUP PAGE
# ==================================================

def authentication_page():

    left, center, right = st.columns([1, 1.5, 1])

    with center:

        st.markdown(
            "<div style='text-align:center;padding:25px 0;'>"
            "<div style='font-size:60px;'>💸</div>"
            "<div style='font-size:44px;font-weight:850;color:#102a43;'>"
            "FinTrack</div>"
            "<div style='font-size:16px;color:#718096;margin-top:10px;'>"
            "Your money. Your goals. Your future.</div>"
            "<div style='font-size:15px;color:#718096;'>"
            "Manage your finances with confidence.</div>"
            "</div>",
            unsafe_allow_html=True
        )

        st.write("")

        login_tab, signup_tab = st.tabs([
            "🔐 Login",
            "✨ Create Account"
        ])

        # LOGIN
        with login_tab:

            st.subheader("Welcome back!")

            st.caption(
                "Log in to access your personal dashboard."
            )

            with st.form("login_form"):

                username = st.text_input(
                    "Username",
                    placeholder="Enter your username"
                )

                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Enter your password"
                )

                login_button = st.form_submit_button(
                    "Login to FinTrack",
                    use_container_width=True
                )

            if login_button:

                if not username.strip() or not password:

                    st.error(
                        "Please enter your username and password."
                    )

                else:

                    user = authenticate_user(
                        username,
                        password
                    )

                    if user:

                        st.session_state.user = user

                        st.rerun()

                    else:

                        st.error(
                            "Invalid username or password."
                        )

        # SIGNUP
        with signup_tab:

            st.subheader("Create your account")

            st.caption(
                "Start managing your money personally."
            )

            with st.form("signup_form"):

                new_username = st.text_input(
                    "Choose a username",
                    placeholder="Enter a username"
                )

                new_password = st.text_input(
                    "Create password",
                    type="password",
                    placeholder="At least 8 characters"
                )

                confirm_password = st.text_input(
                    "Confirm password",
                    type="password",
                    placeholder="Re-enter your password"
                )

                signup_button = st.form_submit_button(
                    "Create My Account",
                    use_container_width=True
                )

            if signup_button:

                if not new_username.strip():

                    st.error("Please enter a username.")

                elif len(new_password) < 8:

                    st.error(
                        "Password must be at least 8 characters."
                    )

                elif new_password != confirm_password:

                    st.error("Passwords do not match.")

                else:

                    created = create_user(
                        new_username,
                        new_password
                    )

                    if created:

                        st.success(
                            "Account created successfully! "
                            "Please log in."
                        )

                    else:

                        st.error(
                            "Username already exists. "
                            "Please choose another."
                        )

        st.markdown(
            "<div style='text-align:center;color:#94a3b8;"
            "font-size:12px;padding-top:25px;'>"
            "FINTRACK · PERSONAL FINANCE MANAGEMENT"
            "</div>",
            unsafe_allow_html=True
        )


# ==================================================
# MAIN DASHBOARD
# ==================================================

def dashboard_page():

    user = st.session_state.user

    user_id = user["id"]
    username = user["username"]

    safe_username = html.escape(username)

    # SIDEBAR
    st.sidebar.markdown(
        "<div style='text-align:center;padding:15px 0;'>"
        "<div style='font-size:40px;'>💸</div>"
        "<div style='font-size:27px;font-weight:850;color:white;'>"
        "FinTrack</div>"
        "<div style='font-size:11px;color:#99f6e4;"
        "letter-spacing:1px;'>PERSONAL FINANCE</div>"
        "</div>",
        unsafe_allow_html=True
    )

    st.sidebar.divider()

    st.sidebar.markdown(
        f"### 👤 {safe_username}"
    )

    st.sidebar.caption("Your personal finance space")

    page = st.sidebar.radio(
        "Navigation",
        [
            "Dashboard",
            "Add Transaction",
            "Manage Transactions"
        ]
    )

    st.sidebar.divider()

    if st.sidebar.button(
        "🚪 Logout",
        use_container_width=True
    ):

        st.session_state.user = None

        st.rerun()

    # LOAD THIS USER'S TRANSACTIONS
    records = get_transactions(user_id)

    columns = [
        "ID",
        "Date",
        "Type",
        "Category",
        "Amount",
        "Description"
    ]

    df = pd.DataFrame(
        records,
        columns=columns
    )

    if not df.empty:

        df["Date"] = pd.to_datetime(df["Date"])

        df["Amount"] = pd.to_numeric(df["Amount"])

    # ==================================================
    # DASHBOARD
    # ==================================================

    if page == "Dashboard":

        show_banner(
            f"Welcome back, {username} 👋",
            "Here's how your money is looking today.",
            "YOUR PERSONAL FINANCE SPACE"
        )

        if df.empty:

            st.markdown(
                "<div style='background:white;padding:40px;"
                "border-radius:20px;text-align:center;'>"
                "<div style='font-size:55px;'>🌱</div>"
                "<div style='font-size:25px;font-weight:750;"
                "color:#102a43;'>"
                "Your financial journey starts here</div>"
                "<div style='color:#718096;margin-top:10px;'>"
                "Add your first transaction to see your "
                "personal financial overview.</div>"
                "</div>",
                unsafe_allow_html=True
            )

            st.write("")

            st.info(
                "Choose Add Transaction from the sidebar "
                "to get started."
            )

        else:

            income = df.loc[
                df["Type"] == "Income",
                "Amount"
            ].sum()

            expenses = df.loc[
                df["Type"] == "Expense",
                "Amount"
            ].sum()

            balance = income - expenses

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "💚 Total Income",
                f"₹{income:,.2f}"
            )

            col2.metric(
                "❤️ Total Expenses",
                f"₹{expenses:,.2f}"
            )

            col3.metric(
                "💰 Available Balance",
                f"₹{balance:,.2f}"
            )

            st.write("")

            chart1, chart2 = st.columns(2)

            # EXPENSE CATEGORY CHART
            with chart1:

                st.subheader("🧾 Spending by Category")

                expense_df = df[
                    df["Type"] == "Expense"
                ]

                if not expense_df.empty:

                    category_summary = (
                        expense_df
                        .groupby("Category")["Amount"]
                        .sum()
                        .reset_index()
                    )

                    fig = px.pie(
                        category_summary,
                        names="Category",
                        values="Amount",
                        hole=0.55
                    )

                    fig.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        margin=dict(
                            t=20,
                            b=20,
                            l=10,
                            r=10
                        )
                    )

                    st.plotly_chart(
                        fig,
                        use_container_width=True
                    )

                else:

                    st.info("No expenses recorded yet.")

            # MONTHLY CHART
            with chart2:

                st.subheader("📊 Monthly Overview")

                monthly_df = df.copy()

                monthly_df["Month"] = (
                    monthly_df["Date"]
                    .dt.to_period("M")
                    .astype(str)
                )

                monthly_summary = (
                    monthly_df
                    .groupby(["Month", "Type"])["Amount"]
                    .sum()
                    .reset_index()
                )

                fig = px.bar(
                    monthly_summary,
                    x="Month",
                    y="Amount",
                    color="Type",
                    barmode="group",
                    color_discrete_map={
                        "Income": "#14b8a6",
                        "Expense": "#fb7185"
                    }
                )

                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(
                        t=20,
                        b=20,
                        l=10,
                        r=10
                    ),
                    xaxis_title="",
                    yaxis_title="Amount (₹)",
                    legend_title=""
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            st.divider()

            st.subheader("🕒 Recent Transactions")

            recent_df = df.sort_values(
                "Date",
                ascending=False
            ).head(5).copy()

            recent_df["Date"] = (
                recent_df["Date"]
                .dt.strftime("%d %b %Y")
            )

            recent_df["Amount"] = (
                recent_df["Amount"].apply(
                    lambda amount: f"₹{amount:,.2f}"
                )
            )

            st.dataframe(
                recent_df[
                    [
                        "Date",
                        "Type",
                        "Category",
                        "Amount",
                        "Description"
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )

    # ==================================================
    # ADD TRANSACTION
    # ==================================================

    elif page == "Add Transaction":

        show_banner(
            "Add a Transaction ✨",
            "Keep track of every rupee that comes in or goes out.",
            "YOUR MONEY JOURNAL"
        )

        with st.form("transaction_form"):

            st.subheader("Transaction Details")

            transaction_date = st.date_input(
                "Transaction Date",
                value=date.today()
            )

            transaction_type = st.selectbox(
                "Transaction Type",
                ["Expense", "Income"]
            )

            category = st.selectbox(
                "Category",
                [
                    "Food",
                    "Transport",
                    "Shopping",
                    "Bills",
                    "Entertainment",
                    "Health",
                    "Education",
                    "Salary",
                    "Business",
                    "Other"
                ]
            )

            amount = st.number_input(
                "Amount (₹)",
                min_value=0.01,
                step=100.0,
                format="%.2f"
            )

            description = st.text_input(
                "Description",
                placeholder="Example: Lunch, monthly salary..."
            )

            submit_button = st.form_submit_button(
                "💾 Save Transaction",
                use_container_width=True
            )

        if submit_button:

            add_transaction(
                user_id,
                str(transaction_date),
                transaction_type,
                category,
                amount,
                description
            )

            st.success(
                "Transaction saved successfully!"
            )

            st.rerun()

    # ==================================================
    # MANAGE TRANSACTIONS
    # ==================================================

    elif page == "Manage Transactions":

        show_banner(
            "Manage Transactions 📋",
            "View and manage your personal financial records.",
            "YOUR TRANSACTION HISTORY"
        )

        if df.empty:

            st.info(
                "You don't have any transactions yet."
            )

        else:

            display_df = df.copy()

            display_df["Date"] = (
                display_df["Date"]
                .dt.strftime("%d %b %Y")
            )

            display_df["Amount"] = (
                display_df["Amount"].apply(
                    lambda amount: f"₹{amount:,.2f}"
                )
            )

            st.dataframe(
                display_df[
                    [
                        "ID",
                        "Date",
                        "Type",
                        "Category",
                        "Amount",
                        "Description"
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )

            st.divider()

            st.subheader("🗑️ Delete a Transaction")

            transaction_ids = df["ID"].tolist()

            selected_id = st.selectbox(
                "Select transaction ID",
                transaction_ids
            )

            if st.button(
                "Delete Selected Transaction",
                type="primary",
                use_container_width=True
            ):

                delete_transaction(
                    selected_id,
                    user_id
                )

                st.success(
                    "Transaction deleted successfully."
                )

                st.rerun()


# ==================================================
# APP ENTRY POINT
# ==================================================

if st.session_state.user is None:

    authentication_page()

else:

    dashboard_page()
