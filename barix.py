import socket # Doesn't need installation
import pyaudio # Requires another package
import audioop # Doesn't need installation until python 3.13
import time

# Constants for the UDP socket
UDP_IP = "192.168.0.194"  # Listen on all local IPs
UDP_PORT = 9444     # Port number to listen on
SUBSCRIBE_INTERVAL = 15  # in seconds

# Audio constants
FORMAT = pyaudio.paInt16  # PCM format
CHANNELS = 1
RATE = 24000  # Sample rate

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", UDP_PORT)) # Throws an error if it's anything else
sock.sendto(b"subscribe", (UDP_IP, UDP_PORT))

p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, input=True)
# Timer for sending subscribe message every SUBSCRIBE_INTERVAL seconds
last_subscribe_time = time.time()

# Function to send subscribe message
def send_subscribe_message():
    sock.sendto(b"subscribe", (UDP_IP, UDP_PORT))
    print("Sending")

try:
    while True:
        # Receive data from UDP
        data, addr = sock.recvfrom(1024)  # Buffer size is 1024 bytes
        # Skip RTP header (first 12 bytes)
        payload = data[12:] 
        # Decode μ-law to PCM
        linear_pcm = audioop.ulaw2lin(payload,2)
        # Play audio
        stream.write(linear_pcm)
        # Check if it's time to send the subscribe message again
        if time.time() - last_subscribe_time >= SUBSCRIBE_INTERVAL:
            send_subscribe_message()
            last_subscribe_time = time.time()

        
except KeyboardInterrupt:
    pass
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()
    sock.close()

print("Stream closed and socket closed.")
