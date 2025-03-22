from flask import Flask, jsonify, render_template
import socket
import threading
import time
from datetime import datetime
from flask_cors import CORS

# Initialize Flask application
app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing (CORS) to allow API access from different domains

# Server Configuration
HOST = '192.168.0.100'  # The IP address of the server
PORT = 12345  # Port number for TCP communication with clients

# Dictionaries to manage connected clients and their states
clients = {}  # Stores active client connections (IP -> Socket object)
acknowledgments = {}  # Tracks whether each client has acknowledged commands (IP -> Boolean)
client_states = {}  # Tracks process states per client (IP -> Boolean, True if running, False if stopped)
connected_clients = {}  # Stores the timestamp of when each client last communicated

# Global variable to track whether the machine is running or stopped
machine_started = False  # True if the machine is running, False if stopped


def timestamp():
    """Returns the current timestamp for logging with milliseconds."""
    return datetime.now().strftime("%d-%m-%y %H:%M:%S.%f")[:-3]

def handle_client(conn, addr):
    """
    Handles communication with a connected client.
    
    This function continuously listens for messages from the client, processes them,
    and manages client connection status. If the client disconnects, it removes their
    information from tracking dictionaries.
    
    Args:
        conn (socket.socket): The socket connection object for the client.
        addr (tuple): A tuple containing (IP address, port) of the client.
    """
    client_ip = addr[0]  # Extract the client's IP address
    print(f"{timestamp()} - Client connected: {client_ip}")  # Log client connection
    
    # Store client connection and initialize tracking variables
    clients[client_ip] = conn  # Store the socket object for the client
    acknowledgments[client_ip] = False  # No acknowledgment received initially
    client_states[client_ip] = False  # Assume the client process is not running
    connected_clients[client_ip] = timestamp()  # Store the timestamp of connection
    
    try:
        while True:
            # Receive up to 1024 bytes of data from the client
            data = conn.recv(1024).decode().strip()  # Decode received bytes and remove extra spaces
            
            if not data:  # If no data is received, assume client disconnected
                break  # Exit loop and proceed to cleanup
            
            # Log received message
            print(f"{timestamp()} - Received from {client_ip}: {data}")
            
            # Process received message (e.g., check for acknowledgment)
            process_client_message(client_ip, data)
            
            # Update the last activity timestamp for this client
            connected_clients[client_ip] = timestamp()
    
    except ConnectionResetError:
        # Handle unexpected client disconnections (e.g., network issues)
        print(f"{timestamp()} - Client {client_ip} disconnected unexpectedly.")
    
    finally: # finally block does not force the client to disconnect. Without finally, if an exception occurs, the connection might not close properly, leading to resource leaks, stale client entries, or memory buildup in long-running servers.
        # Ensure cleanup is performed regardless of how the function exits
        
        conn.close()  # Close the client socket to release resources
        
        # Remove client from tracking dictionaries to free memory
        clients.pop(client_ip, None)  # Remove from active clients , If client_ip is not in clients, using None prevents an error (KeyError).
        acknowledgments.pop(client_ip, None)  # Remove acknowledgment tracking
        client_states.pop(client_ip, None)  # Remove process state tracking
        connected_clients.pop(client_ip, None)  # Remove last activity timestamp
        
        # Log client disconnection
        print(f"{timestamp()} - Client {client_ip} disconnected.")


def process_client_message(client_ip, message):
    """
    Processes messages received from a client.

    Extracts the core message between '$' and '#' and checks if it matches 
    expected acknowledgment formats.
    
    Args:
        client_ip (str): The IP address of the client sending the message.
        message (str): The message received from the client.
    """
    # Extract substring between '$' and '#'
    if message.startswith("$") and "#" in message:
        extracted_msg = message.split("$")[1].split("#")[0]  # Extract between $ and #
        
        # Check if the extracted message is a valid acknowledgment
        if extracted_msg in ["ACK_STR", "ACK_STP", "ACK_ST1_LOAD,200,200"]:
            acknowledgments[client_ip] = True  # Mark acknowledgment as received
            print(f"{timestamp()} - Acknowledgment received from {client_ip}: {extracted_msg}")


def send_message(client_ip, message):
    """
    Sends a message to a specific client.
    
    This function attempts to send a message to a client using their stored socket connection.
    If the client is disconnected, it removes them from the tracking dictionary.
    
    Args:
        client_ip (str): The IP address of the target client.
        message (str): The message to send to the client.
    
    Returns:
        bool: True if the message was sent successfully, False otherwise.
    """
    if client_ip in clients:  # Check if the client is connected
        try:
            clients[client_ip].sendall(message.encode())  # Send message to the client
            print(f"{timestamp()} - Sent '{message.strip()}' to {client_ip}")
            return True  # Return success
        except (ConnectionResetError, BrokenPipeError):  # Handle disconnection errors
            print(f"{timestamp()} - Error: Lost connection to {client_ip}")
            clients.pop(client_ip, None)  # Remove client from tracking dictionary
    else:
        print(f"{timestamp()} - Client {client_ip} not found.")  # Log missing client error
    return False  # Return failure


