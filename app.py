from tkinter import *
from tkinter import messagebox
from tkinter import ttk  # NEW: for Combobox
import os

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

root = Tk()
root.title("Shiv Travels")

def getvals():

    if gendervalu.get() not in ("Male", "Female", "Other"):
        messagebox.showerror("Missing Gender", "Please select a valid Gender: Male, Female, or Other.")
        return


    if not namevalu.get().strip():
        messagebox.showerror("Missing Name", "Please enter your name.")
        return
    if len(phone_real) != 10:
        messagebox.showerror("Invalid Phone", "Please enter a 10-digit phone number.")
        return

    print("Submitting Form")
    record = (
        f"{namevalu.get().strip()},"
        f"{phone_real},"
        f"{gendervalu.get().strip()},"
        f"{emergencyvalu.get().strip()},"
        f"{paymentmoodvalu.get().strip()},"
        f"{foodservicevalue.get()}\n"
    )
    print(record.strip())
    with open("records.txt", "a", encoding="utf-8") as f:
        f.write(record)
    messagebox.showinfo("Saved", "Your details have been saved.")

# ---------- OPTPUT size ----------
root.geometry("520x650")
root.minsize(820, 850)   # FIXED: minsize should not exceed maxsize/geometry
root.maxsize(800, 800)

# ---------- Heading ----------
Label(root, text="Welcome to Shiv Travels", font="comicsansms 13 bold", pady=14).grid(row=0, column=3)

# ---------- Labels ----------
Label(root, text="Name").grid(row=1, column=2)
Label(root, text="Phone").grid(row=2, column=2)
Label(root, text="Gender").grid(row=3, column=2)
Label(root, text="Emergency Contact").grid(row=4, column=2)
Label(root, text="Payment Mode").grid(row=5, column=2)

# ---------- Variables ----------
namevalu = StringVar()
gendervalu = StringVar()
emergencyvalu = StringVar()
paymentmoodvalu = StringVar(value="Cash")  # Cash / Card / Online
foodservicevalue = IntVar()
phone_real = ""     # to store full number (unmasked)

# ---------- Entry Box Style ----------
entry_style = {"bd": 2, "relief": "solid", "font": ("Segoe UI", 10)}

# ---------- Entries ----------
nameentry = Entry(root, textvariable=namevalu, **entry_style)
phoneentry = Entry(root, **entry_style)

# NEW: Gender as read-only dropdown
genderentry = ttk.Combobox(
    root,
    textvariable=gendervalu,
    values=("Male", "Female", "Other"),
    state="readonly",
    font=("Segoe UI", 10)
)
genderentry.set("Select")  # placeholder

emergecyentry = Entry(root, textvariable=emergencyvalu, **entry_style)
paymentmoodentry = Entry(root, textvariable=paymentmoodvalu, **entry_style)

# ---------- Grid ----------
nameentry.grid(row=1, column=3, ipady=4, padx=4, pady=2, sticky="we")
phoneentry.grid(row=2, column=3, ipady=4, padx=4, pady=2, sticky="we")
genderentry.grid(row=3, column=3, ipady=2, padx=4, pady=2, sticky="we")  # Combobox
emergecyentry.grid(row=4, column=3, ipady=4, padx=4, pady=2, sticky="we")
paymentmoodentry.grid(row=5, column=3, ipady=4, padx=4, pady=2, sticky="we")

# ---------- Phone Mask (********51) ----------
def mask_number(num: str) -> str:
    n = len(num)
    if n <= 2:
        return num
    return "*" * (n - 2) + num[-2:]

def on_phone_key(event):
    global phone_real
    if event.keysym == "BackSpace":
        phone_real = phone_real[:-1]
    elif event.char.isdigit() and len(phone_real) < 10:
        phone_real += event.char
    phoneentry.delete(0, END)
    phoneentry.insert(0, mask_number(phone_real))
    phoneentry.icursor(END)
    return "break"

phoneentry.bind("<KeyPress>", on_phone_key)

# ---------- Payment Mode (Cash/Card/Online) ----------
pm_frame = Frame(root)
pm_frame.grid(row=6, column=3, sticky="w", pady=4)

def set_payment(val):
    paymentmoodvalu.set(val)
    update_payment_ui()

Radiobutton(pm_frame, text="Cash",   variable=paymentmoodvalu, value="Cash",
            command=lambda: set_payment("Cash")).pack(side=LEFT)
Radiobutton(pm_frame, text="Card",   variable=paymentmoodvalu, value="Card",
            command=lambda: set_payment("Card")).pack(side=LEFT)
Radiobutton(pm_frame, text="Online", variable=paymentmoodvalu, value="Online",
            command=lambda: set_payment("Online")).pack(side=LEFT)

# ---------- QR Image Area ----------
qr_frame = Frame(root)
qr_frame.grid(row=7, column=3, sticky="we", pady=(6, 2))
qr_title = Label(qr_frame, text="Scan to Pay", font=("Segoe UI", 10, "bold"))
qr_img_label = Label(qr_frame)
qr_hint = Label(qr_frame, text="UPI/QR ke through payment karein.", font=("Segoe UI", 9))

QR_PATH = r"D:\python\GUI problam solving\Shiv_Travels.jpg"
qr_photo_ref = {"img": None}

def load_qr_image(path):
    if not os.path.exists(path):
        return None
    ext = os.path.splitext(path)[1].lower()
    try:
        if ext in [".png", ".gif"]:
            return PhotoImage(file=path)  # native support
        # JPG/JPEG ke liye PIL
        if PIL_AVAILABLE:
            img_pil = Image.open(path)
            max_w = 320
            if img_pil.width > max_w:
                ratio = max_w / img_pil.width
                img_pil = img_pil.resize((int(img_pil.width * ratio), int(img_pil.height * ratio)))
            return ImageTk.PhotoImage(img_pil)
        else:
            return None
    except Exception as e:
        print("QR load error:", e)
        return None

def update_payment_ui():
    if paymentmoodvalu.get() == "Online":
        img = load_qr_image(QR_PATH)
        if img is None:
            msg = "QR not found OR Pillow not installed for .jpg\nFix: pip install pillow  (ya file path check karo)"
            qr_title.config(text="QR not available", fg="red")
            qr_img_label.config(image="", text=msg, justify="left")
            qr_img_label.grid(row=1, column=0, pady=4, sticky="w")
            qr_photo_ref["img"] = None
            qr_title.grid(row=0, column=0, sticky="w")
            qr_hint.grid_forget()
        else:
            qr_title.config(text="Scan to Pay", fg="black")
            qr_photo_ref["img"] = img
            qr_img_label.config(image=img, text="")
            qr_title.grid(row=0, column=0, sticky="w")
            qr_img_label.grid(row=1, column=0, pady=4, sticky="w")
            qr_hint.grid(row=2, column=0, sticky="w")
    else:
        qr_title.grid_forget()
        qr_img_label.grid_forget()
        qr_hint.grid_forget()

update_payment_ui()

# ---------- Checkbox ----------
foodservice = Checkbutton(text="Want to prebook your meals?", variable=foodservicevalue)
foodservice.grid(row=8, column=3, pady=4, sticky="w")

# ---------- Submit Button ----------
Button(text="Login to Shiv Travels", command=getvals).grid(row=9, column=3, pady=8, sticky="e")

# allow column 3 to stretch
root.grid_columnconfigure(3, weight=1)

root.mainloop()
