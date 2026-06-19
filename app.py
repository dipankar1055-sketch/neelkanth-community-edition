#!/usr/bin/env python3
"""
Neelkanth Community Edition – Prototype
5 Modules: Donation, Vendor, Volunteer, Incident, Certificate
Mobile-friendly, SQLite backend.
"""

import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import uuid
import os
from io import BytesIO
import base64

# Page config
st.set_page_config(
    page_title="Neelkanth Community Edition",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for mobile friendliness
st.markdown("""
<style>
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    .stButton button {
        width: 100%;
    }
    @media (max-width: 640px) {
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.25rem;
        }
        .stTabs [data-baseweb="tab"] {
            font-size: 0.75rem;
            padding: 0.5rem 0.5rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Database helper
DB_PATH = "neelkanth_community.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    # Donations
    c.execute('''CREATE TABLE IF NOT EXISTS donations (
        id TEXT PRIMARY KEY,
        donor_name TEXT,
        amount REAL,
        purpose TEXT,
        collector TEXT,
        status TEXT,
        date TEXT,
        trace_id TEXT
    )''')
    # Vendors
    c.execute('''CREATE TABLE IF NOT EXISTS vendors (
        id TEXT PRIMARY KEY,
        name TEXT,
        contact TEXT,
        amount_agreed REAL,
        amount_paid REAL,
        delivered TEXT,
        approver TEXT,
        trust_score REAL,
        trace_id TEXT
    )''')
    # Volunteers
    c.execute('''CREATE TABLE IF NOT EXISTS volunteers (
        id TEXT PRIMARY KEY,
        name TEXT,
        phone TEXT,
        duty TEXT,
        duty_status TEXT, -- assigned, accepted, completed
        shift_start TEXT,
        shift_end TEXT,
        reliability_score REAL,
        trace_id TEXT
    )''')
    # Incidents
    c.execute('''CREATE TABLE IF NOT EXISTS incidents (
        id TEXT PRIMARY KEY,
        type TEXT,
        description TEXT,
        location TEXT,
        reported_by TEXT,
        reported_at TEXT,
        resolved_at TEXT,
        resolution_notes TEXT,
        status TEXT,
        trace_id TEXT
    )''')
    conn.commit()
    conn.close()

# Initialize DB if not exists
if not os.path.exists(DB_PATH):
    init_db()

# Helper functions to generate Trace-ID
def generate_trace_id(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"

# Sidebar navigation
st.sidebar.title("🏛️ Neelkanth CE")
st.sidebar.markdown("### 5 Modules")
menu = st.sidebar.radio(
    "Choose module",
    ["📋 Donation Ledger", "🏷️ Vendor Register", "👤 Volunteer Register", "🚨 Incident Register", "🏆 Certificate of Integrity"]
)

# --- MODULE 1: DONATION LEDGER ---
if menu == "📋 Donation Ledger":
    st.header("📋 Donation Ledger")
    with st.expander("➕ Record New Donation"):
        with st.form("donation_form"):
            donor = st.text_input("Donor Name")
            amount = st.number_input("Amount (₹)", min_value=0.0, step=10.0)
            purpose = st.text_input("Purpose")
            collector = st.text_input("Collected By")
            status = st.selectbox("Status", ["Pending", "Deposited", "Spent"])
            submitted = st.form_submit_button("Save Donation")
            if submitted and donor and amount > 0:
                conn = get_db()
                c = conn.cursor()
                trace = generate_trace_id("DON")
                c.execute("INSERT INTO donations VALUES (?,?,?,?,?,?,?,?)",
                          (str(uuid.uuid4()), donor, amount, purpose, collector, status, datetime.now().isoformat(), trace))
                conn.commit()
                conn.close()
                st.success(f"✅ Donation recorded! Trace-ID: {trace}")
    # List donations
    conn = get_db()
    df = pd.read_sql_query("SELECT * FROM donations ORDER BY date DESC", conn)
    conn.close()
    if not df.empty:
        st.subheader("📊 Donation Records")
        st.dataframe(df[['donor_name', 'amount', 'purpose', 'collector', 'status', 'trace_id']], use_container_width=True)
    else:
        st.info("No donations recorded yet.")

# --- MODULE 2: VENDOR REGISTER ---
elif menu == "🏷️ Vendor Register":
    st.header("🏷️ Vendor Register")
    with st.expander("➕ Add Vendor"):
        with st.form("vendor_form"):
            name = st.text_input("Vendor Name")
            contact = st.text_input("Contact Info")
            amount_agreed = st.number_input("Amount Agreed (₹)", min_value=0.0, step=100.0)
            amount_paid = st.number_input("Amount Paid (₹)", min_value=0.0, step=100.0)
            delivered = st.selectbox("Material Delivered", ["Yes", "No", "Partial"])
            approver = st.text_input("Committee Approver")
            submitted = st.form_submit_button("Save Vendor")
            if submitted and name:
                conn = get_db()
                c = conn.cursor()
                trace = generate_trace_id("VEN")
                trust = 0.0  # placeholder
                c.execute("INSERT INTO vendors VALUES (?,?,?,?,?,?,?,?,?)",
                          (str(uuid.uuid4()), name, contact, amount_agreed, amount_paid, delivered, approver, trust, trace))
                conn.commit()
                conn.close()
                st.success(f"✅ Vendor added! Trace-ID: {trace}")
    # List vendors
    conn = get_db()
    df = pd.read_sql_query("SELECT * FROM vendors", conn)
    conn.close()
    if not df.empty:
        st.subheader("📊 Vendor Records")
        st.dataframe(df[['name', 'amount_agreed', 'amount_paid', 'delivered', 'approver', 'trace_id']], use_container_width=True)
    else:
        st.info("No vendors added yet.")

# --- MODULE 3: VOLUNTEER REGISTER ---
elif menu == "👤 Volunteer Register":
    st.header("👤 Volunteer Register")
    with st.expander("➕ Register Volunteer"):
        with st.form("volunteer_form"):
            name = st.text_input("Volunteer Name")
            phone = st.text_input("Phone Number")
            duty = st.text_input("Duty Assigned")
            status_duty = st.selectbox("Duty Status", ["Assigned", "Accepted", "Completed"])
            shift_start = st.time_input("Shift Start")
            shift_end = st.time_input("Shift End")
            submitted = st.form_submit_button("Save Volunteer")
            if submitted and name:
                conn = get_db()
                c = conn.cursor()
                trace = generate_trace_id("VOL")
                reliability = 0.0  # placeholder
                c.execute("INSERT INTO volunteers VALUES (?,?,?,?,?,?,?,?,?)",
                          (str(uuid.uuid4()), name, phone, duty, status_duty,
                           shift_start.strftime("%H:%M"), shift_end.strftime("%H:%M"),
                           reliability, trace))
                conn.commit()
                conn.close()
                st.success(f"✅ Volunteer registered! Trace-ID: {trace}")
    # List volunteers
    conn = get_db()
    df = pd.read_sql_query("SELECT * FROM volunteers", conn)
    conn.close()
    if not df.empty:
        st.subheader("📊 Volunteer Records")
        st.dataframe(df[['name', 'duty', 'duty_status', 'shift_start', 'shift_end', 'trace_id']], use_container_width=True)
    else:
        st.info("No volunteers registered yet.")

# --- MODULE 4: INCIDENT REGISTER ---
elif menu == "🚨 Incident Register":
    st.header("🚨 Incident Register")
    with st.expander("➕ Report Incident"):
        with st.form("incident_form"):
            incident_type = st.selectbox("Incident Type", ["Medical", "Safety", "Power", "Vendor Issue", "Other"])
            description = st.text_area("Description")
            location = st.text_input("Location")
            reported_by = st.text_input("Reported By")
            status_inc = st.selectbox("Status", ["Open", "In Progress", "Resolved"])
            resolution_notes = st.text_area("Resolution Notes (if resolved)")
            submitted = st.form_submit_button("Report Incident")
            if submitted and description:
                conn = get_db()
                c = conn.cursor()
                trace = generate_trace_id("INC")
                now = datetime.now().isoformat()
                c.execute("INSERT INTO incidents VALUES (?,?,?,?,?,?,?,?,?,?)",
                          (str(uuid.uuid4()), incident_type, description, location, reported_by, now, None if status_inc!="Resolved" else now, resolution_notes, status_inc, trace))
                conn.commit()
                conn.close()
                st.success(f"✅ Incident reported! Trace-ID: {trace}")
    # List incidents
    conn = get_db()
    df = pd.read_sql_query("SELECT * FROM incidents ORDER BY reported_at DESC", conn)
    conn.close()
    if not df.empty:
        st.subheader("📊 Incident Records")
        st.dataframe(df[['type', 'description', 'location', 'status', 'reported_at', 'trace_id']], use_container_width=True)
    else:
        st.info("No incidents reported yet.")

# --- MODULE 5: CERTIFICATE OF INTEGRITY ---
elif menu == "🏆 Certificate of Integrity":
    st.header("🏆 Certificate of Community Integrity")

    # Generate summary data
    conn = get_db()
    don_total = conn.execute("SELECT SUM(amount) FROM donations WHERE status='Deposited'").fetchone()[0] or 0
    don_count = conn.execute("SELECT COUNT(*) FROM donations").fetchone()[0] or 0
    ven_count = conn.execute("SELECT COUNT(*) FROM vendors").fetchone()[0] or 0
    vol_count = conn.execute("SELECT COUNT(*) FROM volunteers").fetchone()[0] or 0
    inc_resolved = conn.execute("SELECT COUNT(*) FROM incidents WHERE status='Resolved'").fetchone()[0] or 0
    inc_total = conn.execute("SELECT COUNT(*) FROM incidents").fetchone()[0] or 0
    conn.close()

    st.subheader("📊 Event Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Donations", f"₹{don_total:,.0f}", f"{don_count} transactions")
    col2.metric("Vendors", ven_count)
    col3.metric("Volunteers", vol_count)
    col4, col5 = st.columns(2)
    col4.metric("Incidents", inc_total)
    col5.metric("Incidents Resolved", inc_resolved)

    st.markdown("---")
    st.subheader("📄 Generate Certificate")

    if st.button("Generate Certificate of Integrity"):
        # Create an HTML certificate
        html = f"""
        <html>
        <head><meta charset="UTF-8"><title>Certificate of Integrity</title>
        <style>
            body {{ font-family: 'Times New Roman', serif; text-align: center; padding: 40px; }}
            .cert {{ border: 5px double #2c3e50; padding: 40px; max-width: 700px; margin: auto; }}
            h1 {{ color: #2c3e50; }}
            .seal {{ font-size: 48px; }}
            .details {{ text-align: left; margin: 20px 0; }}
            .footer {{ margin-top: 30px; font-style: italic; }}
        </style>
        </head>
        <body>
        <div class="cert">
            <div class="seal">🏛️</div>
            <h1>Certificate of Community Integrity</h1>
            <p><em>Issued by Neelkanth Community Edition</em></p>
            <hr>
            <div class="details">
                <p><strong>Total Donations:</strong> ₹{don_total:,.0f} (from {don_count} donors)</p>
                <p><strong>Vendors Engaged:</strong> {ven_count}</p>
                <p><strong>Volunteers Registered:</strong> {vol_count}</p>
                <p><strong>Incidents Reported:</strong> {inc_total} (Resolved: {inc_resolved})</p>
                <p><strong>Generated on:</strong> {datetime.now().strftime('%d %B %Y, %H:%M')}</p>
            </div>
            <hr>
            <p><strong>Verification:</strong> This certificate attests that the above event was conducted with transparency and accountability.</p>
            <p><em>Traceability is enabled via Trace-IDs recorded in the Neelkanth system.</em></p>
            <div class="footer">
                <p>Certificate ID: NCI-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}</p>
                <p>© 2026 Neelkanth Enterprise Pilot</p>
            </div>
        </div>
        </body>
        </html>
        """
        # Display the certificate in an iframe (or just show HTML)
        st.components.v1.html(html, height=700, scrolling=True)
        st.success("✅ Certificate generated! You can print this page to PDF using your browser's 'Print' option.")
        st.info("💡 Tip: Use 'Save as PDF' from the print dialog to download your certificate.")

    st.markdown("---")
    st.caption("The Certificate of Community Integrity is a summary of your event's governance records. It provides trust and transparency to donors, volunteers, and stakeholders.")
