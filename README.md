# Gym Booking System

- **Course:** Advanced Programming 462 – Individual Project (Client Server Project)
- **Student:** Ahmed Mohammed Noman
- **Student ID:** 451000323
- **GitHub:** https://github.com/a7medn002-commits/gym-booking


## What the application does

Gym Booking System is a desktop application that helps gym staff manage session
bookings in one window. Staff can **add, view, edit and delete** bookings. Each
booking has an ID, a customer name, a date, a start hour and a duration. The
server calculates the end time automatically.

**Overlap prevention.** Flask rejects a new or edited booking if
its time overlaps with an existing booking, including bookings that cross
midnight. The window shows the message "This time is already booked."

The Tkinter window in `client.py` sends HTTP requests to Flask in `server.py`. Flask reads and writes bookings in SQLite and sends JSON replies to the window.

## Files

| File | Purpose |
| --- | --- |
| `server.py` | Flask back end, SQLite table setup, `BookingStore` class, all routes |
| `client.py` | Tkinter window (inputs, buttons, table, messages) |
| `report.py` | Report helper that uses one thread to write `bookings_report.txt` |
| `requirements.txt` | Python packages (Flask) |
| `bookings.db` | SQLite database (created automatically if missing) |

## Setup and run

Open PowerShell in the project folder. Python 3 with Tkinter is required.

1. Install the packages.

   ```powershell
   py -m pip install -r requirements.txt
   ```

2. Start Flask. `server.py` creates the `bookings` table if it is missing and keeps existing records.

   ```powershell
   py server.py
   ```

   Flask runs on `http://127.0.0.1:5050`.

3. Open a second terminal in the same folder and start Tkinter.

   ```powershell
   py client.py
   ```

4. With Flask running, open PowerShell in the project folder to create the text report.

   ```powershell
   py report.py
   ```

   The report is saved as `bookings_report.txt`.

## Course topics and where they appear

| Topic | Evidence in the project |
| --- | --- |
| Python and collections | `list_bookings()` in `server.py` builds a list of booking dictionaries. `load_bookings()` in `client.py` loops through that list to display the bookings. |
| Exceptions | `add_booking()` and `edit_booking()` in `server.py` catch `ValueError` and `OverflowError`. `send_post()` and `load_bookings()` in `client.py` catch `HTTPError`, `URLError` and `TimeoutError`. `write_report()` in `report.py` catches `OSError`. |
| Classes | `BookingStore` in `server.py` holds the database name and reads bookings with `list_bookings()`. |
| SQLite | `server.py`: `CREATE TABLE IF NOT EXISTS` (setup), `SELECT` in `list_bookings()`, `INSERT` in `add_booking()`, `UPDATE` in `edit_booking()`, `DELETE` in `delete_booking()`. Queries that take input values use `?` placeholders. Each request opens and closes a database connection. Write requests commit their changes. |
| Threads and files | `main()` in `report.py` creates one `Thread`, calls `start()` and then `join()`. `write_report()` opens the UTF-8 file with `with` and handles `OSError`. |
| Tkinter | `client.py`: labels, entry boxes, **Add / Edit / Delete / Refresh** buttons, a `Treeview` table, a status label, an edit window, and message boxes (including a confirmation before deletion). |
| Client and server | See the example below. |
| Flask | `server.py`: `GET /bookings`, `POST /bookings/add`, `POST /bookings/<id>/edit`, `POST /bookings/<id>/delete`. Input checks return JSON with status 400, an unknown ID returns 404, and an overlap returns 409. |

### One HTTP request and its reply (Add)

1. The user fills the form and clicks **Add**. `add_booking()` in `client.py` collects the values.
2. `send_post()` encodes them with `urlencode` and sends `POST http://127.0.0.1:5050/bookings/add` with `urlopen(..., timeout=5)`.
3. `add_booking()` in `server.py` reads `request.form`, checks the values and the overlap, and saves the booking in SQLite.
4. Flask sends a JSON reply with a `message` field.
5. Tkinter reads the reply with `json.loads`, reloads the list with `GET /bookings` and shows the message.

## Error handling

| Case | Flask reply | What the window shows |
| --- | --- | --- |
| Missing or invalid input | 400 + JSON message | The message in an error box |
| Unknown booking ID | 404 + JSON message | "Booking not found." |
| Overlapping time | 409 + JSON message | "This time is already booked." |
| Flask stopped or timeout | – | "Cannot connect to the booking server." |

After the connection error, start Flask again and click **Refresh** in the open window.

## Test results

| Test | Result |
| --- | --- |
| Load bookings in the Tkinter table | Passed |
| Reject a booking that overlaps an existing booking across midnight | Passed |
| Generate and open the text report | Passed |
| Start Flask and Tkinter from a clean folder and show a booking | Passed |
| Add, view, edit and delete from a clean folder and check the affected record | Passed |
| Restart Flask and confirm that saved bookings remain | Passed |
| Restart both Flask and Tkinter and check that saved bookings remain | Passed |
| Missing input, invalid value and empty list show clear messages |Passed |
| Unknown ID (delete a record in one window, then edit it in another) | Passed |
| Stop Flask, check the connection error, restart Flask and refresh the open Tkinter window | Passed |

## Credits

- Python standard library, Flask and Tkinter (documentation examples).
- Course instructions and example code from Dr. Majed Hariri.
- I used AI tools for code examples, explanations and debugging help.
