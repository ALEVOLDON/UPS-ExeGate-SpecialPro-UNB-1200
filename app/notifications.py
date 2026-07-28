"""Native Windows Toast Notification manager for UPS Monitor."""

import sys
import os
import logging
import subprocess

try:
    from plyer import notification
    HAS_PLYER = True
except Exception:
    HAS_PLYER = False


def send_notification(title: str, message: str, app_name: str = "ExeGate UPS Monitor") -> None:
    """Send a native OS toast notification safely."""
    logging.info(f"NOTIFICATION: [{title}] {message}")

    # Method 1: Plyer
    if HAS_PLYER:
        try:
            notification.notify(
                title=title,
                message=message,
                app_name=app_name,
                timeout=6
            )
            return
        except Exception as e:
            logging.debug(f"Plyer notification error: {e}")

    # Method 2: Windows PowerShell fallback
    if sys.platform == "win32":
        try:
            ps_script = f'''
            [void] [System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms")
            $notify = New-Object System.Windows.Forms.NotifyIcon
            $notify.Icon = [System.Drawing.SystemIcons]::Information
            $notify.BalloonTipTitle = "{title.replace('"', '`"')}"
            $notify.BalloonTipText = "{message.replace('"', '`"')}"
            $notify.Visible = $true
            $notify.ShowBalloonTip(5000)
            Start-Sleep -s 6
            $notify.Dispose()
            '''
            subprocess.Popen(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        except Exception as e:
            logging.debug(f"PowerShell notification fallback error: {e}")
