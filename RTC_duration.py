import machine
import utime

rtc = machine.RTC()
led = machine.Pin("LED", machine.Pin.OUT)

latest_remaining_time = None  # Initialize variable to hold the latest remaining time

def calculate_remaining_time(duration_seconds):
    # Get the current time from RTC
    current_time = rtc.datetime()

    # Calculate duration in minutes and hours
    duration_minutes, duration_seconds = divmod(duration_seconds, 60)
    duration_hours, duration_minutes = divmod(duration_minutes, 60)

    # Calculate the end time by adding duration to the current time
    end_time_seconds = current_time[6] + duration_seconds
    extra_minutes, end_time_seconds = divmod(end_time_seconds, 60)

    end_time_minutes = current_time[5] + duration_minutes + extra_minutes
    extra_hours, end_time_minutes = divmod(end_time_minutes, 60)

    end_time_hours = current_time[4] + duration_hours + extra_hours

    # Limit seconds and minutes to 60
    if end_time_seconds >= 60:
        end_time_seconds %= 60
        end_time_minutes += 1

    if end_time_minutes >= 60:
        end_time_minutes %= 60
        end_time_hours += 1

    end_time = (
        current_time[0],  # Year
        current_time[1],  # Month
        current_time[2],  # Day
        current_time[3],  # Weekday
        end_time_hours,   # Hours
        end_time_minutes, # Minutes
        end_time_seconds, # Seconds
        current_time[7]   # Subseconds
    )

    return end_time

def get_remaining_time(end_time):
    # Get the current time from RTC
    current_time = rtc.datetime()

    # Calculate the remaining time by finding the difference between end time and current time
    remaining_hours = end_time[4] - current_time[4]
    remaining_minutes = end_time[5] - current_time[5]
    remaining_seconds = end_time[6] - current_time[6]

    # Handle rollover when seconds < 0
    if remaining_seconds < 0:
        remaining_seconds += 60
        remaining_minutes -= 1

    # Handle rollover when minutes < 0
    if remaining_minutes < 0:
        remaining_minutes += 60
        remaining_hours -= 1

    # Handle rollover when hours < 0 or 24
    if remaining_hours < 0 or remaining_hours == 24:
        remaining_hours %= 24

    if remaining_hours == 0 and remaining_minutes == 0 and remaining_seconds == 0:
        return "Time's up!"

    # Convert excess seconds to minutes and update remaining seconds
    if remaining_seconds >= 60:
        remaining_minutes += remaining_seconds // 60
        remaining_seconds %= 60

    # Convert excess minutes to hours and update remaining minutes
    if remaining_minutes >= 60:
        remaining_hours += remaining_minutes // 60
        remaining_minutes %= 60
        
    return f"{remaining_hours:02}:{remaining_minutes:02}:{remaining_seconds:02}"

# Example usage:
duration_input = int(input("Enter duration in seconds: "))
end_time = calculate_remaining_time(duration_input)

while True:
    remaining_time = get_remaining_time(end_time)
    print(f"Remaining time: {remaining_time} | current: {rtc.datetime()} | end: {end_time}")

    if remaining_time == "Time's up!":
        led.value(1)
        break

    utime.sleep(1)  # Delay for 1 second before re-checking remaining time

