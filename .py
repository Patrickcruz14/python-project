import tkinter as tk
from tkinter import *
from tkinter import ttk

class AuthApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Expense Tracker")
        self.geometry("900x600")
        
        # Create monthly expenses dictionary
        self.monthly_expenses = {
            "January": [], "February": [], "March": [], 
            "April": [], "May": [], "June": [],
            "July": [], "August": [], "September": [],
            "October": [], "November": [], "December": []
        }
        
        self.current_active_card = None
        self.create_widgets()

    def create_widgets(self):
        # Main container
        main_frame = Frame(self)
        main_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)

        # Title
        Label(main_frame, text="Monthly Expense Tracker", font=("Arial", 16, "bold")).pack(pady=(0, 20))

        # Scrollable area for month cards
        canvas = Canvas(main_frame, bg="#f0f0f0", highlightthickness=0)
        scrollbar = Scrollbar(main_frame, orient=VERTICAL, command=canvas.yview)
        scrollable_frame = Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

        # Create month cards
        def create_month_card(month, row, col):
            # Card frame (clickable)
            card = Frame(scrollable_frame, bd=2, relief="solid", bg="white", padx=10, pady=10)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            
            # Make entire card clickable by adding a transparent clickable frame
            clickable_area = Frame(card, bg="white")
            clickable_area.pack(fill=BOTH, expand=True)
            
            # Month header
            header = Frame(clickable_area, bg="white")
            header.pack(fill=X)
            Label(header, text=month, font=("Arial", 14, "bold"), bg="white").pack(side=LEFT)
            
            # Add click event to expand/collapse
            def toggle_card(event):
                if self.current_active_card and self.current_active_card != card:
                    # Collapse previous card
                    for widget in self.current_active_card.winfo_children()[1:]:
                        widget.pack_forget()
                    self.current_active_card.config(height=50)
                
                if len(card.winfo_children()) > 1 and card.winfo_children()[1].winfo_ismapped():
                    # Collapse current card
                    for widget in card.winfo_children()[1:]:
                        widget.pack_forget()
                    card.config(height=50)
                    self.current_active_card = None
                else:
                    # Expand current card
                    create_card_content(card, month)
                    card.config(height=300)
                    self.current_active_card = card

            clickable_area.bind("<Button-1>", toggle_card)
            card.clickable_area = clickable_area  # Store reference

            # Initial content
            create_card_content(card, month)
            
            # Initially collapse all cards except first
            if month != "January":
                for widget in card.winfo_children()[1:]:
                    widget.pack_forget()
                card.config(height=50)
            else:
                self.current_active_card = card
                card.config(height=300)

            return card

        def create_card_content(card, month):
            # Expense list frame
            list_frame = Frame(card, bg="white")
            list_frame.pack(fill=BOTH, expand=True, pady=(10, 0))

            # Scrollable area for expenses
            list_canvas = Canvas(list_frame, bg="white", height=150, highlightthickness=0)
            list_scrollbar = Scrollbar(list_frame, orient=VERTICAL, command=list_canvas.yview)
            list_inner_frame = Frame(list_canvas, bg="white")

            list_inner_frame.bind(
                "<Configure>",
                lambda e: list_canvas.configure(scrollregion=list_canvas.bbox("all"))
            )

            list_canvas.create_window((0, 0), window=list_inner_frame, anchor="nw")
            list_canvas.configure(yscrollcommand=list_scrollbar.set)

            list_canvas.pack(side=LEFT, fill=BOTH, expand=True)
            list_scrollbar.pack(side=RIGHT, fill=Y)

            # Entry frame
            entry_frame = Frame(card, bg="white")
            entry_frame.pack(fill=X, pady=(10, 0))

            Label(entry_frame, text="Item:", bg="white").pack(side=LEFT)
            item_entry = Entry(entry_frame, width=20)
            item_entry.pack(side=LEFT, padx=5)

            Label(entry_frame, text="Price:", bg="white").pack(side=LEFT)
            price_entry = Entry(entry_frame, width=10)
            price_entry.pack(side=LEFT, padx=5)

            def add_expense():
                item = item_entry.get()
                price = price_entry.get()
                if item and price.isdigit():
                    self.monthly_expenses[month].append((item, int(price)))
                    update_expense_list(list_inner_frame, month)
                    item_entry.delete(0, END)
                    price_entry.delete(0, END)

            Button(entry_frame, text="Add Expense", command=add_expense, bg="#90CAF9").pack(side=LEFT, padx=5)

            # Total and clear button
            bottom_frame = Frame(card, bg="white")
            bottom_frame.pack(fill=X, pady=(10, 0))

            def clear_expenses():
                self.monthly_expenses[month] = []
                update_expense_list(list_inner_frame, month)

            Button(bottom_frame, text="Clear All", command=clear_expenses, bg="#FFCDD2").pack(side=RIGHT)
            
            # Initial update
            update_expense_list(list_inner_frame, month)

        def update_expense_list(frame, month):
            # Clear existing widgets
            for widget in frame.winfo_children():
                widget.destroy()

            # Add expenses
            total = 0
            for item, price in self.monthly_expenses[month]:
                Label(frame, text=f"{item}: P{price}", bg="white", anchor="w").pack(fill=X)
                total += price

            # Add total
            Label(frame, text=f"Total: P{total}", bg="white", font=("Arial", 10, "bold"), fg="green").pack(fill=X, pady=(5,0))

        # Create 3-column grid of month cards
        for i, month in enumerate(self.monthly_expenses.keys()):
            row = i // 3
            col = i % 3
            create_month_card(month, row, col)

        # Configure grid weights
        for i in range(3):
            scrollable_frame.grid_columnconfigure(i, weight=1)

if __name__ == "__main__":
    app = AuthApp()
    app.mainloop()
