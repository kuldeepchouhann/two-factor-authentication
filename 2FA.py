import pyotp
import qrcode
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pyperclip
import time
import threading

# ---- UI Colors and Fonts ----
PRIMARY_COLOR = "#34495E"
SECONDARY_COLOR = "#2ECC71"
BACKGROUND_COLOR = "#ECF0F1"
TEXT_COLOR = "#2C3E50"
BUTTON_COLOR = "#3498DB"
BUTTON_HOVER_COLOR = "#2980B9"
VERIFY_BUTTON_COLOR = "#E74C3C"
VERIFY_BUTTON_HOVER_COLOR = "#C0392B"

HEADER_FONT = ("Helvetica", 18, "bold")
LABEL_FONT = ("Helvetica", 12)
ENTRY_FONT = ("Helvetica", 12)
BUTTON_FONT = ("Helvetica", 12, "bold")

# ---- Helper Functions ----
def generate_secret_key():
    return pyotp.random_base32()

def generate_provisioning_uri(username, secret_key):
    totp = pyotp.TOTP(secret_key)
    return totp.provisioning_uri(name=username, issuer_name='YourAppName')

def generate_qr_code(uri):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(uri)
    qr.make(fit=True)
    return qr.make_image(fill='black', back_color='white')

def verify_otp(secret_key, otp):
    totp = pyotp.TOTP(secret_key)
    return totp.verify(otp)

def is_valid_username(username):
    return len(username) >= 5 and username.isalnum()

def start_otp_timer():
    threading.Thread(target=otp_countdown, daemon=True).start()

def otp_countdown():
    def update_timer():
        totp = pyotp.TOTP(secret_key)
        time_remaining = totp.interval - time.time() % totp.interval
        otp_timer_label.config(text=f"OTP expires in: {int(time_remaining)} seconds")
        root.after(1000, update_timer)
    
    update_timer()

# ---- Event Handlers ----
def on_generate_click():
    username = username_entry.get().strip()
    if not is_valid_username(username):
        username_entry.config(style="Error.TEntry")
        messagebox.showwarning("Input Error", "Username must be at least 5 characters long and contain only alphanumeric characters.")
        return
    username_entry.config(style="TEntry")
    
    global secret_key, provisioning_uri
    secret_key = generate_secret_key()
    provisioning_uri = generate_provisioning_uri(username, secret_key)
    
    qr_img = generate_qr_code(provisioning_uri)
    qr_img_tk = ImageTk.PhotoImage(qr_img)
    
    qr_label.config(image=qr_img_tk)
    qr_label.image = qr_img_tk
    
    uri_label.config(text=f"Provisioning URI:\n{provisioning_uri}")
    verify_button.config(state=tk.NORMAL)
    otp_entry.delete(0, tk.END)
    start_otp_timer()

def on_verify_click():
    otp = otp_entry.get().strip()
    if not otp:
        otp_entry.config(style="Error.TEntry")
        messagebox.showwarning("Input Error", "Please enter an OTP.")
        return
    otp_entry.config(style="TEntry")

    if verify_otp(secret_key, otp):
        messagebox.showinfo("Success", "OTP verified successfully!")
    else:
        messagebox.showerror("Error", "Invalid OTP. Authentication failed.")

def on_copy_uri():
    pyperclip.copy(provisioning_uri)
    messagebox.showinfo("Copied", "Provisioning URI copied to clipboard!")

def save_secret_key():
    file = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
    if file:
        with open(file, 'w') as f:
            f.write(f"Secret Key: {secret_key}\nProvisioning URI: {provisioning_uri}")
        messagebox.showinfo("Saved", "Secret key and URI saved successfully!")

# ---- Hover Effects ----
def on_enter(e):
    if e.widget['background'] == BUTTON_COLOR:
        e.widget['background'] = BUTTON_HOVER_COLOR
    elif e.widget['background'] == VERIFY_BUTTON_COLOR:
        e.widget['background'] = VERIFY_BUTTON_HOVER_COLOR

