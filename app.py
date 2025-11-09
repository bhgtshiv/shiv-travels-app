import streamlit as st
from datetime import datetime, date
from PIL import Image
import io, csv

st.set_page_config(page_title="Shiv Travels", page_icon="🚌", layout="centered")
st.title("🚌 Shiv Travels – Booking Form")

# Session table store
if "rows" not in st.session_state:
    st.session_state.rows = []

def mask_number(num: str) -> str:
    return "*" * (len(num) - 2) + num[-2:] if len(num) > 2 else num

def validate_phone(num: str) -> bool:
    return num.isdigit() and len(num) == 10

# -------- Inputs (LIVE, no form -> instant re-render) --------
c_from, c_to = st.columns(2)
city_from = c_from.text_input("From", placeholder="Start city")
city_to   = c_to.text_input("To", placeholder="Destination")

jdate = st.date_input("Journey Date", value=date.today(), min_value=date.today(), format="DD/MM/YYYY")

col1, col2 = st.columns(2)
name  = col1.text_input("Name", placeholder="Your full name")
phone = col2.text_input("Phone (10 digits)", max_chars=10, placeholder="98XXXXXXXX")

gender    = st.selectbox("Gender", ["Select", "Male", "Female", "Other"], index=0)
emergency = st.text_input("Emergency Contact (optional)")

# Coach + conditional
coach = st.radio("Coach", ["Non-AC", "AC"], horizontal=True)

if coach == "Non-AC":
    nonac_category = "General"   # fixed as requested
    berth = ""
    st.write("Non-AC Category: **General**")
else:
    nonac_category = ""
    berth = st.selectbox("Seat (AC)", ["Upper", "Middle", "Lower"], index=0)

# Payment + QR
payment = st.radio("Payment Mode", ["Cash", "Card", "Online"], horizontal=True)
if payment == "Online":
    st.caption("Scan this QR to pay:")
    try:
        img = Image.open("qr.jpg")  # keep qr.jpg next to app.py
        st.image(img, width=260)
    except Exception:
        st.warning("QR image not found. Add a file named **qr.jpg** next to app.py.")

prebook_meal = st.checkbox("Want to prebook your meals?")

# Submit
submitted = st.button("Submit")

# -------- Submit Logic --------
if submitted:
    errors = []
    if not city_from.strip(): errors.append("From is required.")
    if not city_to.strip():   errors.append("To is required.")
    if not name.strip():      errors.append("Name is required.")
    if not validate_phone(phone): errors.append("Phone must be 10 digits.")
    if gender not in ("Male", "Female", "Other"): errors.append("Please select a valid Gender.")

    if errors:
        st.error(" | ".join(errors))
    else:
        jdate_str = jdate.strftime("%d/%m/%Y")
        row = {
            "from": city_from.strip(),
            "to": city_to.strip(),
            "journey_date": jdate_str,
            "name": name.strip(),
            "phone": phone.strip(),
            "gender": gender,
            "emergency": emergency.strip(),
            "coach": coach,
            "nonac_category": nonac_category,  # "General" for Non-AC, "" for AC
            "berth": berth,                    # "", or Upper/Middle/Lower for AC
            "payment": payment,
            "prebook_meal": int(prebook_meal),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        st.session_state.rows.append(row)
        st.success(
            f"Saved: {city_from} → {city_to} on {jdate_str} | {coach} "
            + (f"(Seat: {berth})" if coach == "AC" else "(General)")
            + f" | {name}, {mask_number(phone)} | {payment}"
        )

# -------- Table + CSV --------
if st.session_state.rows:
    st.subheader("Current Submissions (this session)")
    st.dataframe(st.session_state.rows, use_container_width=True)

    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=list(st.session_state.rows[0].keys()))
    writer.writeheader()
    writer.writerows(st.session_state.rows)
    st.download_button("Download CSV", data=buf.getvalue(), file_name="records.csv", mime="text/csv")
else:
    st.info("No submissions yet.")
