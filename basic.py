from flask import Flask, render_template, request, jsonify
from gpiozero import PWMOutputDevice, DigitalOutputDevice

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

@app.route('/')
def index():
    return render_template('./index.html')

@app.route('/control', methods=['POST'])
def control():
    data = request.json
    action = data.get('action')
    
    if action == 'forward':
        pwm_reverse.value = 0.0
        pwm_forward.value = 0.5
    elif action == 'backward':
        pwm_forward.value = 0.0
        pwm_reverse.value = 0.5
    elif action == 'stop':
        stop_motor()
        
    return jsonify(success=True)

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)
    finally:
        stop_motor()
