import streamlit as st
from datetime import datetime, date
from PIL import Image
import io, csv, uuid

# -------------------- PAGE SETUP --------------------
st.set_page_config(page_title="Shiv Travels", page_icon="🚌", layout="centered")
st.title("🚌 Shiv Travels – Booking System")

# -------------------- SESSION SETUP --------------------
if "rows" not in st.session_state:
    st.session_state.rows = []

if "inventory" not in st.session_state:
    # available seats by route
    st.session_state.inventory = {
        ("Saharsa", "Patna"): {"AC": 20, "Non-AC": 40},
        ("Saharsa", "Siliguri"): {"AC": 24, "Non-AC": 35},
        ("Patna", "Delhi"): {"AC": 30, "Non-AC": 45},
    }

# fare per seat
fare_config = {"AC": 800, "Non-AC": 500, "meal": 150}

# -------------------- FUNCTIONS --------------------
def mask_number(num: str) -> str:
    return "*" * (len(num) - 2) + num[-2:] if len(num) > 2 else num

def validate_phone(num: str) -> bool:
    return num.isdigit() and len(num) == 10

# -------------------- USER INPUT --------------------
city_list = ["Saharsa", "Patna", "Siliguri", "Delhi", "Ranchi", "Bhagalpur", "Muzaffarpur", "Kolkata"]

col_from, col_to = st.columns(2)
city_from = col_from.selectbox("From", city_list, index=0)
city_to   = col_to.selectbox("To", city_list, index=1)

if city_from == city_to:
    st.warning("⚠️ 'From' and 'To' cannot be the same city.")

jdate = st.date_input("Journey Date", value=date.today(), min_value=date.today(), format="DD/MM/YYYY")

col1, col2 = st.columns(2)
name  = col1.text_input("Name", placeholder="Your full name")
phone = col2.text_input("Phone (10 digits)", max_chars=10, placeholder="98XXXXXXXX")

gender    = st.selectbox("Gender", ["Select", "Male", "Female", "Other"], index=0)
emergency = st.text_input("Emergency Contact (optional)")

# -------------------- COACH SELECTION --------------------
coach = st.radio("Coach Type", ["Non-AC", "AC"], horizontal=True)
available = st.session_state.inventory.get((city_from, city_to), {}).get(coach, "N/A")
st.info(f"🎟️ Available {coach} Seats: {available}")

if coach == "Non-AC":
    nonac_category = "General"
    berth = ""
    st.text("Category: General (Fixed)")
else:
    nonac_category = ""
    berth = st.selectbox("Seat (AC)", ["Upper", "Middle", "Lower"], index=0)

# -------------------- PAYMENT --------------------
payment = st.radio("Payment Mode", ["Cash", "Card", "Online"], horizontal=True)

if payment == "Card":
    card_col1, card_col2, card_col3 = st.columns(3)
    card_number = card_col1.text_input("Card Number", placeholder="XXXX XXXX XXXX XXXX")
    expiry      = card_col2.text_input("Expiry (MM/YY)", placeholder="MM/YY")
    cvv         = card_col3.text_input("CVV", type="password", max_chars=3)
elif payment == "Online":
    st.caption("Scan this QR to pay:")
    try:
        img = Image.open("qr.jpg")
        st.image(img, width=260)
    except Exception:
        st.warning("⚠️ QR image not found. Add 'qr.jpg' beside app.py.")
else:
    card_number = expiry = cvv = ""

prebook_meal = st.checkbox("🍱 Want to prebook your meals?")

# -------------------- SUBMIT --------------------
submitted = st.button("Submit Booking")

if submitted:
    errors = []
    if not name.strip(): errors.append("Name required")
    if not validate_phone(phone): errors.append("Phone must be 10 digits")
    if gender not in ("Male", "Female", "Other"): errors.append("Select valid gender")
    if city_from == city_to: errors.append("Choose different cities")

    if errors:
        st.error(" | ".join(errors))
    else:
        seats = st.session_state.inventory.get((city_from, city_to))
        if not seats or seats[coach] <= 0:
            st.error(f"No seats available for {coach} on this route.")
        else:
            # reduce one seat
            st.session_state.inventory[(city_from, city_to)][coach] -= 1

            jdate_str = jdate.strftime("%d/%m/%Y")
            fare = fare_config[coach] + (fare_config["meal"] if prebook_meal else 0)

            row = {
                "id": str(uuid.uuid4())[:8],
                "from": city_from,
                "to": city_to,
                "journey_date": jdate_str,
                "name": name.strip(),
                "phone": phone.strip(),
                "gender": gender,
                "emergency": emergency.strip(),
                "coach": coach,
                "berth": berth,
                "payment": payment,
                "fare": fare,
                "meal": int(prebook_meal),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            st.session_state.rows.append(row)
            st.success(
                f"✅ Booked: {city_from} → {city_to} on {jdate_str} | {coach} | "
                f"Seat: {berth or 'General'} | Fare ₹{fare} | {mask_number(phone)}"
            )

# -------------------- TABLE + DOWNLOAD --------------------
if st.session_state.rows:
    st.subheader("📋 Current Bookings")
    st.dataframe(st.session_state.rows, use_container_width=True)

    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=list(st.session_state.rows[0].keys()))
    writer.writeheader()
    writer.writerows(st.session_state.rows)
    st.download_button("⬇️ Download CSV", data=buf.getvalue(), file_name="shiv_travels_records.csv", mime="text/csv")
else:
    st.info("No bookings yet.")
