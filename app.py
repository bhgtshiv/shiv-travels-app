import streamlit as st
from datetime import datetime
import io
from PIL import Image

st.set_page_config(page_title="Shiv Travels", page_icon="🚌", layout="centered")
st.title("🚌 Shiv Travels – Booking Form")

# Session storage for this run
if "rows" not in st.session_state:
    st.session_state.rows = []

def mask_number(num: str) -> str:
    return "*" * (len(num) - 2) + num[-2:] if len(num) > 2 else num

def validate_phone(num: str) -> bool:
    return num.isdigit() and len(num) == 10

with st.form("booking_form", clear_on_submit=False):
    col1, col2 = st.columns(2)
    name = col1.text_input("Name", placeholder="Your full name")
    phone = col2.text_input("Phone (10 digits)", max_chars=10, placeholder="98XXXXXXXX")

    gender = st.selectbox("Gender", ["Select", "Male", "Female", "Other"], index=0)
    emergency = st.text_input("Emergency Contact (optional)")

    payment = st.radio("Payment Mode", ["Cash", "Card", "Online"], horizontal=True)

    # Show QR only for Online
    if payment == "Online":
        st.caption("Scan this QR to pay:")
        try:
            img = Image.open("qr.jpg")   # keep qr.jpg next to app.py
            st.image(img, width=260)
        except Exception:
            st.warning("QR image not found. Add a file named **qr.jpg** next to app.py.")

    prebook_meal = st.checkbox("Want to prebook your meals?")
    submitted = st.form_submit_button("Submit")

if submitted:
    errors = []
    if not name.strip():
        errors.append("Name is required.")
    if not validate_phone(phone):
        errors.append("Phone must be 10 digits.")
    if gender not in ("Male", "Female", "Other"):
        errors.append("Please select a valid Gender.")

    if errors:
        st.error(" | ".join(errors))
    else:
        row = {
            "name": name.strip(),
            "phone": phone.strip(),
            "gender": gender,
            "emergency": emergency.strip(),
            "payment": payment,
            "prebook_meal": int(prebook_meal),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        st.session_state.rows.append(row)
        st.success(
            f"Saved: {name.strip()}, {mask_number(phone)}, {gender}, {emergency or '-'}, {payment}, {int(prebook_meal)}"
        )

# Show table + CSV download
if st.session_state.rows:
    st.subheader("Current Submissions (this session)")
    st.dataframe(st.session_state.rows, use_container_width=True)

    import csv
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=list(st.session_state.rows[0].keys()))
    writer.writeheader()
    writer.writerows(st.session_state.rows)
    st.download_button("Download CSV", data=buf.getvalue(), file_name="records.csv", mime="text/csv")
else:
    st.info("No submissions yet.")
