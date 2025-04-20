import os
import tkinter as tk
from tkinter import ttk, messagebox
import csv

# === CSV Setup ===
USER_CSV = 'users.csv'
EXPENSE_CSV = 'expenses.csv'

# Ensure files exist with headers
if not os.path.exists(USER_CSV):
    with open(USER_CSV, 'w', newline='') as f:
        csv.writer(f).writerow(['username', 'name', 'email', 'password'])
if not os.path.exists(EXPENSE_CSV):
    with open(EXPENSE_CSV, 'w', newline='') as f:
        csv.writer(f).writerow(['username', 'month', 'category', 'item', 'amount'])


# === Register Page ===
class RegisterPage(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#f4f8fb")
        self.master = master
        self.entries = {}

        container = tk.Frame(self, bg="#ffffff", bd=2, relief="ridge")
        container.place(relx=0.5, rely=0.5, anchor="center", width=360, height=520)

        tk.Label(container, text="Create Account", font=("Segoe UI", 18, "bold"),
                 bg="#ffffff", fg="#2c3e50").pack(pady=(30, 5))
        tk.Label(container, text="Start tracking your expenses today", font=("Segoe UI", 10),
                 bg="#ffffff", fg="#7f8c8d").pack(pady=(0, 20))

        self._make_field(container, "Full Name", "name")
        self._make_field(container, "Username", "username")
        self._make_field(container, "Email", "email")
        self._make_field(container, "Password", "password", show="*")

        tk.Button(container, text="Register", font=("Segoe UI", 11, "bold"),
                  bg="#3498db", fg="white", bd=0, cursor="hand2",
                  activebackground="#2980b9", command=self.register).pack(pady=15, ipadx=10, ipady=6)

        tk.Label(container, text="Already have an account?", bg="#ffffff",
                 font=("Segoe UI", 9)).pack()
        tk.Button(container, text="Go to Login", font=("Segoe UI", 9, "underline"),
                  fg="#3498db", bg="#ffffff", bd=0, cursor="hand2",
                  activeforeground="#2980b9",
                  command=lambda: master.show_frame(LoginPage)).pack(pady=(0,10))

    def _make_field(self, parent, label, key, show=None):
        tk.Label(parent, text=label, bg="#ffffff", anchor="w",
                 font=("Segoe UI", 9)).pack(fill="x", padx=40)
        e = tk.Entry(parent, font=("Segoe UI", 11), bd=1, relief="solid", show=show)
        e.pack(padx=40, pady=(0,12), fill="x", ipady=4)
        self.entries[key] = e

    def register(self):
        uname = self.entries["username"].get().strip()
        pwd   = self.entries["password"].get().strip()
        name  = self.entries["name"].get().strip()
        email = self.entries["email"].get().strip()

        if not uname or not pwd:
            messagebox.showwarning("Missing Fields", "Username and password are required.")
            return

        with open(USER_CSV, 'r', newline='') as f:
            reader = csv.reader(f)
            next(reader, None)
            if any(row and row[0] == uname for row in reader):
                messagebox.showwarning("Exists", "Username already exists.")
                return

        with open(USER_CSV, 'a', newline='') as f:
            csv.writer(f).writerow([uname, name, email, pwd])

        messagebox.showinfo("Success", "Registered Successfully!")
        self.master.show_frame(LoginPage)


# === Login Page ===
class LoginPage(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#f4f8fb")
        self.master = master

        container = tk.Frame(self, bg="#ffffff", bd=2, relief="ridge")
        container.place(relx=0.5, rely=0.5, anchor="center", width=320, height=400)

        tk.Label(container, text="Login", font=("Segoe UI", 18, "bold"),
                 bg="#ffffff", fg="#2c3e50").pack(pady=(40,5))
        tk.Label(container, text="Welcome back!", font=("Segoe UI", 10),
                 bg="#ffffff", fg="#7f8c8d").pack(pady=(0,20))

        tk.Label(container, text="Username", bg="#ffffff", anchor="w",
                 font=("Segoe UI", 9)).pack(fill="x", padx=30)
        self.user_e = tk.Entry(container, font=("Segoe UI", 11), bd=1, relief="solid")
        self.user_e.pack(padx=30, pady=(0,12), fill="x", ipady=4)

        tk.Label(container, text="Password", bg="#ffffff", anchor="w",
                 font=("Segoe UI", 9)).pack(fill="x", padx=30)
        self.pwd_e = tk.Entry(container, font=("Segoe UI", 11), bd=1, relief="solid", show="*")
        self.pwd_e.pack(padx=30, pady=(0,20), fill="x", ipady=4)

        tk.Button(container, text="Login", font=("Segoe UI", 11, "bold"),
                  bg="#2ecc71", fg="white", bd=0, cursor="hand2",
                  activebackground="#27ae60", command=self.login).pack(pady=10, ipadx=10, ipady=6)

        tk.Button(container, text="Back to Register", font=("Segoe UI", 9, "underline"),
                  fg="#3498db", bg="#ffffff", bd=0, cursor="hand2",
                  activeforeground="#2980b9",
                  command=lambda: master.show_frame(RegisterPage)).pack()

    def login(self):
        uname = self.user_e.get().strip()
        pwd   = self.pwd_e.get().strip()

        with open(USER_CSV, 'r', newline='') as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                if len(row) >= 4 and row[0] == uname and row[3] == pwd:
                    self.master.current_user = uname
                    messagebox.showinfo("Login Success", f"Welcome, {row[1]}!")
                    self.master.show_frame(ExpenseTrackerPage)
                    return
        messagebox.showerror("Failed", "Invalid username or password.")


# === Expense Tracker Page ===
class ExpenseTrackerPage(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#f4f8fb")
        self.master = master

        container = tk.Frame(self, bg="#ffffff", bd=2, relief="ridge")
        container.place(relx=0.5, rely=0.5, anchor="center", width=380, height=560)

        tk.Label(container, text="Expense Tracker", font=("Segoe UI", 18, "bold"),
                 bg="#ffffff", fg="#2c3e50").pack(pady=(20,10))

        # Month
        tk.Label(container, text="Month", bg="#ffffff", font=("Segoe UI", 9)).pack(anchor="w", padx=30)
        self.month_cb = ttk.Combobox(container, values=[
            "January","February","March","April","May","June",
            "July","August","September","October","November","December"
        ], state="readonly", font=("Segoe UI", 11))
        self.month_cb.set("January")
        self.month_cb.pack(padx=30, pady=(0,15), fill="x")
        self.month_cb.bind("<<ComboboxSelected>>", lambda e: self.load_history())

        # Category
        tk.Label(container, text="Category", bg="#ffffff", font=("Segoe UI", 9)).pack(anchor="w", padx=30)
        self.cat_cb = ttk.Combobox(container, values=["Food","Transport","Entertainment","Utilities","Others"],
                                   state="readonly", font=("Segoe UI", 11))
        self.cat_cb.set("Food")
        self.cat_cb.pack(padx=30, pady=(0,15), fill="x")

        # Item & Price
        tk.Label(container, text="Item", bg="#ffffff", font=("Segoe UI", 9)).pack(anchor="w", padx=30)
        self.item_e = tk.Entry(container, font=("Segoe UI", 11), bd=1, relief="solid")
        self.item_e.pack(padx=30, pady=(0,12), fill="x", ipady=4)

        tk.Label(container, text="Price (₱)", bg="#ffffff", font=("Segoe UI", 9)).pack(anchor="w", padx=30)
        self.price_e = tk.Entry(container, font=("Segoe UI", 11), bd=1, relief="solid")
        self.price_e.pack(padx=30, pady=(0,15), fill="x", ipady=4)

        tk.Button(container, text="Add Expense", font=("Segoe UI", 11, "bold"),
                  bg="#3498db", fg="white", bd=0, cursor="hand2",
                  activebackground="#2980b9", command=self.add_expense).pack(padx=30, pady=5, ipadx=10, ipady=6)

        self.listbox = tk.Listbox(container, font=("Segoe UI", 10), height=8)
        self.listbox.pack(padx=30, pady=(15,5), fill="both", expand=True)

        self.total_lbl = tk.Label(container, text="Total: ₱0.00", font=("Segoe UI", 12, "bold"),
                                  bg="#ffffff", fg="#2c3e50")
        self.total_lbl.pack(pady=(5,15))

        self.load_history()

    def add_expense(self):
        month = self.month_cb.get()
        cat   = self.cat_cb.get()
        item  = self.item_e.get().strip()
        price = self.price_e.get().strip()
        if not item or not price:
            return
        try:
            amt = float(price)
        except ValueError:
            messagebox.showerror("Invalid", "Price must be a number.")
            return

        with open(EXPENSE_CSV, 'a', newline='') as f:
            csv.writer(f).writerow([self.master.current_user, month, cat, item, amt])

        self.load_history()
        self.item_e.delete(0, tk.END)
        self.price_e.delete(0, tk.END)

    def load_history(self):
        self.listbox.delete(0, tk.END)
        month = self.month_cb.get()
        user  = getattr(self.master, 'current_user', None)
        total = 0.0

        with open(EXPENSE_CSV, 'r', newline='') as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                if len(row) >= 5 and row[0] == user and row[1] == month:
                    amt = float(row[4])
                    total += amt
                    self.listbox.insert(tk.END, f"{row[3]} ({row[2]}) – ₱{amt:,.2f}")

        self.total_lbl.config(text=f"Total for {month}: ₱{total:,.2f}")


# === Main Application ===
class ExpenseApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Everyday Expense Tracker")
        self.geometry("400x600")
        self.resizable(False, False)
        self.current_user = None

        # Create and grid all frames
        self.frames = {}
        for Page in (RegisterPage, LoginPage, ExpenseTrackerPage):
            frame = Page(self)
            self.frames[Page] = frame
            frame.place(relwidth=1, relheight=1)

        self.show_frame(RegisterPage)

    def show_frame(self, page_cls):
        self.frames[page_cls].tkraise()


if __name__ == "__main__":
    ExpenseApp().mainloop()



