import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import csv
import os
from datetime import datetime
from fpdf import FPDF

INVENTORY_FILE = "inventory.csv"

# Initialize file

def initialize_inventory_file():
    try:
        with open(INVENTORY_FILE, "x", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Item Name", "Brand", "Category", "Size", "Purchase Price", "Sale Price", "Shipping Cost", "eBay Fee", "Profit", "Listed Date", "Sold Date", "Status"])
    except FileExistsError:
        pass

# GUI setup
root = tk.Tk()
root.title("Inventory Manager")
root.geometry("700x650")
root.configure(bg="#e6f2fa")

# Fonts and styles
label_font = ("Fira Code", 10, "bold")
default_font = ("Fira Code", 10)
style = ttk.Style()
style.theme_use("default")
style.configure("TButton", font=default_font, padding=6, relief="flat", background="#cce7f6", foreground="#003366")
style.configure("Primary.TButton", font=label_font, padding=6, background="#007acc", foreground="white")
style.map("Primary.TButton", background=[("active", "#005a99")])
style.configure("Success.TButton", font=label_font, padding=6, background="#28a745", foreground="white")
style.map("Success.TButton", background=[("active", "#1e7e34")])
style.configure("Delete.TButton", font=label_font, padding=6, background="#ff4d4d", foreground="white")
style.map("Delete.TButton", background=[("active", "#cc0000")])

# Input fields
labels = ["Item Name", "Brand", "Category", "Size", "Purchase Price", "Sale Price"]
entries = {}
for label in labels:
    tk.Label(root, text=label, font=label_font, bg="#e6f2fa").pack(pady=(5, 0))
    entry = tk.Entry(root, font=default_font)
    entry.pack()
    entries[label] = entry

# Treeview setup
tree = ttk.Treeview(root, columns=("ID", "Item Name", "Brand", "Category", "Size", "Purchase Price", "Sale Price", "Shipping Cost", "eBay Fee", "Profit", "Listed Date", "Sold Date", "Status"), show="headings")
for col in tree["columns"]:
    tree.heading(col, text=col)
    tree.column(col, width=100, anchor="center")
tree.pack(expand=True, fill="both", padx=10, pady=10)
scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
tree.configure(yscroll=scrollbar.set)
scrollbar.pack(side="right", fill="y")

# Save item
def save_item():
    item_data = []
    item_id = int(datetime.now().timestamp())
    item_data.append(item_id)
    for label in labels:
        value = entries[label].get()
        item_data.append(value)
    item_data.extend(["", "", "", datetime.now().strftime("%Y-%m-%d"), "", "Listed"])
    with open(INVENTORY_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(item_data)
    tree.insert("", "end", values=item_data)
    for entry in entries.values():
        entry.delete(0, tk.END)
    messagebox.showinfo("Saved", "Item added to inventory!")

# Update CSV

def update_csv_from_treeview():
    with open(INVENTORY_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Item Name", "Brand", "Category", "Size", "Purchase Price", "Sale Price", "Shipping Cost", "eBay Fee", "Profit", "Listed Date", "Sold Date", "Status"])
        for row_id in tree.get_children():
            writer.writerow(tree.item(row_id)["values"])

# Mark as sold

def mark_as_sold():
    selected = tree.focus()
    if not selected:
        messagebox.showwarning("No Selection", "Please select an item.")
        return
    item = tree.item(selected)
    item_values = list(item["values"])
    try:
        sale_price = float(item_values[6])
        purchase_price = float(item_values[5])
        shipping_cost = float(entries_shipping.get())
        ebay_fee = float(entries_fee.get())
    except:
        messagebox.showerror("Error", "Ensure all numeric fields are valid.")
        return
    profit = sale_price - purchase_price - shipping_cost - ebay_fee
    item_values[7] = f"{shipping_cost:.2f}"
    item_values[8] = f"{ebay_fee:.2f}"
    item_values[9] = f"${profit:.2f}"
    item_values[11] = datetime.now().strftime("%Y-%m-%d")
    item_values[12] = "Sold"
    tree.item(selected, values=item_values)
    update_csv_from_treeview()
    entries_shipping.delete(0, tk.END)
    entries_fee.delete(0, tk.END)
    messagebox.showinfo("Updated", "Item marked as sold.")

# Edit item

def open_edit_window():
    win = tk.Toplevel(root)
    win.title("Edit Item")
    win.geometry("400x600")
    win.configure(bg="#e6f2fa")
    tk.Label(win, text="Enter ID:", font=label_font, bg="#e6f2fa").pack()
    id_entry = tk.Entry(win)
    id_entry.pack()
    fields = {}
    editable = ["Item Name", "Brand", "Category", "Size", "Purchase Price", "Sale Price", "Status"]
    for label in editable:
        tk.Label(win, text=label, font=label_font, bg="#e6f2fa").pack()
        ent = tk.Entry(win)
        ent.pack()
        fields[label] = ent

    def load_item():
        item_id = id_entry.get()
        for row_id in tree.get_children():
            if str(tree.item(row_id)["values"][0]) == item_id:
                for i, label in enumerate(editable):
                    fields[label].delete(0, tk.END)
                    fields[label].insert(0, tree.item(row_id)["values"][i + 1])
                return
        messagebox.showerror("Not Found", "Item not found.")

    def save_changes():
        item_id = id_entry.get()
        for row_id in tree.get_children():
            values = list(tree.item(row_id)["values"])
            if str(values[0]) == item_id:
                for i, label in enumerate(editable):
                    values[i + 1] = fields[label].get()
                tree.item(row_id, values=values)
                update_csv_from_treeview()
                messagebox.showinfo("Updated", "Changes saved.")
                return
        messagebox.showerror("Error", "Item not found.")

    ttk.Button(win, text="Load", command=load_item, style="Primary.TButton").pack(pady=10)
    ttk.Button(win, text="Save Changes", command=save_changes, style="Success.TButton").pack()

# Delete sold listings

def delete_sold_items():
    for row_id in tree.get_children():
        if tree.item(row_id)["values"][12] == "Sold":
            tree.delete(row_id)
    update_csv_from_treeview()
    messagebox.showinfo("Deleted", "Sold listings deleted.")

# Extra entry fields
tk.Label(root, text="Shipping Cost", font=label_font, bg="#e6f2fa").pack()
entries_shipping = tk.Entry(root, font=default_font)
entries_shipping.pack()
tk.Label(root, text="eBay Fee", font=label_font, bg="#e6f2fa").pack()
entries_fee = tk.Entry(root, font=default_font)
entries_fee.pack()

# Buttons
ttk.Button(root, text="Add to Inventory", command=save_item, style="Primary.TButton").pack(pady=5)
ttk.Button(root, text="Edit Item", command=open_edit_window, style="TButton").pack(pady=5)
ttk.Button(root, text="Mark as Sold", command=mark_as_sold, style="Success.TButton").pack(pady=5)
ttk.Button(root, text="Delete Sold Items", command=delete_sold_items, style="Delete.TButton").pack(pady=10)

# Load inventory
initialize_inventory_file()
if os.path.exists(INVENTORY_FILE):
    with open(INVENTORY_FILE, newline="") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            tree.insert("", "end", values=row)

# Run loop
root.mainloop()
