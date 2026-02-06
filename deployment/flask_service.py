import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import sys
import os
from waitress import serve
from app import app

class FlaskAppService(win32serviceutil.ServiceFramework):
    _svc_name_ = "FlaskJapanApp"
    _svc_display_name_ = "Flask Japan App Service"
    _svc_description_ = "Flask application for Japanese vocabulary database"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.running = True
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.running = False

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.main()

    def main(self):
        # Change to the deployment directory
        os.chdir(r"D:\1L\deployment")
        
        # Serve the app with waitress
        serve(app, host='0.0.0.0', port=8000)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(FlaskAppService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(FlaskAppService)