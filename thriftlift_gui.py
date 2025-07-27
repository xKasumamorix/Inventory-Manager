import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import csv
import os
from datetime import datetime
from fpdf import FPDF

INVENTORY_FILE = "inventory.csv"

def initialize_inventory_file():
    try:
        with open(INVENTORY_FILE, "x", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Item Name", "Brand", "Category", "Size", "Purchase Price", "Sale Price", "Shipping Cost", "eBay Fee", "Profit", "Listed Date", "Sold Date", "Status"])
    except FileExistsError:
        pass # When file already exists

# Main App Window
root = tk.Tk()
# Theme colors
root.configure(bg="#e6f2fa") # Light Washy Blue background

default_font = ("Fira Code", 10)
label_font = ("Fira Code", 10, "bold")

style = ttk.Style()
style.theme_use("default")  

# Base button style
style.configure("TButton",
    font=default_font,
    padding=6,
    relief="flat",
    background="#cce7f6",
    foreground="#003366")

# Primary button style (for important actions like "Save")
style.configure("Primary.TButton",
    font=label_font,
    padding=6,
    background="#007acc",
    foreground="white")
style.map("Primary.TButton",
    background=[("active", "#005a99")])

# Success button style (e.g., Save Changes)
style.configure("Success.TButton",
    font=label_font,
    padding=6,
    background="#28a745",
    foreground="white")
style.map("Success.TButton",
    background=[("active", "#1e7e34")])

root.title("ThriftLift Inventory Manager")
root.geometry("600x600")

# Labels and Entry fields
labels = ["Item Name", "Brand", "Category", "Size", "Purchase Price"]
entries = {}

for label in labels:
    tk.Label(root, text=label).pack(pady=(10, 0))
    entry = tk.Entry(root)
    entry.pack()
    entries[label] = entry

# Save item listing
def save_item():
    item_data = []
    item_id = int(datetime.now().timestamp()) # Unique ID
    item_data.append(item_id)
    
    for label in labels:
        value = entries[label].get()
        item_data.append(value)
    
    # Format the purchase price as a currency value ($)    
    try:
        price_value = float(item_data[5])
        item_data[5] = f"${price_value:.2f}"
    except (ValueError, IndexError):
        item_data[5] = "$0.00"
    
    # Fill empty fields for sale price, shipping cost, profit, etc.
    item_data.extend(["", "", "", ""]) # Fields for profit, sale price, etc.
    item_data.append(datetime.now().strftime("%Y-%m-%d")) # Listed date
    item_data.append("")  # Sold date
    item_data.append("Listed") # Status
    
    # Save to CSV file
    with open(INVENTORY_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(item_data)
    
    messagebox.showinfo("Saved", "Item added to inventory!")
    
    for entry in entries.values():
        entry.delete(0, tk.END) # Clear fields
    
    tree.insert("", "end", values=item_data)

def open_edit_window():
    edit_window = tk.Toplevel(root)
    edit_window.title("Edit Existing Item")
    edit_window.geometry("400x600")
    edit_window.configure(bg="#e6f2fa")  # Light washy blue

    tk.Label(edit_window, text="Enter Item ID to Edit:", font=label_font, bg="#e6f2fa").pack(pady=(10, 0))
    id_entry = tk.Entry(edit_window, font=default_font)
    id_entry.pack()

    fields = {}
    edit_labels = ["Item Name", "Brand", "Category", "Size", "Purchase Price", "Sale Price", "Shipping Cost", "eBay Fee", "Status"]

    for label in edit_labels:
        tk.Label(edit_window, text=label, font=label_font, bg="#e6f2fa").pack(pady=(8, 0))
        entry = tk.Entry(edit_window, font=default_font)
        entry.pack()
        fields[label] = entry

    def load_item():
        item_id = id_entry.get()
        found = False
        with open(INVENTORY_FILE, "r", newline="") as f:
            reader = csv.reader(f)
            header = next(reader)
            for row in reader:
                if str(row[0]) == item_id:
                    for idx, label in enumerate(edit_labels):
                        if idx + 1 < len(row):
                            fields[label].delete(0, tk.END)
                            fields[label].insert(0, row[idx + 1])
                    found = True
                    break
        if not found:
            messagebox.showerror("Not Found", "Item ID not found.")

    def save_changes():
        item_id = id_entry.get()
        updated_rows = []
        found = False

        with open(INVENTORY_FILE, "r", newline="") as f:
            reader = csv.reader(f)
            header = next(reader)
            for row in reader:
                if str(row[0]) == item_id:
                    for idx, label in enumerate(edit_labels):
                        if idx + 1 < len(row):
                            row[idx + 1] = fields[label].get()
                    row[9] = datetime.now().strftime("%Y-%m-%d")  # update listed date
                    found = True
                updated_rows.append(row)

        if found:
            with open(INVENTORY_FILE, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(header)
                writer.writerows(updated_rows)
            messagebox.showinfo("Updated", "Item updated successfully!")
        else:
            messagebox.showerror("Error", "Item not found.")

    tk.Button(edit_window, text="Load Item", command=load_item, bg="#007acc", fg="white", font=label_font).pack(pady=10)   # Look up an item
    tk.Button(edit_window, text="Save Changes", command=save_changes, bg="#28a745", fg="white", font=label_font).pack()    # Save listing changes

# Edit listing button 
ttk.Button(root, text="Edit Existing Item", command=open_edit_window, style="TButton").pack(pady=5)

# Save item button
save_button = ttk.Button(root, text="Add to Inventory", command=save_item, style="Primary.TButton").pack(pady=10) 

# Marking as Sold 
tk.Label(root, text="Sale Price").pack()
sale_price_entry = tk.Entry(root)
sale_price_entry.pack()

tk.Label(root, text="Shipping Cost").pack()
shipping_cost_entry = tk.Entry(root)
shipping_cost_entry.pack()

tk.Label(root, text="eBay Fee").pack()
ebay_fee_entry = tk.Entry(root)
ebay_fee_entry.pack()

def mark_as_sold():
    selected = tree.focus()
    if not selected:
        messagebox.showwarning("No Selection", "Please select an item in the table.")
        return

    sale_price = sale_price_entry.get()
    shipping_cost = shipping_cost_entry.get()
    ebay_fee = ebay_fee_entry.get()

    if not sale_price or not shipping_cost or not ebay_fee:
        messagebox.showerror("Missing Info", "Please enter sale price and shipping cost.")
        return

    try:
        sale_price = float(sale_price)
        shipping_cost = float(shipping_cost)
        ebay_fee = float(ebay_fee)
    except ValueError:
        messagebox.showerror("Invalid Input", "Sale price, shipping cost, and eBay fee must be numbers.")
        return

    item = tree.item(selected)
    item_values = item["values"]
    
    try:
        purchase_price = float(item_values[5])
    except ValueError:
        messagebox.showerror("Invalid Data", "Could not convert purchase price to a number.")
        return
    profit = sale_price - purchase_price - shipping_cost - ebay_fee
    sold_date = datetime.now().strftime("%Y-%m-%d")

    # Update the treeview
    updated_item = list(item_values)
    updated_item[6] = f"${sale_price:.2f}"      # Sale Price
    updated_item[7] = f"${shipping_cost:.2f}"   # Shipping Cost
    updated_item[8] = f"${ebay_fee:.2f}"        # eBay Fee 
    updated_item[9] = f"${profit:.2f}"          # Profit
    updated_item[11] = sold_date                # Sold Date
    updated_item[12] = "Sold"                   # Status        

    tree.item(selected, values=updated_item)

    # Update the CSV
    update_csv_from_treeview()

    # Clear fields
    sale_price_entry.delete(0, tk.END)
    shipping_cost_entry.delete(0, tk.END)
    ebay_fee_entry.delete(0, tk.END)

    messagebox.showinfo("Updated", "Item marked as sold!")

def update_csv_from_treeview():
    with open(INVENTORY_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Iterm Name", "Brand", "Category", "Size", "Purchase Price", "Sale Price", "Shipping Cost", "eBay Fee", "Profit", "Listed Date", "Sold Date", "Status"])
        for row_id in tree.get_children():
            row = tree.item(row_id)["values"]
            writer.writerow(row)   

# Mark as Sold button
mark_sold_btn = ttk.Button(root, text="Mark as Sold", command=mark_as_sold, style="Success.TButton")
mark_sold_btn.pack(pady=10)

# Inventory Display Table
tree = ttk.Treeview(root, columns=("ID", "Item Name", "Brand", "Category", "Size", "Purchase Price", "Sale Price", "Shipping Cost", "eBay Fee", "Profit", "Listed Date", "Sold Date", "Status"), show="headings")

for col in tree["columns"]:
    tree.heading(col, text=col)
    tree.column(col, width=100, anchor="center")

tree.pack(expand=True, fill="both", padx=10, pady=10)

# Optional scrollbar
scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
tree.configure(yscroll=scrollbar.set)
scrollbar.pack(side="right", fill="y")

# Category Filter
filter_label = ttk.Label(root, text="Filter by Category:", font=label_font)
filter_label.pack(pady=(20, 5))

category_var = tk.StringVar()
category_combo = ttk.Combobox(root, textvariable=category_var, state="readonly")
category_combo.pack()

def update_category_options():
    categories = set()
    if os.path.exists(INVENTORY_FILE):
        with open(INVENTORY_FILE, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                categories.add(row["Category"])
    category_combo["values"] = sorted(categories)

update_category_options()

def filter_by_category():
    selected_category = category_var.get()
    if not selected_category:
        messagebox.showinfo("Info", "Please select a category to filter.")
        return

    filtered_items = []
    with open(INVENTORY_FILE, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["Category"] == selected_category:
                filtered_items.append(row)

    top = tk.Toplevel(root)
    top.title(f"Items in Category: {selected_category}")
    for item in filtered_items:
        item_str = f"{item['Item Name']} - {item['Brand']} - {item['Size']} - {item['Purchase Price']}"
        tk.Label(top, text=item_str).pack()

filter_btn = ttk.Button(root, text="Apply Filter", command=filter_by_category, style="Success.TButton")
filter_btn.pack(pady=10)

# Export to PDF
def export_to_pdf():
    if not os.path.exists(INVENTORY_FILE):
        messagebox.showerror("Error", "No inventory file found to export.")
        return

    pdf = FPDF(orientation='L', unit='mm', format='A4') 
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15) 

    pdf.set_font("Arial", size=14)
    pdf.cell(0, 10, txt="ThriftLift Gear Inventory Report", ln=True, align="C")
    pdf.ln(10)

    # Column headers for the PDF table
    headings = ["ID", "Item Name", "Brand", "Category", "Size", "P. Price", "S. Price", "Shipping", "eBay Fee", "Profit", "Listed Date", "Sold Date", "Status"]
    col_widths = [12, 35, 25, 25, 12, 20, 20, 20, 20, 20, 25, 25, 20]

    # Print table headers
    pdf.set_font("Arial", 'B', 8) 
    for i, heading in enumerate(headings):
        pdf.cell(col_widths[i], 7, heading, 1, 0, 'C')
    pdf.ln()

    # Print table rows
    pdf.set_font("Arial", size=7) 
    with open(INVENTORY_FILE, newline="") as f:
        reader = csv.reader(f)
        next(reader) # Skip the CSV header row
        for row in reader:
            # Ensure row has enough elements to avoid IndexError, pad with empty strings if needed
            while len(row) < len(headings):
                row.append("")
            for i, item in enumerate(row):
                pdf.cell(col_widths[i], 7, str(item), 1, 0, 'L')
            pdf.ln()

    output_file = "inventory_report.pdf"
    pdf.output(output_file)
    messagebox.showinfo("Exported", f"Inventory exported to {output_file} successfully!")

export_btn = ttk.Button(root, text="Export to PDF", command=export_to_pdf, style="Success.TButton")
export_btn.pack(pady=10)


# Initialize CSV if it doesn't exist already
initialize_inventory_file()

# Load inventory from file at startup
if os.path.exists(INVENTORY_FILE):
    with open(INVENTORY_FILE, "r", newline="") as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        for row in reader:
            tree.insert("", "end", values=row)

# Run GUI loop
root.mainloop()