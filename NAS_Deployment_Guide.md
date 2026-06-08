# FluxTracker v2.8 - NAS Deployment & Permissions Guide

If your team is experiencing "Access Denied" or permission errors when running FluxTracker from your NAS, it is likely due to **Windows Security "Unblocking"** or **Folder Share Permissions**.

Follow these steps to ensure everyone on the team can access and run the software correctly.

---

## 1. Unblock the Files (The "Dave" Fix)
Windows automatically "blocks" executable files that are downloaded or copied from another computer as a security measure. This often prevents them from running on a shared network drive.

1.  **On your NAS folder**, right-click `FluxTracker_v2.8.exe`.
2.  Select **Properties**.
3.  At the bottom of the **General** tab, look for a section called **Security**.
4.  Check the box that says **Unblock**, then click **Apply** or **OK**.
5.  *Repeat this for `database.py`, `ui.py`, and `main.py` if you are running the source directly.*

---

## 2. Set Folder Permissions
For the single-instance locking (`app.lock`) and the database (`fluxtracker.db`) to work, every user needs **Modify** access to the folder.

1.  Right-click the **FluxTracker folder** on your NAS.
2.  Select **Properties** > **Security** tab.
3.  Click **Edit...** and ensure the "Users" group (or the specific team members) has the following checked:
    - [x] Read & execute
    - [x] List folder contents
    - [x] Read
    - [x] **Write** (Crucial for the `.db` and `.lock` files)
    - [x] **Modify** (Crucial for deleting the `.lock` file on exit)
4.  Click **Apply** to all subfolders and files.

---

## 3. Map the Drive (Recommended)
Running software via a **UNC path** (e.g., `\\NAS\Share\FluxTracker`) can sometimes cause issues with Python's path handling.

- It is highly recommended that all team members **Map the Network Drive** to a consistent letter (e.g., `Z:\`).
- Everyone should then run the app from `Z:\FluxTracker\FluxTracker_v2.8.exe`.

---

## 4. Troubleshooting "Access Denied"
- **The .lock File:** If the app crashed, a file named `app.lock` might still be in the folder. If a user doesn't have "Delete" permissions, they won't be able to clear it. Ensure everyone has **Modify** permissions.
- **The Database:** If the database is "Read-Only," users can see changes but cannot save new ones. Check that `fluxtracker.db` is NOT marked as Read-Only in its properties.

---

### 💡 Pro Tip: The "Team-Ready" Build
When you run the `build.bat` script, it creates a clean `dist` folder. When you copy this to the NAS, **always copy the entire folder contents**, not just the `.exe`, to ensure all dependencies are present.
