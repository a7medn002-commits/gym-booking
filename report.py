import json
from threading import Thread
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


def write_report(bookings):
    try:
        with open("bookings_report.txt", "w", encoding="utf-8") as report:
            report.write("Gym Bookings Report\n")
            report.write(f"Total bookings: {len(bookings)}\n\n")

            for booking in bookings:
                report.write(
                    f"#{booking['id']} | {booking['customer_name']} | "
                    f"{booking['booking_date']} {booking['start_hour']:02d}:00 | "
                    f"{booking['duration_hours']} hour(s) | "
                    f"Ends at {booking['end_at']}\n"
                )
    except OSError as error:
        print(f"Could not save the report: {error}")
        return

    print("Report saved to bookings_report.txt.")


def main():
    try:
        with urlopen("http://127.0.0.1:5050/bookings", timeout=5) as response:
            bookings = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        print(f"Server returned error {error.code}.")
        return
    except (URLError, TimeoutError):
        print("Cannot connect to the booking server.")
        return
    except ValueError:
        print("The server returned invalid data.")
        return

    worker = Thread(target=write_report, args=(bookings,))
    worker.start()
    worker.join()


if __name__ == "__main__":
    main()