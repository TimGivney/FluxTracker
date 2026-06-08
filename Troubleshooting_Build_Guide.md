# FluxTracker v2.0 - Build & Troubleshooting Guide

## Prerequisites

Before building FluxTracker, ensure you have:

1. **Python 3.7 or later** installed on your system
   - Download from: https://www.python.org/downloads/
   - **Important**: Check "Add Python to PATH" during installation
   - Verify installation: Open Command Prompt and run `python --version`

2. **Required Files**
   - `main.py` - Application entry point
   - `ui.py` - User interface
   - `database.py` - Database management
   - `logo.png` - Application logo
   - `requirements.txt` - Python dependencies
   - `build.bat` - Build script

3. **Disk Space**
   - At least 500 MB free space for build process and virtual environment

## Build Steps

### Step 1: Extract the Build Kit
Unzip `FluxTracker_v2.0_BuildKit.zip` to a folder on your computer.

### Step 2: Open Command Prompt
1. Navigate to the extracted folder
2. Hold Shift and right-click in the folder
3. Select "Open Command Window Here" (or "Open PowerShell Window Here")

### Step 3: Run the Build Script
```bash
build.bat
```

The script will automatically:
1. Check for Python installation
2. Create a virtual environment
3. Install all required dependencies from `requirements.txt`
4. Build the standalone executable using PyInstaller
5. Verify the build was successful

### Step 4: Locate Your Executable
After successful build, your executable will be at:
```
dist/FluxTracker.exe
```