def on_leave(e):
    if e.widget['background'] == BUTTON_HOVER_COLOR:
        e.widget['background'] = BUTTON_COLOR
    elif e.widget['background'] == VERIFY_BUTTON_HOVER_COLOR:
        e.widget['background'] = VERIFY_BUTTON_COLOR

# ---- UI Setup ----
root = tk.Tk()
root.title("2FA Setup")
root.geometry("450x700")
root.config(bg=BACKGROUND_COLOR)

# ---- Styles ----
style = ttk.Style()
style.configure("TLabel", background=BACKGROUND_COLOR, font=LABEL_FONT)
style.configure("TButton", font=BUTTON_FONT)
style.configure("TEntry", font=ENTRY_FONT)
style.configure("Error.TEntry", foreground="red")
style.configure("TFrame", background=BACKGROUND_COLOR)

# ---- Scrollable Frame ----
canvas = tk.Canvas(root, bg=BACKGROUND_COLOR, highlightthickness=0)
scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollable_frame = ttk.Frame(canvas, padding="10")

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

# ---- Widgets ----
title_label = ttk.Label(scrollable_frame, text="Two-Factor Authentication Setup", font=HEADER_FONT, foreground=PRIMARY_COLOR)
title_label.pack(pady=20)

username_label = ttk.Label(scrollable_frame, text="Username:")
username_label.pack(anchor="w", pady=5)
username_entry = ttk.Entry(scrollable_frame, width=40)
username_entry.pack(pady=5)

generate_button = tk.Button(scrollable_frame, text="Generate QR Code", command=on_generate_click, bg=BUTTON_COLOR, fg="white", font=BUTTON_FONT)
generate_button.pack(pady=20)
generate_button.bind("<Enter>", on_enter)
generate_button.bind("<Leave>", on_leave)

qr_label = ttk.Label(scrollable_frame, background=BACKGROUND_COLOR)
qr_label.pack(pady=10)

uri_label = ttk.Label(scrollable_frame, text="Provisioning URI will be displayed here.", wraplength=400, background=BACKGROUND_COLOR, font=LABEL_FONT)
uri_label.pack(pady=10)

copy_uri_button = tk.Button(scrollable_frame, text="Copy URI", command=on_copy_uri, bg=BUTTON_COLOR, fg="white", font=BUTTON_FONT)
copy_uri_button.pack(pady=5)
copy_uri_button.bind("<Enter>", on_enter)
copy_uri_button.bind("<Leave>", on_leave)

save_button = tk.Button(scrollable_frame, text="Save Secret Key", command=save_secret_key, bg=BUTTON_COLOR, fg="white", font=BUTTON_FONT)
save_button.pack(pady=5)
save_button.bind("<Enter>", on_enter)
save_button.bind("<Leave>", on_leave)

otp_frame = ttk.Frame(scrollable_frame, padding="10", relief="ridge")
otp_frame.pack(pady=20)

otp_label = ttk.Label(otp_frame, text="Enter OTP:")
otp_label.grid(row=0, column=0, padx=10, pady=10)
otp_entry = ttk.Entry(otp_frame, width=20)
otp_entry.grid(row=0, column=1, padx=10, pady=10)

otp_timer_label = ttk.Label(otp_frame, text="OTP expires in:", font=("Arial", 10))
otp_timer_label.grid(row=1, columnspan=2, pady=5)

verify_button = tk.Button(scrollable_frame, text="Verify OTP", command=on_verify_click, bg=VERIFY_BUTTON_COLOR, fg="white", font=BUTTON_FONT)
verify_button.pack(pady=10)
verify_button.bind("<Enter>", on_enter)
verify_button.bind("<Leave>", on_leave)

# ---- Layout ----
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# ---- Main Loop ----
root.mainloop()
