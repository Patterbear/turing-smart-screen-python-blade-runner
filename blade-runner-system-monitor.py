import os
import signal
import time
from psutil import cpu_percent, cpu_freq, virtual_memory
from WinTmp import CPU_Temp
from pyadl import ADLManager
from shutil import disk_usage

from library.lcd.lcd_comm_rev_a import LcdCommRevA, Orientation
from library.log import logger

COM_PORT = "AUTO"

stop = False

if __name__ == "__main__":

    def sighandler(signum, frame):
        global stop
        stop = True


    # Set the signal handlers, to send a complete frame to the LCD before exit
    signal.signal(signal.SIGINT, sighandler)
    signal.signal(signal.SIGTERM, sighandler)
    is_posix = os.name == 'posix'
    if is_posix:
        signal.signal(signal.SIGQUIT, sighandler)

    # Build your LcdComm object based on the HW revision
    lcd_comm = None
    logger.info("Selected Hardware Revision A (Turing Smart Screen 3.5\" & UsbPCMonitor 3.5\"/5\")")
    lcd_comm = LcdCommRevA(com_port=COM_PORT, display_width=320, display_height=480)

    # Reset screen in case it was in an unstable state (screen is also cleared)
    lcd_comm.Reset()

    # Send initialization commands
    lcd_comm.InitializeComm()

    # Set brightness in % (warning: revision A display can get hot at high brightness! Keep value at 50% max for rev. A)
    lcd_comm.SetBrightness(level=10)

    # Set backplate RGB LED color (for supported HW only)
    lcd_comm.SetBackplateLedColor(led_color=(0, 0, 0))

    # Set orientation (screen starts in Portrait)
    lcd_comm.SetOrientation(orientation=Orientation.REVERSE_LANDSCAPE)

    # Define background picture
    background = f"res/backgrounds/br_system_monitor.png"

    # Display sample picture
    logger.debug("setting background picture")
    start = time.perf_counter()
    lcd_comm.DisplayBitmap(background)
    end = time.perf_counter()
    logger.debug(f"background picture set (took {end - start:.3f} s)")

    while not stop:
        start = time.perf_counter()

        # CPU usage
        cpu_usage = cpu_percent()
        lcd_comm.DisplayText(f" {cpu_usage}% ", 55, 115,
                             font="blade-runner/blade-runner.ttf",
                             font_size=20,
                             font_color=(255, 255, 255),
                             background_color=(0, 0, 0))

        # Clock speed
        cpu_speed = round(cpu_freq().current / 1000, 2)
        lcd_comm.DisplayText(f" {cpu_speed} GHz ", 180, 115,
                             font="blade-runner/blade-runner.ttf",
                             font_size=20,
                             font_color=(255, 255, 255),
                             background_color=(0, 0, 0))

        # CPU temperature
        cpu_temp = round(CPU_Temp(), 1)
        lcd_comm.DisplayText(f" {cpu_temp} °C ", 335, 115,
                             font="blade-runner/blade-runner.ttf",
                             font_size=20,
                             font_color=(255, 255, 255),
                             background_color=(0, 0, 0))

        # RAM usage
        ram_usage = virtual_memory().percent
        lcd_comm.DisplayText(f" {ram_usage}% ", 45, 235,
                             font="blade-runner/blade-runner.ttf",
                             font_size=20,
                             font_color=(255, 255, 255),
                             background_color=(0, 0, 0))

        # GPU usage
        gpu_usage = ADLManager.getInstance().getDevices()[0].getCurrentUsage()
        lcd_comm.DisplayText(f" {gpu_usage}% ", 200, 235,
                             font="blade-runner/blade-runner.ttf",
                             font_size=20,
                             font_color=(255, 255, 255),
                             background_color=(0, 0, 0))

        # Storage
        storage = round((disk_usage("/").used  / disk_usage("/").total) * 100, 2)
        lcd_comm.DisplayText(f" {storage}% ", 345, 235,
                             font="blade-runner/blade-runner.ttf",
                             font_size=20,
                             font_color=(255, 255, 255),
                             background_color=(0, 0, 0))

        time.sleep(1)
        logger.debug(f"refresh done (took {end - start:.3f} s)")

    # Close serial connection at exit
    lcd_comm.closeSerial()
