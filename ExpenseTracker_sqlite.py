import os
import sqlite3
import tkinter as tk
from tkinter import messagebox
from tkinter import *
from tkinter import ttk
from datetime import datetime

# === SQLite Database Setup ===
DB_PATH = 'expense_tracker.db'

# Create the database and tables if they don't exist
if not os.path.exists(DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Create the Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    name TEXT,
                    email TEXT,
                    password TEXT)''')

    # Create the Expenses table
    c.execute('''CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item TEXT,
                    price INTEGER,
                    month TEXT)''')
    
    conn.commit()
    conn.close()
    print("Database and tables created successfully!")

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
        tk.Label(parent, text=label, bg="#ffffff", anchor="w", font=("Segoe UI", 9)).pack(fill="x", padx=40)
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

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (uname,))
        if c.fetchone():
            messagebox.showwarning("Exists", "Username already exists.")
            conn.close()
            return

        c.execute("INSERT INTO users (username, name, email, password) VALUES (?, ?, ?, ?)",
                  (uname, name, email, pwd))
        conn.commit()
        conn.close()

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

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (uname, pwd))
        user = c.fetchone()
        conn.close()

        if user:
            messagebox.showinfo("Login Success", f"Welcome, {user[1]}!")
            self.master.destroy()
            launch_expense_tracker()
        else:
            messagebox.showerror("Failed", "Invalid username or password.")

# === Main App ===
class AuthApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Login/Register System")
        self.geometry("400x600")
        self.resizable(False, False)

        self.frames = {}
        for Page in (RegisterPage, LoginPage):
            frame = Page(self)
            self.frames[Page] = frame
            frame.place(relwidth=1, relheight=1)

        self.show_frame(RegisterPage)

    def show_frame(self, page_cls):
        self.frames[page_cls].tkraise()

# === Expense Tracker with Scrollable Month Cards ===
def launch_expense_tracker():
    root = Tk()
    root.title("Expense Tracker")
    root.geometry("1300x800")  # Increased height for better visibility
    root.config(bg="white")

    monthly_expenses = {
        "January": [], "February": [], "March": [], "April": [], "May": [], "June": [],
        "July": [], "August": [], "September": [], "October": [], "November": [], "December": []
    }

    entry_frame = Frame(root, bg="white")
    entry_frame.pack(pady=10)

    Label(entry_frame, text="Item:", font=("Arial", 12), bg="white").grid(row=0, column=0, padx=5, pady=5)
    item_entry = Entry(entry_frame, font=("Arial", 12), width=25)
    item_entry.grid(row=0, column=1, padx=5, pady=5)

    Label(entry_frame, text="Price:", font=("Arial", 12), bg="white").grid(row=0, column=2, padx=5, pady=5)
    price_entry = Entry(entry_frame, font=("Arial", 12), width=10)
    price_entry.grid(row=0, column=3, padx=5, pady=5)

    Label(entry_frame, text="Month:", font=("Arial", 12), bg="white").grid(row=0, column=4, padx=5, pady=5)
    months = list(monthly_expenses.keys())
    selected_month = StringVar()
    selected_month.set(months[datetime.now().month - 1])
    OptionMenu(entry_frame, selected_month, *months).grid(row=0, column=5, padx=5, pady=5)

    def add_expense():
        item = item_entry.get()
        price = price_entry.get()
        month = selected_month.get()
        if item and price.isdigit():
            monthly_expenses[month].append((item, int(price)))
            update_month_card(month)
            item_entry.delete(0, END)
            price_entry.delete(0, END)

    def clear_expenses(month):
        monthly_expenses[month] = []
        update_month_card(month)

    def update_month_card(month):
        card = month_cards[month]
        for widget in card.winfo_children():
            widget.destroy()
        
        # Create a canvas for scrolling
        canvas = Canvas(card, bg="white", highlightthickness=0)
        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        
        # Add a scrollbar
        scrollbar = Scrollbar(card, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Create a frame inside the canvas
        inner_frame = Frame(canvas, bg="white")
        canvas.create_window((0, 0), window=inner_frame, anchor="nw")
        
        # Add content to the inner frame
        Label(inner_frame, text=month, font=("Arial", 14, "bold"), bg="white").pack(pady=5)
        
        total = 0
        for item, price in monthly_expenses[month]:
            Label(inner_frame, text=f"{item}: \u20b1{price}", font=("Arial", 10), bg="white").pack(anchor="w")
            total += price
        
        # Add total and clear button at the bottom
        Label(inner_frame, text=f"Total: \u20b1{total}", font=("Arial", 12, "bold"), bg="white", fg="green").pack(pady=5)
        Button(inner_frame, text="Clear", command=lambda m=month: clear_expenses(m), 
               font=("Arial", 10, "bold"), fg="black").pack(pady=5)
        
        # Update the inner frame's size and the canvas scroll region
        inner_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))
        
        # Bind mousewheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

    Button(entry_frame, text="Add Expense", command=add_expense, font=("Arial", 12, "bold"), bg="#90CAF9").grid(row=0, column=6, padx=5, pady=5)

    # Create a Canvas for the main window scrolling
    main_canvas = Canvas(root, bg="white")
    main_canvas.pack(side=LEFT, fill=BOTH, expand=True)

    # Add a scrollbar to the main canvas
    main_scrollbar = Scrollbar(root, orient="vertical", command=main_canvas.yview)
    main_scrollbar.pack(side=RIGHT, fill=Y)

    main_canvas.configure(yscrollcommand=main_scrollbar.set)

    # Create a frame to hold the month cards inside the main canvas
    cards_frame = Frame(main_canvas, bg="white")
    main_canvas.create_window((0, 0), window=cards_frame, anchor="nw")

    month_cards = {}
    for i, month in enumerate(months):
        row = i // 4  # 4 columns per row
        col = i % 4   # 4 columns
        
        card = Frame(cards_frame, bd=2, relief="solid", bg="white", width=300, height=300)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        card.grid_propagate(False)
        month_cards[month] = card
        update_month_card(month)

    # Configure grid weights for proper resizing
    for i in range(4):  # 4 columns
        cards_frame.grid_columnconfigure(i, weight=1)
    for i in range(3):  # 3 rows (12 months / 4 columns)
        cards_frame.grid_rowconfigure(i, weight=1)

    # Update the scrolling region of the main canvas
    cards_frame.update_idletasks()
    main_canvas.config(scrollregion=main_canvas.bbox("all"))

    # Bind mousewheel scrolling for the main canvas
    def _on_main_mousewheel(event):
        main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    main_canvas.bind_all("<MouseWheel>", _on_main_mousewheel)

    root.mainloop()

if __name__ == "__main__":
    AuthApp().mainloop()
