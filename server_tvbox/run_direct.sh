#!/data/data/com.termux/files/usr/bin/sh
export PREFIX=/data/data/com.termux/files/usr
export HOME=/data/data/com.termux/files/home
export PATH=$PREFIX/bin:$PATH
export PYTHONUNBUFFERED=1
DIR=$HOME/exegate_ups_monitor

su 0 chmod -R 777 /dev/bus/usb >/dev/null 2>&1
su 0 sh -c 'echo -n 4-1:1.0 > /sys/bus/usb/drivers/usbhid/unbind' >/dev/null 2>&1

cd "$DIR" || exit 1
exec python3 server.py
