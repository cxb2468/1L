@echo off
TITLE Flask Japan Vocabulary App
cd /d D:\1L\deployment
echo Starting Flask Japan Vocabulary Application...
echo Access the application at http://localhost:8000
call venv\Scripts\activate
set FLASK_CONFIG=production
set SECRET_KEY=your-production-secret-key-here
set DATABASE_URL=japan.db
waitress-serve --host=0.0.0.0 --port=8000 wsgi:application
pause