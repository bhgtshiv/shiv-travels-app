import streamlit as st
from datetime import datetime, date
from PIL import Image
import io, csv, re, uuid, os

st.set_page_config(page_title="Shiv Travels", page_icon="🚌", layout="centered")
st.title("🚌 Shiv Travels – Booking System")

# ------------------- SESSION SETUP -------------------
if "rows" not in st.session_state:
    st.session_state.rows = []

if "inventory" not in st.session_state:
    # route-wise seat availability
    st.session_state.inventory = {
        ("Saharsa", "Patna"): {"AC": 20, "Non-AC": 40},
        ("Saharsa", "Siliguri"): {"AC": 24, "Non-AC": 35},
    }

# Fare config (₹)
fare_config = {"AC": 800, "Non-AC": 500, "meal": 150}

# ------------------- HELPERS -------------------
def mask_number(num: str) -> str:
    return "*" * (len(num) - 2) + num[-2:] if len(num) > 2 else num

def validate_phone(num: str) -> bool:
    return num.isdigit() and len(num) == 10

def booking_id():
    return "ST-" + datetime.now().strftime("%Y%m%d-") + str(uuid.uuid4())[:6].upper()

def save_to_csv(row):
    file_exists = os.path.exists("records.csv")
    with open("records.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()))
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

def send_email_demo(to, msg):
    if to:
        st.info(f"📧 Demo email to **{to}** —\n\n{msg}")

def get_inventory(fr, to):
    return st.session_state.inventory.get((fr, to), {"AC": 0, "Non-AC": 0})

# ------------------- MAIN FORM -------------------
st.subheader("Booking Form")

c_from, c_to = st.columns(2)
city_from = c_from.text_input("From", placeholder="Start city")
city_to = c_to.text_input("To", placeholder="Destination")

# show seats if route exists
inv = get_inventory(city_from, city_to)
if any(inv.values()):
    st.info(f"🪑 Available → AC: {inv['AC']} | Non-AC: {inv['Non-AC']}")
else:
    st.warning("⚠️ Route not in database — seats not tracked yet.")

jdate = st.date_input("Journey Date", value=date.today(), min_value=date.today(), format="DD/MM/YYYY")

col1, col2 = st.columns(2)
name = col1.text_input("Name", placeholder="Your full name")
phone = col2.text_input("Phone (10 digits)", max_chars=10, placeholder="98XXXXXXXX")

gender = st.selectbox("Gender", ["Select", "Male", "Female", "Other"], index=0)
emergency = st.text_input("Emergency Contact (optional)")
email = st.text_input("Email (for confirmation, optional)")

# Coach
coach = st.radio("Coach", ["Non-AC", "AC"], horizontal=True)
if coach == "Non-AC":
    nonac_category = "General"
    berth = ""
    st.write("Non-AC Category: **General**")
else:
    nonac_category = ""
    berth = st.selectbox("Seat (AC)", ["Upper", "Middle", "Lower"], index=0)

# Fare Calculation
fare = fare_config[coach]
prebook_meal = st.checkbox("Want to prebook your meals?")
if prebook_meal:
    fare += fare_config["meal"]

st.info(f"💰 Estimated Fare: ₹{fare}")

# Payment
payment = st.radio("Payment Mode", ["Cash", "Card", "Online"], horizontal=True)

card_last4 = ""
if payment == "Online":
    st.caption("Scan this QR to pay:")
    try:
        img = Image.open("qr.jpg")
        st.image(img, width=260)
    except Exception:
        st.warning("QR image not found. Add qr.jpg next to app.py")
elif payment == "Card":
    st.info("Card entry is demo-only. Don’t submit real details.")
    c1, c2 = st.columns([2, 1])
    card_num = c1.text_input("Card Number (16 digits)", max_chars=19)
    expiry = c2.text_input("MM/YY", max_chars=5)
    cvv = st.text_input("CVV", type="password", max_chars=4)
    if card_num.strip() and len(re.sub(r'\\s+', '', card_num)) >= 4:
        card_last4 = re.sub(r'\\s+', '', card_num)[-4:]

# ------------------- SUBMIT -------------------
submitted = st.button("Submit")

if submitted:
    errors = []
    if not city_from.strip(): errors.append("From required.")
    if not city_to.strip(): errors.append("To required.")
    if city_from.strip().lower() == city_to.strip().lower():
        errors.append("From and To cannot be same.")
    if not name.strip(): errors.append("Name required.")
    if not validate_phone(phone): errors.append("Invalid phone.")
    if gender not in ("Male", "Female", "Other"): errors.append("Select valid gender.")
    if inv and inv[coach] <= 0: errors.append(f"{coach} seats sold out.")
    
    # duplicate booking check
    for r in st.session_state.rows:
        if r["phone"] == phone and r["journey_date"] == jdate.strftime("%d/%m/%Y"):
            errors.append("Duplicate booking (same phone + date).")
            break

    if errors:
        st.error(" | ".join(errors))
    else:
        bid = booking_id()
        jdate_str = jdate.strftime("%d/%m/%Y")

        row = {
            "booking_id": bid,
            "from": city_from.strip(),
            "to": city_to.strip(),
            "journey_date": jdate_str,
            "name": name.strip(),
            "phone": phone.strip(),
            "gender": gender,
            "emergency": emergency.strip(),
            "email": email.strip(),
            "coach": coach,
            "nonac_category": nonac_category,
            "berth": berth,
            "payment": payment,
            "card_last4": card_last4,
            "fare": fare,
            "prebook_meal": int(prebook_meal),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        # Save
        st.session_state.rows.append(row)
        save_to_csv(row)

        # decrement seat if route found
        if (city_from, city_to) in st.session_state.inventory:
            st.session_state.inventory[(city_from, city_to)][coach] -= 1

        st.success(f"✅ Booking Confirmed: {bid}\n\n"
                   f"{city_from} → {city_to} on {jdate_str} | {coach} "
                   + (f"(Seat: {berth})" if coach == 'AC' else '(General)')
                   + f"\nName: {name}, Phone: {mask_number(phone)}"
                   + f"\nFare: ₹{fare} | Payment: {payment}"
                   + (f" ••••{card_last4}" if card_last4 else "")
                   )

        if email:
            send_email_demo(email, f"Your booking {bid} confirmed for {city_from} → {city_to} on {jdate_str}. Fare ₹{fare}.")

# ------------------- RECORDS TABLE -------------------
st.divider()
st.subheader("📋 Current Session Records")
if st.session_state.rows:
    st.dataframe(st.session_state.rows, use_container_width=True)
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=list(st.session_state.rows[0].keys()))
    writer.writeheader()
    writer.writerows(st.session_state.rows)
    st.download_button("Download CSV", data=buf.getvalue(), file_name="records.csv", mime="text/csv")
else:
    st.info("No bookings yet this session.")

# ------------------- ADMIN PANEL -------------------
st.divider()
st.subheader("🔐 Admin Dashboard")

pin = st.text_input("Enter Admin PIN", type="password")
if pin == "1234":
    st.success("Admin Access Granted ✅")

    # route inventory management
    st.write("### Seat Inventory")
    for (fr, to), stock in st.session_state.inventory.items():
        c1, c2, c3 = st.columns(3)
        c1.write(f"{fr} → {to}")
        ac_val = c2.number_input(f"AC seats ({fr}->{to})", value=int(stock["AC"]), key=f"ac_{fr}_{to}")
        nac_val = c3.number_input(f"Non-AC seats ({fr}->{to})", value=int(stock["Non-AC"]), key=f"nac_{fr}_{to}")
        st.session_state.inventory[(fr, to)] = {"AC": ac_val, "Non-AC": nac_val}

    st.divider()
    st.metric("Total Bookings", len(st.session_state.rows))
    ac_count = sum(1 for r in st.session_state.rows if r["coach"] == "AC")
    nac_count = len(st.session_state.rows) - ac_count
    st.metric("AC Bookings", ac_count)
    st.metric("Non-AC Bookings", nac_count)

    if st.button("Reset Session Data"):
        st.session_state.rows = []
        st.success("Session cleared.")
elif pin:
    st.error("Incorrect PIN ❌")
else:
    st.info("Enter PIN to manage routes or reset data.")
