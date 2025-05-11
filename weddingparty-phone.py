import RPi.GPIO as GPIO
import datetime
import pyaudio
import wave
import uuid
import time
import os

# General var setup
DEBUG = False
pickup_state = False

REC_OUTPUT_FOLDER = "./audio/output/"
START_REC_AUDIOMESSAGE = './audio/src/leave-a-message.wav'
STOP_REC_AUDIOMESSAGE = './audio/src/end-of-recording.wav'

# GPIO setup
GPIO.setmode(GPIO.BCM)                              # Use BCM numbering
GPIO.setup(18, GPIO.OUT)                            # Set pin 18 as input with pull-up resistor
GPIO.setup(2, GPIO.IN, pull_up_down=GPIO.PUD_UP)    # Set pin 18 as input with pull-up resistor

# PyAudio setup
RECORD_CHUNK = 16384 #8192                          # Record in chunks of 1024 samples
SAMPLE_FORMAT = pyaudio.paInt16                     # 16 bits per sample
CHANNELS = 1
FS = 48000                                          # 44100  # Record at 48000 samples per second
TIMEOUT_SECONDS = 120                               # hard limit of 120 secs

def control_led(state):
    if state:
        GPIO.output(18, GPIO.HIGH)
    else:
        GPIO.output(18,GPIO.LOW)

def get_state():
    input_state = GPIO.input(2)
    if input_state == GPIO.HIGH:
        pickup_state = True
        if DEBUG:
            print(f"[info] PICKUP - state: {pickup_state}")
    else:
        pickup_state = False
        if DEBUG:  
            print(f"[info] PLACEBACK - state: {pickup_state}")
    return pickup_state
          
def play_message(play_filename):
    OUTPUT_CHUNK = 2048 #1024

    with wave.open(play_filename, 'rb') as wf:        
        p = pyaudio.PyAudio()                                               # Instantiate PyAudio and initialize PortAudio system resources (1)
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),  # Open stream (2)
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)

        while len(data := wf.readframes(OUTPUT_CHUNK)):                            # Play samples from the wave file (3)
            stream.write(data)

        stream.close()                                                      # Close stream (4)
        p.terminate()                                                       # Release PortAudio system resources (5)

def record_input(state):
    if state:
        play_message(START_REC_AUDIOMESSAGE)

        wav_filename = f"{str(datetime.datetime.now()).replace(' ', 'T').replace(':','-').replace('.','-')}_{str(uuid.uuid4())[:16].upper()}.wav" #"output.wav"
        output_wav = os.path.join(REC_OUTPUT_FOLDER, wav_filename)
        frames = []                                                     # Initialize array to store frames
        p = pyaudio.PyAudio()                                           # Create an interface to PortAudio

        stream = p.open(format=SAMPLE_FORMAT,
                        channels=CHANNELS,
                        rate=FS,
                        frames_per_buffer=RECORD_CHUNK,
                        input=True)

        if DEBUG:
            print(f"[info] state {state} - started recording")            
            print(f"[debug] saving recording to {output_wav}")

        try:
            for i in range(0, int(FS / RECORD_CHUNK * TIMEOUT_SECONDS)):# Store data in OUTPUT_CHUNKs for time until timeout
                state = get_state()
                data = stream.read(RECORD_CHUNK)
                frames.append(data)
                if state == False:                                      # trip exit when handset is placed back
                    break
            
            stream.stop_stream()                                        # Stop and close the stream 
            stream.close()
            p.terminate()                                               # Terminate the PortAudio interface

            if not os.path.isdir(REC_OUTPUT_FOLDER):
                os.mkdir(REC_OUTPUT_FOLDER) 
            else:
                # save_recording(frames, p, output_wav)                 # dont know if i want to use the function or not
                wf = wave.open(output_wav, 'wb')                        # save_recording(frames, p)
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(p.get_sample_size(SAMPLE_FORMAT))
                wf.setframerate(FS)
                wf.writeframes(b''.join(frames))
                wf.close()

            if DEBUG:
                print("[info] finished recording and writing to SD")

        except Exception as e:
            # TODO! Add blinky LED here
            if DEBUG:
                print(f"[critical] fault during recording:{e}")

        play_message(STOP_REC_AUDIOMESSAGE)

def save_recording(frames, p, filename):
    if not os.path.isdir(REC_OUTPUT_FOLDER):
        os.mkdir(REC_OUTPUT_FOLDER) 
    else:
        wf = wave.open(filename, 'wb')                        # Save the recorded data as a WAV file
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(SAMPLE_FORMAT))
        wf.setframerate(FS)
        wf.writeframes(b''.join(frames))
        wf.close()


# main loop
try:
    while True:
        state = get_state()
        control_led(state)
        record_input(state)
        # time.sleep(0.5)  # Check every half second
except KeyboardInterrupt:
    print("Exiting...")
    GPIO.cleanup()
