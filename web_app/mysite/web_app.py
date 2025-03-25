import os
import json
import logging
import random
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# FOLDERS #
DATA_FOLDER = "/home/SocialDedictionGame/data"
GAME_DATA_FOLDER ="/home/SocialDedictionGame/mysite/data/"
GAME_LOGS_FOLDER ="/home/SocialDedictionGame/mysite/data/game_logs/"
CHAT_LOGS_FOLDER ="/home/SocialDedictionGame/mysite/data/chat_logs/"
os.makedirs(DATA_FOLDER, exist_ok=True)
os.makedirs(GAME_DATA_FOLDER, exist_ok=True)
os.makedirs(GAME_LOGS_FOLDER, exist_ok=True)
os.makedirs(CHAT_LOGS_FOLDER, exist_ok=True)

# LOBBY, PLAYER, & GAME FILES #
PLAYER_FILE = os.path.join(DATA_FOLDER, "players.json")
PLAYER_INFO_FILE = os.path.join(GAME_DATA_FOLDER, "player_info.json")
LOBBY_FILE = os.path.join(DATA_FOLDER, "lobbies.json")

# DATA FILES #
CODENAME_FILE = os.path.join(GAME_DATA_FOLDER, "codenames.txt")
COLOR_FILE = os.path.join(GAME_DATA_FOLDER, "colors.txt")
GAME_COUNTER_FILE = os.path.join(GAME_DATA_FOLDER, "game_counter.txt")
GAME_LOG_FILE = os.path.join(GAME_DATA_FOLDER, "game_log.txt")

DEVELOPER_PASSWORD = "meat"

def read_json(file, default={}):
    if not os.path.exists(file):
        return default
    try:
        with open(file, "r") as f:
            data = json.load(f)
        print(f"Read from {file}: {json.dumps(data, indent=4)}")
        return data
    except Exception as e:
        print(f"Error reading {file}: {e}")
        return default

def write_json(file, data):
    try:
        with open(file, "w") as f:
            json.dump(data, f, indent=4)
            f.flush()  # Force writing to disk
            os.fsync(f.fileno())  # Ensure changes are saved
        print(f"Successfully wrote data to {file}: {json.dumps(data, indent=4)}")
    except Exception as e:
        print(f"Error writing to {file}: {e}")


###############################################
# RENDER TEMPLATES
###############################################

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/lobby")
def lobby():
    return render_template("lobby.html")


@app.route("/waiting_room/<lobby_id>")
def waiting_room(lobby_id):
    return render_template("waiting_room.html", lobby_id=lobby_id)


@app.route("/info_collection/<lobby_id>/<player_name>")
def info_collection(lobby_id, player_name):
    lobbies = read_json(LOBBY_FILE)
    game_id = lobbies[lobby_id].get("game_id")
    return render_template("info_collection.html", lobby_id=lobby_id, player_name=player_name, game_id=game_id)


@app.route("/game/<game_id>")
def game(game_id):
    lobbies = read_json(LOBBY_FILE)
    if not any(lobby["game_id"] == int(game_id) for lobby in lobbies.values()):
        return jsonify({"status": "error", "message": "Game not found"}), 404

    return render_template("game.html", game_id=game_id)

###############################################
# LOBBY & WAITING ROOMS
###############################################

@app.route("/get_lobbies")
def get_lobbies():
    return jsonify(read_json(LOBBY_FILE))


@app.route("/get_lobby/<lobby_id>")
def get_lobby(lobby_id):
    lobbies = read_json(LOBBY_FILE)
    lobby_id = str(lobby_id)

    if lobby_id in lobbies:
        return jsonify({
            "status": "success",
            "lobby_id": lobby_id,
            "players": lobbies[lobby_id]["players"],
            "current_players": len(lobbies[lobby_id]["players"]),
            "max_players": lobbies[lobby_id]["max_players"]
        })

    return jsonify({"status": "error", "message": "Lobby not found"}), 404


@app.route("/create_lobby", methods=["POST"])
def create_lobby():
    data = request.json
    server_logger.debug(f"Received lobby creation request: {data}")

    max_players = data.get("max_players", 1)
    if max_players < 1:
        return jsonify({"status": "error", "message": "Lobby must have at least 1 player"}), 400

    if data.get("password") != DEVELOPER_PASSWORD:
        error_logger.error("Unauthorized attempt to create a lobby")
        return jsonify({"status": "error", "message": "Unauthorized"}), 403

    lobbies = read_json(LOBBY_FILE)
    lobby_id = str(len(lobbies) + 1)
    game_id = 0 # Placeholder value

    lobbies[lobby_id] = {
        "max_players": max_players,
        "players": [],
        "status": "waiting",
        "game_id": game_id
    }

    write_json(LOBBY_FILE, lobbies)
    access_logger.info(f"Lobby {lobby_id} created: {lobbies}")

    return jsonify({"status": "success", "lobby_id": lobby_id})


