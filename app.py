from flask import Flask, jsonify, render_template
import socket

app = Flask(__name__)

# Define STM32 IP and Port
STM32_IP = "192.168.0.104"  # Replace with actual STM32 IP
STM32_PORT = 8888           # Port STM32 is listening on

def check_stm32_online():
    """Checks if the STM32 controller is online by attempting a TCP connection."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.settimeout(3)  # Set timeout to 3 seconds
            client_socket.connect((STM32_IP, STM32_PORT))
            return {"status": "online", "message": "STM32 is reachable"}
    except (socket.timeout, ConnectionRefusedError):
        return {"status": "offline", "message": "STM32 is unreachable"}
    except Exception as e:
        return {"status": "offline", "message": str(e)}

@app.route('/')
def home():
    """Serve the HTML page."""
    return render_template('home.html')

@app.route('/check_stm32', methods=['GET'])
def check_stm32():
    """API endpoint to check STM32 connectivity."""
    result = check_stm32_online()
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
