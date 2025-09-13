from flask import Flask, jsonify, request
import threading
import time
from datetime import datetime

print("runing app.py")
app = Flask(__name__)

server_cache = {"value": 0}

BIT_LENGTH = 8

PASSWORD = "Password"  # CHANGE FOR THE PASSWORD IN HTTP              TRANSMITTER. Use HEADERS (WITHOUT THE #)
# Password: Password

# Command codes
STOP_CODE = "10110110"  # Binary code to stop a process
RUN_CODE = "01001001"  # Binary code to run/start a process

# Process control variables
process_running = False
process_thread = None

# Game control state
game_state = {
    "running": False,
    "last_command": None,
    "sequence": 0,
    "updated_at": None
}


def background_process():
    #Example background process that can be started/stopped
    global process_running
    counter = 0
    while process_running:
        counter += 1
        print(f"Background process running... count: {counter}")
        time.sleep(2)
    print("Background process stopped.")


def start_process():
    """Start the background process"""
    global process_running, process_thread, game_state
    if not process_running:
        process_running = True
        process_thread = threading.Thread(target=background_process)
        process_thread.start()

        # Update game state
        game_state["running"] = True
        game_state["last_command"] = "RUN"
        game_state["sequence"] += 1
        game_state["updated_at"] = datetime.now().isoformat()
        return True
    return False


def stop_process():
    """Stop the background process"""
    global process_running, process_thread, game_state
    if process_running:
        process_running = False
        if process_thread:
            process_thread.join()

        # Update game state
        game_state["running"] = False
        game_state["last_command"] = "STOP"
        game_state["sequence"] += 1
        game_state["updated_at"] = datetime.now().isoformat()
        return True
    return False


@app.route('/', methods=["GET", "POST"])
def main():
    if request.method == "POST":
        password = request.headers.get("Password")
        if password != PASSWORD:
            return jsonify({
                "error":
                "Unauthorized ahahahah. Invalid or missing password."
            }), 401

        binary_value = request.form.get("value")
        if binary_value and len(binary_value) == BIT_LENGTH and all(
                c in "01" for c in binary_value):

            # Check for command codes first
            if binary_value == STOP_CODE:
                success = stop_process()
                return jsonify({
                    "command": "STOP",
                    "success": success,
                    "status": "stopped" if success else "already stopped",
                    "value": binary_value
                }), 200

            elif binary_value == RUN_CODE:
                success = start_process()
                return jsonify({
                    "command": "RUN",
                    "success": success,
                    "status": "started" if success else "already running",
                    "value": binary_value
                }), 200

            # Normal binary value storage for non-command codes
            server_cache["value"] = int(binary_value, 2)
            return jsonify(
                {"value": format(server_cache["value"],
                                 f'0{BIT_LENGTH}b')}), 200

        return jsonify({
            "error":
            f"Invalid binary value. Must be {BIT_LENGTH} bits of 0s and 1s."
        }), 400

    elif request.method == "GET":
        return jsonify(
            {"value": format(server_cache["value"], f'0{BIT_LENGTH}b')}), 200


@app.route('/status', methods=["GET"])
def status():
    """Get current game state for the game to check"""
    return jsonify(game_state), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
