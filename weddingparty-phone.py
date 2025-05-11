# read GPIO

# when GPIO trigger
    # set LED GPIO high
    # start recording
    # save file on timeout
# when no trigger
    # stop recording
    # save file

import RPi.GPIO as GPIO
import datetime
import pyaudio
import wave
import uuid
import time

# GPIO setup
GPIO.setmode(GPIO.BCM)  # Use BCM numbering
GPIO.setup(18, GPIO.OUT)  # Set pin 17 as input with pull-up resistor
GPIO.setup(2, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Set pin 17 as input with pull-up resistor

# PyAudio setup
chunk = 2048  # Record in chunks of 1024 samples
sample_format = pyaudio.paInt16  # 16 bits per sample
channels = 1
fs = 48000 #44100  # Record at 44100 samples per second
seconds = 10
wav_filename = f"{str(datetime.datetime.now()).replace(' ', 'T').replace(':','-').replace('.','-')}_{str(uuid.uuid4())[:16].upper()}.wav" #"output.wav"






def control_led(pickup_state):
    if pickup_state:
        GPIO.output(18,GPIO.HIGH)
    else:
        GPIO.output(18,GPIO.LOW)


def get_state():
    pickup_state = False
    input_state = GPIO.input(2)
    if input_state == GPIO.HIGH:
        print(f"[info] PICKUP - state: {pickup_state}")
        pickup_state = True
    else:
        pickup_state = False
        print(f"[info] PLACEBACK - state: {pickup_state}")
    return pickup_state



def record_input():
    p = pyaudio.PyAudio()  # Create an interface to PortAudio

    print('Recording')

    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=chunk,
                    input=True)

    frames = []  # Initialize array to store frames

    # Store data in chunks for 3 seconds
    for i in range(0, int(fs / chunk * seconds)):
        data = stream.read(chunk)
        frames.append(data)

    # Stop and close the stream 
    stream.stop_stream()
    stream.close()
    # Terminate the PortAudio interface
    p.terminate()

    print('Finished recording')
    # save_recording(frames, p)
    wf = wave.open(wav_filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()



def save_recording(frames, p):
    # Save the recorded data as a WAV file
    wf = wave.open(wav_filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()





try:
    while True:
        state = get_state()
        control_led(state)

        if state:
            record_input()

        time.sleep(0.5)  # Check every half second
except KeyboardInterrupt:
    print("Exiting...")
    GPIO.cleanup()
