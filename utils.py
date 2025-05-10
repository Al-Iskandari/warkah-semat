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


def auto_list(text):
    lines = text.split("\n")
    if len(lines) < 2:
        return text

    new_lines = []
    last_item_type = None  # Keep track of the last item type: 'hyphen' or 'number'
    last_number = 0

    for line in lines:
        # line = line.strip()  # remove leading/trailing whitespace for better detection
        if line.startswith("- "):
            new_lines.append("- " + line[2:])  # Keep only the content after '- '
            last_item_type = 'hyphen'
        elif line and line[0].isdigit() and ". " in line:
            try:
                number = int(line.split(". ")[0])
                new_lines.append(line)
                last_item_type = 'number'
                last_number = number

            except ValueError:
                new_lines.append(line)  # If not a valid number, keep the original line
                last_item_type = None

        else:
            if not line:  # Only suggest on empty lines
                if last_item_type == 'hyphen':
                    new_lines.append("- ")  # Suggest next hyphen item
                elif last_item_type == 'number':
                    new_lines.append(f"{last_number + 1}. ")  # Suggest next number
                    last_number += 1
                else:
                    new_lines.append("")  # Keep empty line
            else:
                new_lines.append(line)  # Keep non-empty, non-list lines
                last_item_type = None  # Stop suggesting if a non-list item is entered

    return "\n".join(new_lines)


def strikethrough_completed_tasks(text):
    """
    Strikethroughs lines in the text that are considered completed tasks (list items).
    """
    lines = text.split("\n")
    new_lines = []
    for line in lines:
        if line.startswith("- ") or (line and line[0].isdigit() and ". " in line):
            new_lines.append("~~" + line + "~~")
        else:
            new_lines.append(line)
    return "\n".join(new_lines)