@app.route("/join_lobby", methods=["POST"])
def join_lobby():
    data = request.json
    lobby_id = str(data.get("lobby_id"))
    player_name = data.get("player_name")

    if not lobby_id or not player_name:
        return jsonify({"status": "error", "message": "Missing lobby ID or player name"}), 400

    lobbies = read_json(LOBBY_FILE)

    if lobby_id not in lobbies:
        return jsonify({"status": "error", "message": "Lobby does not exist"}), 404

    if len(lobbies[lobby_id]["players"]) >= lobbies[lobby_id]["max_players"]:
        return jsonify({"status": "error", "message": "Lobby is full"}), 400

    lobbies[lobby_id]["players"].append(player_name)

    if len(lobbies[lobby_id]["players"]) == lobbies[lobby_id]["max_players"]:
        lobbies[lobby_id]["status"] = "Ongoing Game"
        lobbies[lobby_id]["game_id"] = get_next_game_number()  # Update game_id when lobby is full

    write_json(LOBBY_FILE, lobbies)

    players = read_json(PLAYER_FILE)
    players[player_name] = {"lobby_id": lobby_id}
    write_json(PLAYER_FILE, players)

    access_logger.info(f"{player_name} joined Lobby {lobby_id}: {lobbies[lobby_id]['players']}")

    return jsonify({"status": "success", "redirect": f"/waiting_room/{lobby_id}"})


@app.route("/leave_lobby", methods=["POST"])
def leave_lobby():
    data = request.json
    player_name = data.get("player_name")
    lobby_id = str(data.get("lobby_id"))

    if not player_name:
        error_logger.error("leave_lobby: Missing player name in request")
        return jsonify({"status": "error", "message": "Missing player name"}), 400

    if not lobby_id or lobby_id == "None":
        error_logger.error("leave_lobby: Missing or invalid lobby ID in request")
        return jsonify({"status": "error", "message": "Missing lobby ID"}), 400

    lobbies = read_json(LOBBY_FILE)
    players = read_json(PLAYER_FILE)

    if lobby_id not in lobbies:
        error_logger.error(f"leave_lobby: Lobby {lobby_id} not found in lobbies.json")
        return jsonify({"status": "error", "message": f"Lobby {lobby_id} not found"}), 404

    if player_name not in lobbies[lobby_id]["players"]:
        error_logger.error(f"leave_lobby: Player {player_name} not found in lobby {lobby_id}")
        return jsonify({"status": "error", "message": f"Player {player_name} not found in lobby"}), 400

    lobbies[lobby_id]["players"].remove(player_name)
    write_json(LOBBY_FILE, lobbies)

    if player_name in players:
        del players[player_name]
        write_json(PLAYER_FILE, players)

    access_logger.info(f"{player_name} left Lobby {lobby_id}")
    return jsonify({"status": "success", "current_players": len(lobbies[lobby_id]['players'])})


@app.route("/delete_lobby", methods=["POST"])
def delete_lobby():
    data = request.json

    if data.get("password") != DEVELOPER_PASSWORD:
        return jsonify({"status": "error", "message": "Unauthorized"}), 403

    server_logger.debug(f"Received lobby deletion request: {data}")

    lobbies = read_json(LOBBY_FILE)
    players = read_json(PLAYER_FILE)
    lobby_id = str(data["lobby_id"])

    if lobby_id in lobbies:
        players_in_lobby = lobbies[lobby_id]["players"]

        del lobbies[lobby_id]
        write_json(LOBBY_FILE, lobbies)

        for player in players_in_lobby:
            if player in players:
                del players[player]

        write_json(PLAYER_FILE, players)

        access_logger.info(f"Lobby {lobby_id} deleted. Players removed: {players_in_lobby}")
        return jsonify({"status": "success"})

    return jsonify({"status": "error", "message": "Lobby not found"}), 400


###############################################
# INFO COLLECTION
###############################################

def get_unique_codename():                  # Assigns each player a unique codename
    with open(CODENAME_FILE, "r") as f:
        codenames = f.read().splitlines()
    return random.choice(codenames)

def get_unique_color():                     # Assigns each player a unique text color
    with open(COLOR_FILE, "r") as f:
        colors = f.read().splitlines()
    return random.choice(colors)

def get_next_game_number():                 # Assigns and increments the game id
    if not os.path.exists(GAME_COUNTER_FILE):
        with open(GAME_COUNTER_FILE, "w") as f:
            f.write("1")

    with open(GAME_COUNTER_FILE, "r") as f:
        game_number = int(f.read().strip())

    # Increment and save
    with open(GAME_COUNTER_FILE, "w") as f:
        f.write(str(game_number + 1))

    return game_number

