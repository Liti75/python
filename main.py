import tkinter as tk
from tkinter import messagebox
import sqlite3
import time
import os
import base64
from cryptography.fernet import Fernet
import string
import random
import pyperclip

# ---------- Folder Setup ----------
DATA_FOLDER = "PasswordManager"
KEY_FILE = os.path.join(DATA_FOLDER, "key.key")
DB_FILE = os.path.join(DATA_FOLDER, "passwords.db")

if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

# ---------- Encryption Key ----------
def generate_key():
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)

def load_key():
    if not os.path.exists(KEY_FILE):
        generate_key()
    with open(KEY_FILE, "rb") as f:
        return f.read()

fernet = Fernet(load_key())

# ---------- Database ----------
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS passwords (
    username TEXT,
    password TEXT,
    last_changed REAL
)
""")
conn.commit()

# ---------- Utility Functions ----------
def is_password_expired(timestamp):
    return (time.time() - timestamp) > (30 * 24 * 60 * 60)

def is_password_reused(username, password):
    cursor.execute("SELECT password FROM passwords WHERE username = ?", (username,))
    result = cursor.fetchone()
    if result:
        stored_encrypted = result[0]
        decrypted = fernet.decrypt(stored_encrypted.encode()).decode()
        return decrypted == password
    return False

def save_password(username, password):
    encrypted = fernet.encrypt(password.encode()).decode()
    now = time.time()
    cursor.execute("REPLACE INTO passwords (username, password, last_changed) VALUES (?, ?, ?)",
                   (username, encrypted, now))
    conn.commit()

def check_password_strength(pw):
    has_upper = any(c.isupper() for c in pw)
    has_lower = any(c.islower() for c in pw)
    has_digit = any(c.isdigit() for c in pw)
    has_special = any(c in string.punctuation for c in pw)
    length_ok = len(pw) >= 8

    score = sum([has_upper, has_lower, has_digit, has_special, length_ok])
    if score == 5:
        return "Strong"
    elif score >= 3:
        return "Medium"
    return "Weak"

def generate_strong_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))

# ---------- GUI ----------
root = tk.Tk()
root.title("Password Manager")
root.geometry("400x350")
root.resizable(False, False)

# Variables
username_var = tk.StringVar()
password_var = tk.StringVar()
length_var = tk.IntVar(value=12)
show_password_var = tk.BooleanVar()

# ---------- GUI Functions ----------
def toggle_password():
    password_entry.config(show="" if show_password_var.get() else "*")

def copy_to_clipboard():
    pyperclip.copy(password_var.get())
    messagebox.showinfo("Copied", "Password copied to clipboard!")

def generate_password():
    length = length_var.get()
    if length < 8:
        messagebox.showerror("Error", "Password length should be at least 8.")
        return
    password_var.set(generate_strong_password(length))

def save():
    username = username_var.get().strip()
    password = password_var.get()

    if not username or not password:
        messagebox.showerror("Error", "Username and password required.")
        return

    cursor.execute("SELECT last_changed FROM passwords WHERE username = ?", (username,))
    result = cursor.fetchone()

    if result:
        if is_password_reused(username, password):
            messagebox.showerror("Error", "Password reused. Use a new one.")
            return
        if is_password_expired(result[0]):
            messagebox.showwarning("Expired", "Password expired. Please change it.")

    strength = check_password_strength(password)
    if strength == "Weak":
        messagebox.showwarning("Weak", "Password is weak. Try a stronger one.")
        return

    save_password(username, password)
    messagebox.showinfo("Saved", f"{strength} password saved successfully!")

# ---------- Layout ----------
tk.Label(root, text="Username").pack(pady=5)
tk.Entry(root, textvariable=username_var).pack()

tk.Label(root, text="Password").pack(pady=5)
password_entry = tk.Entry(root, textvariable=password_var, show="*")
password_entry.pack()

tk.Checkbutton(root, text="Show Password", variable=show_password_var, command=toggle_password).pack()
tk.Button(root, text="Copy to Clipboard", command=copy_to_clipboard).pack(pady=5)

tk.Label(root, text="Password Length").pack()
tk.Entry(root, textvariable=length_var).pack()

tk.Button(root, text="Generate Password", command=generate_password).pack(pady=5)
tk.Button(root, text="Save Password", command=save).pack(pady=10)

root.mainloop()
