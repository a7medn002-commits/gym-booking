import json
import tkinter as tk
from tkinter import messagebox, ttk
from urllib.parse import urlencode
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


def load_bookings():
    try:
        with urlopen("http://127.0.0.1:5050/bookings", timeout=5) as response:
            bookings = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        status.config(text=f"Server returned error {error.code}.")
        return
    except (URLError, TimeoutError):
        status.config(text="Cannot connect to the booking server.")
        return

    for row in table.get_children():
        table.delete(row)

    for booking in bookings:
        values = tuple(booking[field] for field in columns)
        table.insert("", "end", values=values)

    status.config(text=f"{len(bookings)} booking(s)" if bookings else "No bookings yet.")

def send_post(path, values):
    body = urlencode(values).encode("utf-8")

    try:
        with urlopen(
            f"http://127.0.0.1:5050{path}", data=body, timeout=5
        ) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        message = f"Server returned error {error.code}."
        with error:
            try:
                message = json.loads(error.read().decode("utf-8")).get("message", message)
            except ValueError:
                pass
        messagebox.showerror("Request failed", message)
    except (URLError, TimeoutError):
        messagebox.showerror("Connection error", "Cannot connect to the booking server.")

    return None


def add_booking():
    values = {field: entry.get().strip() for field, entry in entries.items()}
    result = send_post("/bookings/add", values)
    if result is None:
        return

    for entry in entries.values():
        entry.delete(0, tk.END)

    load_bookings()
    messagebox.showinfo("Booking added", result["message"])


def delete_booking():
    selected = table.selection()
    if len(selected) != 1:
        messagebox.showwarning("Select a booking", "Select one booking to delete.")
        return

    booking_id, name = table.item(selected[0], "values")[:2]
    if not messagebox.askyesno("Confirm deletion", f"Delete booking #{booking_id} for {name}?"):
        return

    result = send_post(f"/bookings/{booking_id}/delete", {})
    if result is None:
        return

    load_bookings()
    messagebox.showinfo("Booking deleted", result["message"])
    
def edit_booking():
    selected = table.selection()
    if len(selected) != 1:
        messagebox.showwarning("Select a booking", "Select one booking to edit.")
        return

    booking_id, name, date, start_hour, duration = table.item(
        selected[0], "values"
    )[:5]

    dialog = tk.Toplevel(window)
    dialog.title("Edit Booking")
    dialog.transient(window)

    ttk.Label(dialog, text=f"Booking #{booking_id} for {name}").grid(
        row=0, column=0, columnspan=2, padx=10, pady=10
    )

    current_values = {
        "booking_date": date,
        "start_hour": start_hour,
        "duration_hours": duration,
    }
    edit_entries = {}

    for row, (field, value) in enumerate(current_values.items(), start=1):
        ttk.Label(dialog, text=columns[field]).grid(row=row, column=0, padx=10, pady=4)
        entry = ttk.Entry(dialog)
        entry.insert(0, value)
        entry.grid(row=row, column=1, padx=10, pady=4)
        edit_entries[field] = entry

    def save_changes():
        values = {field: entry.get().strip() for field, entry in edit_entries.items()}
        result = send_post(f"/bookings/{booking_id}/edit", values)
        if result is None:
            return

        dialog.destroy()
        load_bookings()
        messagebox.showinfo("Booking updated", result["message"])

    ttk.Button(dialog, text="Save", command=save_changes).grid(
        row=4, column=0, columnspan=2, pady=10
    )    
window = tk.Tk()
window.title("Gym Bookings")

columns = {
    "id": "ID",
    "customer_name": "Name",
    "booking_date": "Date",
    "start_hour": "Start hour",
    "duration_hours": "Duration (hours)",
    "end_at": "End time",
}

form = ttk.Frame(window)
form.pack(padx=10, pady=10)

fields = ("customer_name", "booking_date", "start_hour", "duration_hours")
entries = {}

for column, field in enumerate(fields):
    ttk.Label(form, text=columns[field]).grid(row=0, column=column, padx=4)
    entry = ttk.Entry(form, width=16)
    entry.grid(row=1, column=column, padx=4)
    entries[field] = entry


ttk.Button(form, text="Add", command=add_booking).grid(row=1, column=4, padx=8)
ttk.Button(form, text="Delete", command=delete_booking).grid(row=1, column=5, padx=8)
ttk.Button(form, text="Edit", command=edit_booking).grid(row=1, column=6, padx=8)
table = ttk.Treeview(window, columns=tuple(columns), show="headings")
for field, title in columns.items():
    table.heading(field, text=title)
    table.column(field, width=130)
table.pack(fill="both", expand=True, padx=10, pady=10)

ttk.Button(window, text="Refresh", command=load_bookings).pack()
status = ttk.Label(window)
status.pack(pady=8)

window.after(0, load_bookings)
window.mainloop()