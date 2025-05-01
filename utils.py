import csv

# Replace with your Google Apps Script Web App URL
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycb........................../exec"


def sync_to_google_sheets(active_notewindows):
    try:
        data = [
            [
                "ID",
                "X",
                "Y",
                "Text",
                "Priority",
                "Timer Enabled",
                "Timer Time",
            ]
        ]  # Header row
        for note_window_id, note_window in active_notewindows.items():
            note = note_window.note
            data.append(
                [
                    note.id,
                    note.x,
                    note.y,
                    note.text,
                    note.priority,
                    note.timer_enabled,
                    note.timer_time,
                ]
            )

        # Write data to CSV format
        csv_data = "\n".join([",".join(map(str, row)) for row in data])

        # Send the data to the shared link (this will likely not work directly)
        # Shared links are typically read-only.  You would need an API
        # that accepts CSV data to update the sheet.  This is a placeholder.
        # The following line will likely result in an error.
        # requests.post(SHARED_LINK_URL, data=csv_data)

        print(
            "Data prepared.  Direct update to shared link is not possible."
            "  You need an API to accept the CSV data."
        )

    except Exception as e:
        print(f"An error occurred: {e}")
