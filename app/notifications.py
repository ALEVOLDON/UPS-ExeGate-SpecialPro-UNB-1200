"""Native Windows Toast Notification manager for UPS Monitor."""

import sys
import os
import logging
import subprocess


def send_notification(title: str, message: str, app_name: str = "ExeGate UPS Monitor") -> None:
    """Send a native OS toast notification safely."""
    logging.info(f"NOTIFICATION: [{title}] {message}")

    if sys.platform == "win32":
        try:
            # Clean quotes for PowerShell
            safe_title = title.replace('"', '`"').replace("'", "''")
            safe_msg = message.replace('"', '`"').replace("'", "''")

            ps_script = f'''
            [void] [System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms")
            $notify = New-Object System.Windows.Forms.NotifyIcon
            $notify.Icon = [System.Drawing.SystemIcons]::Information
            $notify.BalloonTipTitle = "{safe_title}"
            $notify.BalloonTipText = "{safe_msg}"
            $notify.Visible = $true
            $notify.ShowBalloonTip(5000)
            Start-Sleep -s 6
            $notify.Dispose()
            '''
            
            subprocess.Popen(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
                creationflags=0x08000000  # CREATE_NO_WINDOW
            )
            return
        except Exception as e:
            logging.error(f"PowerShell notification error: {e}")

    # Fallback for non-Windows platforms
    try:
        from plyer import notification
        notification.notify(
            title=title,
            message=message,
            app_name=app_name,
            timeout=6
        )
    except Exception as e:
        logging.debug(f"Plyer notification fallback error: {e}")
