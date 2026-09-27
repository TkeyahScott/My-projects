#GUI PASSWORD MANAGER
#28 AUGUST 2026
#T. SCOTT
#V1.0


#Step 1.1: Initialize the UI with Tkinter
    #This script sets up a basic interface \
    #  with fields for the website, email, and password.

import tkinter as tk
from tkinter import messagebox

def save_password():
    website = website_entry.get()
    email = email_entry.get()
    password = password_entry.get()
    
    if not website or not email or not password:
        messagebox.showwarning(title="Error", message="Please fill out all fields!")
        return
        
    # Temporary placeholder for saving logic
    messagebox.showinfo(title="Success", message="Data captured successfully!")

# Window setup
window = tk.Tk()
window.title("Secure Password Manager")
window.config(padx=40, pady=40)

# Labels & Entries
tk.Label(text="Website:").grid(row=1, column=0, sticky="W")
website_entry = tk.Entry(width=35)
website_entry.grid(row=1, column=1, columnspan=2, pady=5)
website_entry.focus()

tk.Label(text="Email/Username:").grid(row=2, column=0, sticky="W")
email_entry = tk.Entry(width=35)
email_entry.grid(row=2, column=1, columnspan=2, pady=5)

tk.Label(text="Password:").grid(row=3, column=0, sticky="W")
password_entry = tk.Entry(width=21)
password_entry.grid(row=3, column=1, pady=5, sticky="W")

# Buttons
gen_pass_btn = tk.Button(text="Generate")
gen_pass_btn.grid(row=3, column=2, sticky="E")

save_btn = tk.Button(text="Add Credentials", width=33, command=save_password)
save_btn.grid(row=4, column=1, columnspan=2, pady=10)

window.mainloop()


#Step 1.2: Add Password Generation & Clipboard Support
    #Install pyperclip via the terminal (pip install pyperclip) \
    # So the app can auto-copy passwords to the clipboard. \
    # Add this generation function to the script and link it to the Generate button:

import secrets
import string
import pyperclip

def generate_password():
    password_entry.delete(0, tk.END)
    
    alphabet = string.ascii_letters + string.digits + string.punctuation
    # Secure random generation suitable for cryptography
    password = ''.join(secrets.choice(alphabet) for _ in range(16))
    
    password_entry.insert(0, password)
    pyperclip.copy(password) # Auto-copy to clipboard


#Step 1.3: Secure Data with Encryption
