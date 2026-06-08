import tkinter as tk
from tkinter import messagebox
import os
import sys
import time
import socket
from database import DatabaseManager
from ui import EngineeringChangeTrackerApp, SplashScreen

def main():
    # Initial Tkinter setup for Splash Screen
    root = tk.Tk()
    root.withdraw() # Hide the main root window initially
    
    # Show Splash Screen immediately
    splash_root = tk.Toplevel(root)
    splash = SplashScreen(splash_root)
    splash_root.update()

    # Multi-user access control using a lock file
    # For NAS environments, we use a lock file containing: PID, Hostname, Timestamp
    splash.update_status("Checking NAS lock file...")
    exe_dir = os.path.dirname(os.path.abspath(sys.executable if hasattr(sys, 'frozen') else __file__))
    lock_file = os.path.join(exe_dir, "app.lock")
    hostname = socket.gethostname()
    
    def create_lock():
        try:
            with open(lock_file, "w") as f:
                # Format: PID, Hostname, Time
                f.write(f"{os.getpid()},{hostname},{time.strftime('%Y-%m-%d %H:%M:%S')}")
        except Exception as e:
            print(f"Could not create lock file: {e}")

    if os.path.exists(lock_file):
        try:
            with open(lock_file, "r") as f:
                content = f.read().strip().split(',')
                if len(content) >= 2:
                    lock_pid = content[0]
                    lock_host = content[1]
                    lock_time = content[2] if len(content) > 2 else "Unknown"
                    
                    # If it's the SAME host, we can check if the PID is still alive
                    if lock_host == hostname:
                        import psutil
                        if not psutil.pid_exists(int(lock_pid)):
                            # Stale lock on current machine - safe to remove
                            os.remove(lock_file)
                            create_lock()
                        else:
                            raise Exception(f"Already running on this PC (PID: {lock_pid})")
                    else:
                        # Running on a DIFFERENT host on the NAS
                        raise Exception(f"Currently in use by user on workstation: {lock_host}\nStarted at: {lock_time}")
        except Exception as e:
            if "Currently in use" in str(e) or "Already running" in str(e):
                splash_root.destroy()
                # v2.10: Added "Force Unlock" option
                msg = f"FluxTracker is locked.\n\n{str(e)}\n\n"
                msg += "If you are CERTAIN no one else is using it, click YES to force unlock.\n"
                msg += "Otherwise, please wait for them to finish."
                
                if messagebox.askyesno("Access Denied", msg):
                    try:
                        if os.path.exists(lock_file):
                            os.remove(lock_file)
                        # Re-run the splash and continue
                        root.destroy()
                        return main()
                    except Exception as fe:
                        messagebox.showerror("Error", f"Could not force unlock: {fe}")
                        sys.exit(0)
                else:
                    root.destroy()
                    sys.exit(0)
            else:
                # If file is unreadable or corrupted, try to overwrite it
                create_lock()
    else:
        create_lock()

    try:
        # Determine the base path for assets (PyInstaller compatibility)
        splash.update_status("Loading system resources...")
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")
            
        db_path = os.path.join(exe_dir, "fluxtracker.db")
        
        # Initialize the database manager
        splash.update_status("Connecting to NAS database...")
        db_manager = DatabaseManager(db_path)
        
        # Initialize the UI
        splash.update_status("Building command interface...")
        app = EngineeringChangeTrackerApp(root, db_manager)
        
        def final_cleanup():
            # v2.10: More robust lock clearing
            if os.path.exists(lock_file):
                try:
                    # Only remove if it's OUR lock (check PID)
                    with open(lock_file, "r") as f:
                        curr_content = f.read().split(',')
                        if curr_content[0] == str(os.getpid()):
                            f.close() # Ensure file is closed before removal
                            os.remove(lock_file)
                except Exception as e:
                    print(f"Cleanup error: {e}")
            root.destroy()

        def on_closing():
            # v2.8: Trigger cinematic HAL logout ONLY if HAL was activated
            if hasattr(app, 'hal_active') and app.hal_active:
                app.perform_logout_sequence(final_cleanup)
            else:
                final_cleanup()
            
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Give user a moment to see the completed splash
        splash.update_status("System Ready.")
        root.after(800, splash_root.destroy)
        root.after(850, root.deiconify) # Show the main window
        
        root.mainloop()
        
    except Exception as e:
        if os.path.exists(lock_file):
            try:
                os.remove(lock_file)
            except:
                pass
        splash_root.destroy()
        error_msg = f"CRITICAL BOOT ERROR:\n\n{str(e)}\n\nTraceback:\n"
        import traceback
        error_msg += traceback.format_exc()
        
        try:
            temp_root = tk.Tk()
            temp_root.withdraw()
            messagebox.showerror("FluxTracker Failure", error_msg)
            temp_root.destroy()
        except:
            print(error_msg)
        sys.exit(1)

if __name__ == "__main__":
    main()
