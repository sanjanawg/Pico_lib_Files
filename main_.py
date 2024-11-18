import machine
import utime

rtc = machine.RTC()
led = machine.Pin("LED", machine.Pin.OUT)
button = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_DOWN)

latest_remaining_time = None  # Initialize variable to hold the latest remaining time

def calculate_remaining_time(duration_seconds, pause_duration):
    current_time = rtc.datetime()

    duration_minutes, duration_seconds = divmod(duration_seconds, 60)
    duration_hours, duration_minutes = divmod(duration_minutes, 60)

    # Adjust duration based on pause duration
    duration_seconds -= pause_duration
    if duration_seconds < 0:
        duration_seconds = 0

    end_time_seconds = current_time[6] + duration_seconds
    extra_minutes, end_time_seconds = divmod(end_time_seconds, 60)

    end_time_minutes = current_time[5] + duration_minutes + extra_minutes
    extra_hours, end_time_minutes = divmod(end_time_minutes, 60)

    end_time_hours = current_time[4] + duration_hours + extra_hours

    if end_time_seconds >= 60:
        end_time_seconds %= 60
        end_time_minutes += 1

    if end_time_minutes >= 60:
        end_time_minutes %= 60
        end_time_hours += 1

    end_time = (
        current_time[0],  
        current_time[1],  
        current_time[2],  
        current_time[3],  
        end_time_hours,   
        end_time_minutes, 
        end_time_seconds, 
        current_time[7]   
    )

    return end_time

def get_remaining_time(end_time, paused):
    current_time = rtc.datetime()

    if paused:
        return "Paused"

    remaining_hours = end_time[4] - current_time[4]
    remaining_minutes = end_time[5] - current_time[5]
    remaining_seconds = end_time[6] - current_time[6]

    if remaining_seconds < 0:
        remaining_seconds += 60
        remaining_minutes -= 1

    if remaining_minutes < 0:
        remaining_minutes += 60
        remaining_hours -= 1

    if remaining_hours < 0 or remaining_hours == 24:
        remaining_hours %= 24

    if remaining_hours == 0 and remaining_minutes == 0 and remaining_seconds == 0:
        return "Time's up!"

    if remaining_seconds >= 60:
        remaining_minutes += remaining_seconds // 60
        remaining_seconds %= 60

    if remaining_minutes >= 60:
        remaining_hours += remaining_minutes // 60
        remaining_minutes %= 60
        
    return f"{remaining_hours:02}:{remaining_minutes:02}:{remaining_seconds:02}"

def pause_resume(duration_input):
    end_time = calculate_remaining_time(duration_input, 0)

    pause_start_time = None
    paused = False
    pause_duration = 0

    while True:
        remaining_time = get_remaining_time(end_time, paused)
        print(f"Remaining time: {remaining_time} | current: {rtc.datetime()} | end: {end_time}")

        button_state = button.value()

        if button_state == 1:
            if not paused:
                pause_start_time = rtc.datetime()
                paused = True
                print("Paused")
                
                while button.value() == 1:  # Wait until button is released
                    utime.sleep(0.5)  # Small delay to avoid high CPU usage
            else:
                pause_end_time = rtc.datetime()
                paused = False
                pause_duration += (
                    (pause_end_time[4] - pause_start_time[4]) * 3600 +
                    (pause_end_time[5] - pause_start_time[5]) * 60 +
                    (pause_end_time[6] - pause_start_time[6])
                )
                end_time = calculate_remaining_time(duration_input, pause_duration)
                print("Resumed")
        
        if remaining_time == "Time's up!":
            if remaining_time == "Time's up!":
                led.value(1)
            break

        utime.sleep(0.5)  # Small delay to avoid high CPU usage

duration_input = int(input("Enter duration in seconds: "))
pause_resume(duration_input)
