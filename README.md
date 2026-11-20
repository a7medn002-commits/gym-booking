# Gym Booking System

This desktop app manages gym bookings. Users can add, view, edit, and delete
bookings. The server prevents overlapping time slots and calculates the end time.

## Setup and Run

Open PowerShell in the `gym-booking` folder. Use Python with Tkinter installed.

1. Install Flask.

   ```powershell
   py -m pip install -r requirements.txt
   ```

2. Start the server.

   ```powershell
   py server.py
   ```

   Flask runs on port 5050. The server creates the SQLite database and
   the `bookings` table when needed.

3. Open a second terminal in the same folder and start the client.

   ```powershell
   py client.py
   ```

4. To generate a text report, run this command while the server is running.

   ```powershell
   py report.py
   ```

   The report is saved as `bookings_report.txt`.

## Course Topics

| Topic | Where it appears |
| --- | --- |
| Classes and SQLite | `BookingStore` reads bookings in `server.py`. |
| Flask and HTTP | `get_bookings()` returns JSON. `add_booking()` handles `POST /bookings/add`. |
| Tkinter and collections | `load_bookings()` in `client.py` reads a list of bookings and displays their fields in a table. |
| Input checks and exceptions | `add_booking()` and `edit_booking()` in `server.py` validate input. `send_post()` in `client.py` handles request errors. |
| Threads and file handling | `main()` in `report.py` starts and joins one thread. `write_report()` writes the UTF-8 file. |

When the user clicks **Add**, the client sends a POST request to Flask.
Flask validates the input, checks for overlaps, and saves the booking in SQLite.
The client then refreshes the table.

## Test Results

| Test | Result |
| --- | --- |
| Load bookings in the Tkinter table | Passed |
| Reject a booking that overlaps an existing booking across midnight | Passed |
| Generate and open the text report | Passed |
| Run the project from a clean folder | Pending |
| Stop the server, restart it, and refresh the client | Pending |

