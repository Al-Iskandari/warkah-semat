# Warkah Semat(Sticky Notes) Application

## Overview

Warkah Semat is another term of Sticky Notes in Malay. It is a desktop application built with Python and the PySide6 library. It allows users to create, manage, and organize notes with features such as prioritization, timers, and cloud synchronization with Google Sheets that is prepared for next development on Web Platform. The application utilizes a SQLite database for local storage and provides a system tray icon for easy access.

## Project Structure

```
.
├── .gitignore          # Specifies intentionally untracked files that Git should ignore
├── dashboard.py        # Implements the dashboard window for managing notes
├── database.py         # Defines the database models and connection
├── main.py             # Main application entry point
├── note_window.py      # Implements the note window
├── requirements.txt    # Lists the project dependencies
├── utils.py            # Utility functions, including Google Sheets sync and text formatting
└── resources/          # Directory for images and the SQLite database
    ├── checked.png
    ├── minimize.png
    ├── notes.db
    ├── sticky-note.png
    └── trash.png
```

## Features

-   **Note Creation and Management:** Create, edit, and delete sticky notes.
-   **Prioritization:** Assign priorities (Low, Medium, High, Critical) to notes.
-   **Timers:** Set timers for notes with notifications.
-   **Persistence:** Notes are saved to a local SQLite database.
-   **Dashboard:** A dashboard to view and manage all notes.
-   **System Tray Integration:** Application runs in the system tray for quick access.
-   **Google Sheets Sync:** (Placeholder) Functionality to sync notes with Google Sheets.
-   **Auto-List Formatting:** Automatic list formatting in notes.
-   **Strikethrough Completed Tasks:** Strikethrough completed tasks in notes.

## Technologies Used

-   **Python:** Programming language.
-   **PySide6:** GUI framework for creating the user interface.
-   **SQLAlchemy:** ORM for database management.
-   **SQLite:** Database for local storage.

## Dependencies

-   greenlet==3.1.1
-   PySide6==6.2.4
-   shiboken6==6.2.4
-   sqlalchemy==2.0.40
-   typing-extensions==4.13.2

## Setup and Installation

