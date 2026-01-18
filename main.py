import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'Aegis'))

from Aegis.src.ui.dashboard import DashboardWindow

if __name__ == "__main__":
    try:
        app = DashboardWindow()
        app.protocol("WM_DELETE_WINDOW", app.on_closing)
        app.mainloop()
    except KeyboardInterrupt:
        print("Exiting...")
        sys.exit(0)
