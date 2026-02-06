# Troubleshooting Guide

## Common Issues and Solutions

### 1. "Fatal error in launcher" Error

**Error Message:**
```
Fatal error in launcher: Unable to create process using '"D:\1L\deployment\venv\Scripts\python.exe"  "D:\deployment\venv\Scripts\pip.exe" install -r requirements_windows.txt'
```

**Cause:** This error typically occurs when:
- The Python installation used to create the virtual environment is no longer available or has been moved
- There's a path mismatch in the virtual environment
- The virtual environment was created with a different Python version

**Solutions:**

1. **Recreate the virtual environment:**
   ```cmd
   cd D:\1L\deployment
   rmdir /s venv
   python -m venv venv
   D:\1L\deployment\venv\Scripts\activate
   pip install -r requirements_windows.txt
   ```

2. **Use python -m pip instead of pip directly:**
   ```cmd
   cd D:\1L\deployment
   D:\1L\deployment\venv\Scripts\activate
   python -m pip install -r requirements_windows.txt
   ```

3. **Use full paths:**
   ```cmd
   D:\1L\deployment\venv\Scripts\python.exe -m pip install -r D:\1L\deployment\requirements_windows.txt
   ```

### 2. "python is not recognized" Error

**Cause:** Python is not installed or not in the system PATH.

**Solution:**
1. Install Python 3.8 or higher from https://www.python.org/downloads/
2. During installation, make sure to check "Add Python to PATH"
3. Restart your command prompt

### 3. "Module not found" Errors

**Cause:** Missing dependencies or incorrect virtual environment.

**Solution:**
1. Make sure you've activated the virtual environment:
   ```cmd
   D:\1L\deployment\venv\Scripts\activate
   ```
2. Install dependencies:
   ```cmd
   pip install -r requirements_windows.txt
   ```

### 4. Port Already in Use

**Cause:** Another application is using port 8000.

**Solution:**
1. Change the port in the start script:
   ```cmd
   waitress-serve --host=0.0.0.0 --port=8001 wsgi:application
   ```
2. Or stop the application using the port:
   ```cmd
   netstat -ano | findstr :8000
   taskkill /PID <PID_NUMBER> /F
   ```

### 5. Database Issues

**Symptoms:** Application starts but data is missing or errors occur when accessing data.

**Solution:**
1. Check if japan.db exists in the deployment directory
2. If not, the application will create it automatically from japan.xlsx on first run
3. Ensure japan.xlsx is present in the deployment directory

### 6. Permission Issues

**Symptoms:** Access denied errors when starting the application.

**Solution:**
1. Run the command prompt as Administrator
2. Or change the host binding to localhost only:
   ```cmd
   waitress-serve --host=127.0.0.1 --port=8000 wsgi:application
   ```

## Diagnostic Commands

### Check Python Version
```cmd
python --version
```

### Check Pip Version
```cmd
pip --version
```

### List Installed Packages
```cmd
pip list
```

### Check Virtual Environment
```cmd
where python
echo %VIRTUAL_ENV%
```

### Check Port Usage
```cmd
netstat -ano | findstr :8000
```

## For Developers

If you continue to have issues:

1. **Clean Installation:**
   - Delete the entire deployment directory
   - Recreate it from the original source
   - Follow the setup steps from scratch

2. **Check File Integrity:**
   - Ensure all files are copied correctly
   - Check that there are no path issues in the files
   - Verify that japan.xlsx is present

3. **Environment Variables:**
   - Make sure FLASK_CONFIG is set to "production"
   - Check that SECRET_KEY is set to a secure value