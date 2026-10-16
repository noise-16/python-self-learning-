

import time

import schedule
from plyer import notification

APP_NAME = "Health Reminder"
TOAST_TIMEOUT = 5            # seconds the notification stays on screen


PRODUCTION = False
HYDRATION_INTERVAL = 45 if PRODUCTION else 10
POSTURE_INTERVAL = 20 if PRODUCTION else 20


def send_break_alert(title, message):
    
    try:
        notification.notify(
            title=title,
            message=message,
            app_name=APP_NAME,
            timeout=TOAST_TIMEOUT,
        )
    except Exception as err:
      
        print(f"[!] Could not show notification ({err}). Message was: {title} - {message}")
    else:
        print(f"[{time.strftime('%H:%M:%S')}] Sent: {title}")


def hydration_alert():
    send_break_alert("Hydration Alert", "Time to drink a glass of water!")


def posture_check():
    send_break_alert("Posture Check", "Sit up straight, relax your shoulders and rest your eyes.")


def configure_schedule():
    
    if PRODUCTION:
        schedule.every(HYDRATION_INTERVAL).minutes.do(hydration_alert)
        schedule.every(POSTURE_INTERVAL).minutes.do(posture_check)
    else:
        schedule.every(HYDRATION_INTERVAL).seconds.do(hydration_alert)
        schedule.every(POSTURE_INTERVAL).seconds.do(posture_check)


def main():
    configure_schedule()
    unit = "minutes" if PRODUCTION else "seconds"
    print("Health reminder started.")
    print(f"  Hydration Alert : every {HYDRATION_INTERVAL} {unit}")
    print(f"  Posture Check   : every {POSTURE_INTERVAL} {unit}")
    print("Press Ctrl+C to stop.\n")

    try:
        while True:
            schedule.run_pending()   # run any job whose time has come
            time.sleep(1)            # check again in one second (keeps CPU use low)
    except KeyboardInterrupt:
        print("\nReminder stopped. Stay healthy, see you next time!")


if __name__ == "__main__":
    main()