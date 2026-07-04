from flask import Flask, render_template, request, jsonify
from gpiozero import PWMOutputDevice, DigitalOutputDevice
import socket

app = Flask(__name__)

# Initialize Enable Pins (set to High immediately)
en_forward = DigitalOutputDevice(17, initial_value=True)
en_reverse = DigitalOutputDevice(27, initial_value=True)

# Initialize PWM Pins (Frequency default is 100Hz)
pwm_forward = PWMOutputDevice(12)
pwm_reverse = PWMOutputDevice(13)

def stop_motor():
    pwm_forward.value = 0.0
    pwm_reverse.value = 0.0

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()

def inject_ip_banner(html, local_ip):
    lower_html = html.lower()
    body_idx = lower_html.find('<body')
    if body_idx >= 0:
        tag_end = html.find('>', body_idx)
        if tag_end >= 0:
            return html[:tag_end+1] + f'<div style="padding: 1rem; background: #eef; font-weight: bold;">Local IP: {local_ip}</div>' + html[tag_end+1:]
    return f'<div style="padding: 1rem; background: #eef; font-weight: bold;">Local IP: {local_ip}</div>' + html

@app.route('/')
def index():
    local_ip = get_local_ip()
    rendered = render_template('./index.html')
    return inject_ip_banner(rendered, local_ip)

@app.route('/control', methods=['POST'])
def control():
    data = request.json
    action = data.get('action')
    # Modifiers: expect booleans 'alt' and 'shift' in the JSON
    alt = bool(data.get('alt', False))
    shift = bool(data.get('shift', False))

    # Determine speed: ctrl -> full, shift -> slow, otherwise default half
    if alt:
        speed = 1.0
    elif shift:
        speed = 0.1
    else:
        speed = 0.5
    
    if action == 'forward':
        pwm_reverse.value = 0.0
        pwm_forward.value = speed
    elif action == 'backward':
        pwm_forward.value = 0.0
        pwm_reverse.value = speed
    elif action == 'stop':
        stop_motor()
        
    return jsonify(success=True)

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)
    finally:
        stop_motor()
