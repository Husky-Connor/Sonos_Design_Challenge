import soco
import time
import RPi.GPIO as GPIO
default_song = 'http://ia801402.us.archive.org/20/items/TenD2005-07-16.flac16/TenD2005-07-16t10Wonderboy.mp3'

def find_zone(zone_name):
    for zone in soco.discover():
        if zone.player_name == zone_name:
            return zone

def volume_fade(a_zone, another_zone, seconds):
    max_vol = a_zone.volume
    sleep_time = seconds / max_vol
    for i in range(max_vol):
        a_zone.volume = max_vol - i - 1
        another_zone.volume = i + 1
        time.sleep(sleep_time)

def full_stop():
    for zone in soco.discover(): zone.pause()

def listen(pin0, pin1):
    if GPIO.input(pin0) and not GPIO.input(pin1):
        while GPIO.input(pin0):
            if GPIO.input(pin1):
                return 1
    elif GPIO.input(pin1) and not GPIO.input(pin0):
        while GPIO.input(pin1):
            if GPIO.input(pin0):
                return 0

def main(song_name, volume):
    # GPIO Setup
    GPIO.setmode(GPIO.BOARD)
    pin0 = 11
    pin1 = 12
    GPIO.setup(pin0, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(pin1, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Constantly search for zones until more than 1 is found
    zones = []
    count = 0
    while len(zones) < 2:
        count += 1
        print('Attempt #%d'%count)
        if soco.discover(): zones = list(soco.discover())
    
    # Initialize Volume
    zones[0].volume = volume
    for zone in zones[1:]:
        zone.volume = 0
    
    # Send play command to all
    for zone in zones:
        zone.play_uri(song_name)
    
    # Initialize state
        # 0 = Initial Room
        # 1 = Other Room
    current_state = 0
    
    # Loop Forever
    while True:
        # Listen for a room event
        room_event = listen(pin0, pin1)
        # If the room event indicates a different position, update state and print
        if (room_event != current_state) and (room_event is not None):
            # Fade between zones
            volume_fade(zones[current_state], zones[room_event], 1)
            # Update current state
            current_state = room_event

main(default_song, 30)