@app.route("/submit_info", methods=["POST"])
def submit_info():
    data = request.json
    player_name = data.get("player_name")
    lobby_id = data.get("lobby_id")
    game_id = data.get("game_id")

    # Assign unique codename & color
    codename = get_unique_codename()
    color = get_unique_color()

    # Save player info
    player_info = f"{player_name}, {lobby_id}, {game_id}, {codename}, {color}, {data['grade']}, {data['favorite_food']}, {data['favorite_animal']}, {data['favorite_color']}, {data['hobby']}, {data['extra_info']}\n"

    with open(PLAYER_INFO_FILE, "a") as f:
        f.write(player_info)

    # return jsonify({"status": "success"})
    return jsonify({"status": "success", "codename": codename, "color": color})


###############################################
# GAME
###############################################

@app.route("/start_game", methods=["POST"])
def start_game():
    data = request.json
    lobby_id = str(data.get("lobby_id"))  # Get lobby_id from request

    if not lobby_id:
        error_logger.error("start_game: Missing lobby ID in request")
        return jsonify({"status": "error", "message": "Missing lobby ID"}), 400

    lobbies = read_json(LOBBY_FILE)

    if lobby_id not in lobbies:
        error_logger.error(f"start_game: Lobby ID {lobby_id} not found")
        return jsonify({"status": "error", "message": "Lobby ID not found"}), 404

    game_id = lobbies[lobby_id].get("game_id")
    if not game_id:
        error_logger.error(f"start_game: Game ID not found for Lobby ID {lobby_id}")
        return jsonify({"status": "error", "message": "Game ID not found"}), 404

    lobbies[lobby_id]["status"] = "Ongoing Game"  # Mark game as started
    write_json(LOBBY_FILE, lobbies)

    # Log game start
    with open(GAME_LOG_FILE, "a") as f:
        f.write(
            f"Game ID: {game_id} Human Players: {len(lobbies[lobby_id]['players'])} Duration: TBD Winner: TBD Completed: TBD\n")

    access_logger.info(f"Game {game_id} started for Lobby {lobby_id}")

    return jsonify({"status": "success", "game_id": game_id})


@app.route("/send_message", methods=["POST"])
def send_message():
    data = request.json
    game_id = str(data.get("game_id"))
    player_name = data.get("player_name")
    codename = str(data.get("codename"))
    color = str(data.get("color"))
    message = data.get("message")

    if not game_id or not player_name or not message:
        return jsonify({"status": "error", "message": "Missing game ID, player name, or message"}), 400

    chat_log_file = os.path.join(CHAT_LOGS_FOLDER, f"{game_id}.json")

    chat_data = read_json(chat_log_file, default=[])
    chat_entry = {
        "player": player_name,
        "codename": codename,
        "color": color,  # Store color as hex code
        "message": message
    }
    chat_data.append(chat_entry)

    # Log the chat data before writing
    print("Updated chat data:", chat_data)

    write_json(chat_log_file, chat_data)

    return jsonify({"status": "success"})


@app.route("/get_messages/<game_id>")
def get_messages(game_id):
    chat_log_file = os.path.join(CHAT_LOGS_FOLDER, f"{game_id}.json")
    chat_data = read_json(chat_log_file, default=[])
    return jsonify({"status": "success", "messages": chat_data})


###############################################
# LOGS
###############################################

# Define log directory
LOG_DIR = "/home/SocialDedictionGame/logs/"
os.makedirs(LOG_DIR, exist_ok=True)

# Log file paths
ACCESS_LOG = os.path.join(LOG_DIR, "access.log")
ERROR_LOG = os.path.join(LOG_DIR, "error.log")
SERVER_LOG = os.path.join(LOG_DIR, "server.log")

# Create loggers
access_logger = logging.getLogger("access")
error_logger = logging.getLogger("error")
server_logger = logging.getLogger("server")

# Set log levels
access_logger.setLevel(logging.INFO)
error_logger.setLevel(logging.ERROR)
server_logger.setLevel(logging.DEBUG)

# Create handlers
access_handler = logging.FileHandler(ACCESS_LOG)
error_handler = logging.FileHandler(ERROR_LOG)
server_handler = logging.FileHandler(SERVER_LOG)

# Set log formats
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
access_handler.setFormatter(formatter)
error_handler.setFormatter(formatter)
server_handler.setFormatter(formatter)

# Add handlers to loggers
access_logger.addHandler(access_handler)
error_logger.addHandler(error_handler)
server_logger.addHandler(server_handler)

logging.basicConfig(filename='/home/SocialDedictionGame/logs/flask_debug.log', level=logging.DEBUG)

if __name__ == "__main__":
    app.run(debug=True)