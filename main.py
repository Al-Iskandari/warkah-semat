import sys

from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QMenu,
    QSystemTrayIcon,
)

from note_window import NoteWindow
from database import Note, session  # Import Note and session
from dashboard import Dashboard  # Import the Dashboard
from utils import sync_to_google_sheets  # Import the sync function


app = QApplication(sys.argv)

# Store references to the NoteWindow objects in this, keyed by id.
active_notewindows = {}


def create_notewindow():
    note = NoteWindow(active_notewindows=active_notewindows)
    note.show()


# Load notes from the database on startup
notes = session.query(Note).all()
for note in notes:
    note_window = NoteWindow(note=note, active_notewindows=active_notewindows)
    note_window.show()


# Create the icon
icon = QIcon("sticky-note.png")

# Create the tray
tray = QSystemTrayIcon()
tray.setIcon(icon)
tray.setVisible(True)


def handle_tray_click(reason):
    # If the tray is left-clicked, create a new note.
    if reason == QSystemTrayIcon.ActivationReason.Trigger:
        create_notewindow()


tray.activated.connect(handle_tray_click)

# Don't automatically close app when the last window is closed.
app.setQuitOnLastWindowClosed(False)

# Create the menu
menu = QMenu()
# Add the Add Note option to the menu.
add_note_action = QAction("Add note")
add_note_action.triggered.connect(create_notewindow)
menu.addAction(add_note_action)

# Add Dashboard option
dashboard_action = QAction("Dashboard")
dashboard_action.triggered.connect(lambda: Dashboard(active_notewindows).show())
menu.addAction(dashboard_action)


# Add Sync to Google Sheets option
sync_action = QAction("Sync to Google Sheets")
sync_action.triggered.connect(lambda: sync_to_google_sheets(active_notewindows))
menu.addAction(sync_action)


# Add a Quit option to the menu.
quit_action = QAction("Quit")
quit_action.triggered.connect(app.quit)
menu.addAction(quit_action)
# Add the menu to the tray
tray.setContextMenu(menu)


app.exec()