def broadcast_message(message, command):
    """
    Broadcasts a command message to all connected clients.
    
    This function sends a specified command (start/stop) to all clients,
    updates their state accordingly, and waits for acknowledgments.
    
    Args:
        message (str): The command message to send (e.g., "$STR#", "$STP#").
        command (str): The command type ('start' or 'stop').
    """
    global machine_started
    state = True if command == "start" else False  # Determine state based on command
    machine_started = state  # Update global machine state
    
    
    # Send the command to all connected clients and update their states
    for client_ip in clients.keys():
        send_message(client_ip, message)
        client_states[client_ip] = state
    
    print(f"machine started : {machine_started}")

    # Set a timeout of 10 seconds for receiving acknowledgments
    timeout = time.time() + 10
    while not all(acknowledgments.get(ip, False) for ip in clients) and time.time() < timeout:
        time.sleep(0.5)  # Wait for acknowledgments with small delay
    
    # Log the acknowledgment status after timeout or when all clients respond
    print(f"{timestamp()} - All clients acknowledged {command} command.")

@app.route('/broadcast/<command>', methods=['POST'])
def broadcast_command(command):
    """
    Endpoint to broadcast a command to all connected clients.

    Args:
        command (str): The command to be broadcasted, extracted from the URL.

    Returns:
        JSON response:
            - 200 OK with success message if the command is valid and broadcasted successfully.
            - 400 Bad Request if the command is invalid.
    """

    # Dictionary mapping command names to their corresponding message formats
    command_mapping = {
        "start": "$STR#\r\n",  # Command to start the process
        "stop": "$STP#\r\n"    # Command to stop the process
        # add more commands here for broadcasting to all clients
    }

    # Check if the received command is valid
    if command not in command_mapping:
        return jsonify({"message": "Invalid command"}), 400  # Return error if the command is not recognized

    # Call the broadcast function to send the command message to all connected clients
    broadcast_message(command_mapping[command], command)

    # Return success response indicating that the command was broadcasted successfully
    return jsonify({
        "success": True,
        "message": f"Broadcast '{command}' to all clients and received acknowledgments"
    }), 200


def start_tcp_server():
    """
    Initializes and starts the TCP server to listen for incoming client connections.

    The server binds to a predefined host and port, then listens for client connections.
    Each accepted client connection is handled in a separate thread to allow multiple
    clients to connect concurrently.

    The function runs indefinitely, accepting new connections and spawning threads
    for handling each client.

    Exceptions encountered during connection acceptance are caught and logged.
    """
    
    # Create a new TCP socket using IPv4 addressing (AF_INET) and TCP protocol (SOCK_STREAM)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the specified host and port
    sock.bind((HOST, PORT))

    # Enable the server to accept connections, with the default backlog queue size
    sock.listen()

    # Log the server startup information with a timestamp
    print(f"{timestamp()} - TCP server started on {HOST}:{PORT}")

    # Infinite loop to continuously accept client connections
    while True:
        try:
            # Accept a new client connection; this call blocks until a connection is received
            conn, addr = sock.accept()

            # Spawn a new thread to handle the client connection
            # `daemon=True` ensures that the thread will not prevent the program from exiting
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

        except Exception as e:
            # Log any exception that occurs while accepting client connections
            print(f"{timestamp()} - TCP Server Error: {e}")

# Start the TCP server in a separate daemon thread to keep the main program responsive
threading.Thread(target=start_tcp_server, daemon=True).start()


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/command/<client_ip>/<command>', methods=['POST'])
def send_client_command(client_ip, command):
    """
    API endpoint to send a specific command to a designated client.

    Args:
        client_ip (str): The IP address of the target client.
        command (str): The command to be sent.

    Returns:
        JSON response:
            - 200 OK if the command was sent successfully and an acknowledgment was received.
            - 500 Internal Server Error if the command was sent but no acknowledgment was received.
            - 500 Internal Server Error if the command could not be sent to the client.
            - 400 Bad Request if the command is invalid.
    """

    # Define a mapping between command names and their respective message formats
    command_mapping = {
        "load":"$ST1_LOAD,200,200#\r\n" # Load command
        #add more commands here for specific client
    }

    # Validate if the received command is recognized
    if command not in command_mapping:
        return jsonify({"message": "Invalid command"}), 400  # Return error if the command is not in the mapping

    # If the client IP exists in the known clients list, update its last active timestamp
    if client_ip in clients:
        connected_clients[client_ip] = timestamp()

    # Attempt to send the mapped command message to the specified client
    if send_message(client_ip, command_mapping[command]):
        timeout = time.time() + 5  # Set a 5-second timeout for acknowledgment

        # Wait in a loop for acknowledgment, checking every 0.5 seconds
        while not acknowledgments.get(client_ip, False) and time.time() < timeout:
            time.sleep(0.5)

        # If acknowledgment is received within the timeout, return success response
        if acknowledgments.get(client_ip, False):
            return jsonify({
                "message": f"Command '{command}' sent to {client_ip} and acknowledgment received"
            }), 200
        else:
            # No acknowledgment received within the timeout
            return jsonify({
                "message": f"Command '{command}' sent to {client_ip}, but no acknowledgment received"
            }), 500

    # If the message could not be sent, return an error response
    return jsonify({
        "message": f"Failed to send '{command}' to {client_ip}"
    }), 500


@app.route('/clients', methods=['GET'])
def get_connected_clients():
    """
    API endpoint to retrieve a list of currently connected clients.

    Returns:
        JSON response:
            - 200 OK with a dictionary containing connected clients and their last active timestamps.
    """

    # Return the dictionary of connected clients along with a 200 OK response
    return jsonify(connected_clients), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)