You can now:
- Run it directly from this location
- Copy it to any folder on your computer
- Create a shortcut for easy access
- Share it with others (it's completely standalone)

## What the Build Script Does

The `build.bat` script performs the following steps:

1. **Python Check**: Verifies Python is installed and in your PATH
2. **Virtual Environment**: Creates an isolated Python environment (`venv` folder)
3. **Dependency Installation**: Installs packages from `requirements.txt`:
   - `pyinstaller` - Converts Python to executable
   - `pillow` - Image processing for logo
   - `pandas` - Data handling for CSV import/export
   - `openpyxl` - Excel file support

4. **PyInstaller Build**: Packages everything into a single executable:
   - `--onefile` - Creates a single .exe file
   - `--windowed` - Removes console window
   - `--clean` - Cleans up old build artifacts
   - `--add-data "logo.png;."` - Includes the logo image

## Common Issues & Solutions

### Issue 1: "Python is not recognized"
**Error Message**: `'python' is not recognized as an internal or external command`

**Solutions**:
1. **Reinstall Python with PATH**
   - Uninstall Python completely
   - Download from https://www.python.org/downloads/
   - During installation, **check "Add Python to PATH"**
   - Restart your computer
   - Try building again

2. **Manually Add Python to PATH**
   - Find your Python installation folder (usually `C:\Users\YourName\AppData\Local\Programs\Python\Python311`)
   - Add this folder to your system PATH
   - Restart Command Prompt and try again

3. **Use Full Python Path**
   - Find your Python executable location
   - Run: `C:\path\to\python.exe -m PyInstaller --version`
   - If this works, Python is installed correctly but not in PATH

### Issue 2: "Failed to install dependencies"
**Error Message**: `ERROR: Failed to install dependencies from requirements.txt`

**Solutions**:
1. **Check Internet Connection**
   - Ensure you have a stable internet connection
   - Try running: `pip install pillow` to test connectivity

2. **Update pip**
   ```bash
   python -m pip install --upgrade pip
   ```

3. **Manual Installation**
   ```bash
   pip install pyinstaller pillow pandas openpyxl
   ```

4. **Use Alternative Package Index**
   ```bash
   pip install -r requirements.txt -i https://pypi.org/simple/
   ```

### Issue 3: "PyInstaller build failed"
**Error Message**: `ERROR: PyInstaller build failed`

**Solutions**:
1. **Delete Old Build Artifacts**
   - Delete the `build` folder
   - Delete the `dist` folder
   - Delete the `.spec` file
   - Run `build.bat` again

2. **Verify logo.png Exists**
   - Make sure `logo.png` is in the same folder as `build.bat`
   - If missing, add a placeholder image or comment out the `--add-data` line

3. **Check File Permissions**
   - Right-click the folder and select "Properties"
   - Ensure your user account has read/write permissions
   - Run Command Prompt as Administrator

4. **Insufficient Disk Space**
   - Ensure you have at least 500 MB free space
   - Delete temporary files if needed

### Issue 4: "Executable not found in dist folder"
**Error Message**: `Build finished but executable was not found in 'dist' folder`

**Solutions**:
1. Check the `build` folder for any error messages
2. Look for a `.spec` file - this indicates PyInstaller ran
3. Try running PyInstaller manually:
   ```bash
   python -m PyInstaller --noconfirm --onefile --windowed --clean --add-data "logo.png;." --name "FluxTracker" main.py
   ```

4. Check for antivirus interference - some antivirus software blocks executable creation

### Issue 5: "Multiple instances running" error
**Error Message**: `Someone else is using FluxTracker. Please try again soon.`

**Solution**:
1. Close all running instances of FluxTracker
2. Delete the `app.lock` file in the same directory as the executable
3. Run FluxTracker again

### Issue 6: "Application crashes on startup"
**Error Message**: `CRITICAL BOOT ERROR` or application closes immediately

**Solutions**:
1. **Check Database Integrity**
   - Delete `fluxtracker.db` (it will be recreated)
   - Run the application again

2. **Check Attachments Folder**
   - Ensure the `attachments` folder has proper permissions
   - Try deleting and letting the app recreate it

3. **Run as Administrator**
   - Right-click `FluxTracker.exe`
   - Select "Run as Administrator"

4. **Check Windows Compatibility**
   - Right-click `FluxTracker.exe`
   - Select "Properties"
   - Go to "Compatibility" tab
   - Try "Run this program in compatibility mode for:" and select Windows 10

## File Structure After Build

```
fluxtracker/
├── build.bat                          # Build script
├── requirements.txt                   # Python dependencies
├── main.py                            # Application entry point
├── ui.py                              # User interface
├── database.py                        # Database management
├── logo.png                           # Application logo
├── README.md                          # Documentation
├── Troubleshooting_Build_Guide.md    # This file
├── venv/                              # Virtual environment (created by build.bat)
├── build/                             # Build artifacts (created by PyInstaller)
├── dist/                              # Output folder
│   └── FluxTracker.exe               # Your standalone executable
└── FluxTracker.spec                   # PyInstaller specification file
```

## Verifying Your Build

After building, verify everything works:

1. **Test the Executable**
   - Double-click `dist/FluxTracker.exe`
   - Application should launch without errors

2. **Test Core Features**
   - Add a new part
   - Add a new engineering change
   - Attach a file
   - Search for a change
   - Export to CSV

3. **Check Data Persistence**
   - Close the application
   - Reopen it
   - Verify your data is still there

## Distributing Your Build

Once built successfully, you can:

1. **Share the Single Executable**
   - Copy `dist/FluxTracker.exe` to any location
   - Send it to colleagues
   - No installation required - it just works!

2. **Create an Installer** (Optional)
   - Use tools like NSIS or Inno Setup
   - Create a professional installer package
   - Include the executable and documentation

3. **Create a Portable Version**
   - Copy `FluxTracker.exe` to a USB drive
   - Run it from anywhere without installation

## Advanced Build Options

### Custom Executable Name
Edit `build.bat` and change:
```batch
--name "FluxTracker"
```
to your desired name.

### Include Additional Files
To include other files in the executable, modify the `--add-data` parameter:
```batch
--add-data "file1.txt;." --add-data "file2.png;."
```

### Reduce Executable Size
Add `--onedir` instead of `--onefile` to create a folder with separate files (smaller individual file size but requires all files to be distributed together).

## Support & Further Help

If you encounter issues not covered here:

1. **Check the Error Message Carefully** - It often contains useful information
2. **Review the Build Log** - Check the console output for details
3. **Verify Prerequisites** - Ensure Python is installed correctly
4. **Try a Clean Build** - Delete `build`, `dist`, and `.spec` files and rebuild
5. **Update Python** - Ensure you have the latest Python version

---

**FluxTracker v2.0** - Engineering Change Control System
*Built with Python, PyInstaller, and ❤️*
