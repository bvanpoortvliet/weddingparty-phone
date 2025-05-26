# Wedding Phone Recorder (Raspberry Pi 3B+)
A retro-style voicemail recorder using a Raspberry Pi 3. Detects when a handset is picked up, plays a prompt, records audio, and plays an outro when the handset is placed back. Fun for weddings!

---
## 🖥️ OS
- Raspbian Lite (TODO: check if DietPi performs better)

---
## 🧰 Hardware
- Raspberry Pi 3B+
- Analog phone with mechanical cradle switch
- Hook switch connected to GPIO pin 2 (BCM)
- Optional: LED connected to GPIO pin 18 (BCM)
- USB sound card with audio input and output
---

## 📦 Software Installation
### System packages:

```bash
sudo apt update
sudo apt install git wget curl python3 python3-pip python3-venv libcurl4-openssl-dev libssl-dev alsa-utils portaudio19-dev build-essential -y
```

### Python setup:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r ./requirements.txt
```

---

## 🔧 Directory Layout
```
project/
├── audio/
│   ├── src/
│   │   ├── leave-a-message.wav
│   │   └── end-of-recording.wav
│   └── output/
├── weddingparty-phone.py
├── requirements.txt
└── README.md
```

- `audio/src/`: message prompts
- `audio/output/`: saved recordings

---

## 🚦 GPIO Pinout

| Function     | BCM Pin |
|--------------|---------|
| Hook Switch  | 2       |
| LED Output   | 18      |

---

## ▶️ Running the App

```bash
source venv/bin/activate
python3 weddingparty-phone.py
```
Press `Ctrl+C` to exit.

##### _NOTE: consider running this script as a service._
---

## 🎙 Audio Behavior

1. Detects handset pickup
2. Turns on LED
3. Plays `leave-a-message.wav`
4. Starts recording audio
5. Stops when handset is placed back
6. Saves `.wav` file in `audio/output/`
7. Plays `end-of-recording.wav`

---

## ⚙️ requirements.txt

```txt
RPi.GPIO
pyaudio
datetime
uuid
```
---

## 📝 License
I don't care, use it as you please.
