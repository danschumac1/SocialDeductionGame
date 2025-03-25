const SERVER_URL = "https://socialdedictiongame.pythonanywhere.com";

/* ==========================
   LOBBY MANAGEMENT
========================== */

async function loadLobbyData(lobby_id) {
    console.log("Loading lobby data for lobby_id:", lobby_id);
    if (!lobby_id) {
        alert("Error: Missing lobby ID");
        window.location.href = "/lobby";
        return;
    }

    await fetchLobbyDetails(lobby_id);
    setInterval(() => fetchLobbyDetails(lobby_id), 3000);
}

async function fetchLobbyDetails(lobby_id) {
    let response = await fetch(`${SERVER_URL}/get_lobby/${lobby_id}`);
    let data = await response.json();

    if (data.status === "error") {
        alert("Lobby not found!");
        window.location.href = "/lobby";
        return;
    }

    document.getElementById("playerCount").innerText = `${data.current_players}/${data.max_players}`;
    document.getElementById("playerList").innerHTML = data.players
        .map(player => `<li>${player}</li>`)
        .join("");

    // Detect when the game starts
    if (data.current_players === data.max_players && data.status !== "Ongoing Game") {
        console.log("Lobby is full! Preparing to start the game...");
        document.getElementById("waitingMessage").innerText = "Game starting...";

        setTimeout(async () => {
            let startResponse = await fetch(`${SERVER_URL}/start_game`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ lobby_id: lobby_id })  // Ensure lobby_id is sent
            });

            let startData = await startResponse.json();
            if (startData.status === "success") {
                console.log("Game officially started! Redirecting to info collection...");
                window.location.href = `/info_collection/${lobby_id}/${sessionStorage.getItem("player_name")}`;
            } else {
                console.error("Failed to start the game:", startData);
            }
        }, 7000);
    }

    // If the game has already started, transition to info collection screen
    if (data.status === "Ongoing Game") {
        console.log("Game already ongoing! Redirecting to info collection...");
        window.location.href = `/info_collection/${lobby_id}/${sessionStorage.getItem("player_name")}`;
    }
}


async function fetchLobbies() {
    if (window.location.pathname !== "/lobby") return;

    let response = await fetch(`${SERVER_URL}/get_lobbies`);
    let lobbies = await response.json();

    let lobbyList = document.getElementById("lobbyList");
    if (!lobbyList) return;

    lobbyList.innerHTML = "";
    Object.entries(lobbies).forEach(([lobby_id, lobby]) => {
        let lobbyItem = document.createElement("div");
        lobbyItem.innerHTML = `
            <p>Lobby ID: ${lobby_id} | Players: ${lobby.players.length}/${lobby.max_players}</p>
            <button onclick="joinLobby(${lobby_id})">Join</button>
            <button onclick="deleteLobby(${lobby_id})">Delete</button>
        `;
        lobbyList.appendChild(lobbyItem);
    });
}


async function createLobby() {
    let playerCount = document.getElementById("playerCount").value;
    let password = prompt("Enter developer password:");

    let response = await fetch(`${SERVER_URL}/create_lobby`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ max_players: parseInt(playerCount), password })
    });

    let data = await response.json();
    if (data.status === "success") {
        fetchLobbies();
    } else {
        alert("Incorrect password!");
    }
}


async function deleteLobby(lobby_id) {
    let password = prompt("Enter developer password:");

    let response = await fetch(`${SERVER_URL}/delete_lobby`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ lobby_id: lobby_id, password })
    });

    let data = await response.json();
    if (data.status === "success") {
        fetchLobbies();
    } else {
        alert("Incorrect password or lobby not empty!");
    }
}


async function joinLobby(lobby_id) {
    let playerName = prompt("Enter your name:");

    let response = await fetch(`${SERVER_URL}/join_lobby`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ lobby_id: lobby_id, player_name: playerName })
    });

    let data = await response.json();
    console.log("Join Lobby Response:", data);

    if (data.status === "success") {
        sessionStorage.setItem("player_name", playerName);
        sessionStorage.setItem("lobby_id", lobby_id);
        showOverlayMessage("Joining lobby...");
        setTimeout(() => {
            window.location.href = data.redirect;
        }, 2000);
    } else {
        alert("Error: " + data.message);
        console.error("Join lobby failed:", data);
    }
}


async function leaveLobby() {
    let urlPath = window.location.pathname;
    let pathParts = urlPath.split("/");
    let lobby_id = pathParts[pathParts.length - 1];

    let playerName = sessionStorage.getItem("player_name");

    console.log("Leaving lobby with lobby id:", lobby_id);
    console.log("Player name:", playerName);

    if (!lobby_id || isNaN(lobby_id)) {
        alert("Error: Invalid or missing lobby ID.");
        return;
    }

    if (!playerName) {
        alert("Error: Player name not found in session storage.");
        return;
    }

    let response = await fetch(`${SERVER_URL}/leave_lobby`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ lobby_id: lobby_id, player_name: playerName })
    });

    let data = await response.json();
    if (data.status === "success") {
        sessionStorage.removeItem("player_name");
        window.location.href = "/lobby";
    } else {
        alert("Error leaving the lobby: " + data.message);
    }
}


async function checkLobbyFull(lobby_id) {
    let interval = setInterval(async () => {
        let response = await fetch(`${SERVER_URL}/get_lobbies`);
        let lobbies = await response.json();

        if (lobbies[lobby_id] && lobbies[lobby_id].status === "full") {
            clearInterval(interval);
            alert("Lobby is full! Starting game in 5 seconds...");
            setTimeout(() => startGame(lobby_id), 5000);
        }
    }, 2000);
}

/* ==========================
   INFO COLLECTION
========================== */

async function submitPlayerInfo() {
    let pathParts = window.location.pathname.split("/");
    let lobby_id = pathParts[pathParts.length - 2];
    let game_id = document.getElementById("gameID").innerText;
    let playerName = sessionStorage.getItem("player_name");

    if (!game_id) {
        console.error("Error: game_id is not defined.");
        alert("Game ID is not available. Please try again.");
        return;
    }
    console.log("Game ID:", game_id);

    let data = {
        player_name: playerName,
        lobby_id,
        game_id,
        grade: document.getElementById("grade").value,
        favorite_food: document.getElementById("favFood").value,
        favorite_animal: document.getElementById("favAnimal").value,
        favorite_color: document.getElementById("favColor").value,
        hobby: document.getElementById("hobby").value,
        extra_info: document.getElementById("extraInfo").value
    };

    let response = await fetch(`${SERVER_URL}/submit_info`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });

    let result = await response.json();
    if (result.status === "success") {
        sessionStorage.setItem("codename", result.codename);
        sessionStorage.setItem("color", result.color);
        window.location.href = `/game/${game_id}`;
        console.log("Response from server:", result);
    } else {
        alert("Error submitting info.");
    }
}

/* ==========================
   GAME & CHAT SYSTEM
========================== */

async function startGame(lobby_id) {
    let response = await fetch(`${SERVER_URL}/start_game`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ lobby_id: lobby_id })
    });

    let data = await response.json();
    if (data.status === "success") {
        sessionStorage.setItem("game_id", data.game_id);
        sessionStorage.setItem("player_name", data.player_name);

        showOverlayMessage("Game is starting...");
        setTimeout(() => {
            window.location.href = `/info_collection/${lobby_id}/${sessionStorage.getItem("player_name")}`;
        }, 7000);
    } else {
        console.error("Failed to start the game:", data);
    }
}


function showOverlayMessage(message) {
    let overlay = document.createElement("div");
    overlay.className = "overlay-message";
    overlay.innerText = message;
    document.body.appendChild(overlay);
    overlay.style.display = "block";

    setTimeout(() => {
        overlay.style.display = "none";
        document.body.removeChild(overlay);
    }, 5000);
}


async function fetchGameStatus(game_id) {
    let response = await fetch(`${SERVER_URL}/get_game_status/${game_id}`);
    let data = await response.json();

    if (data.status === "Waiting") {
        document.getElementById("gameOverlay").style.display = "block";
        document.getElementById("waitingMessage").innerText = "Waiting for players...";
    } else {
        document.getElementById("gameOverlay").style.display = "none";
    }
}


document.addEventListener("DOMContentLoaded", () => {
    initializeChat();
});


// TODO Update to only initialize on game screen
async function initializeChat() {
    let chatInput = document.getElementById("chatInput");
    let chatbox = document.getElementById("chatbox");

    if (!chatInput || !chatbox) {
        console.error("Chat elements not found.");
        return;
    }

    chatInput.addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            sendMessage();
        }
    });

    setInterval(fetchMessages, 2000);
}


// async function sendMessage() {
//     let chatInput = document.getElementById("chatInput");
//     let chatbox = document.getElementById("chatbox");
//     let message = chatInput.value.trim();
//     let playerName = sessionStorage.getItem("player_name");
//     let gameID = document.getElementById("gameID").innerText;

//     if (!message || !playerName || !gameID) return;

//     let response = await fetch(`${SERVER_URL}/send_message`, {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({ game_id: gameID, player_name: playerName, message })
//     });

//     let data = await response.json();
//     if (data.status === "success") {
//         chatInput.value = "";
//         fetchMessages();
//     } else {
//         console.error("Error sending message:", data.message);
//     }
// }
async function sendMessage() {
    let chatInput = document.getElementById("chatInput");
    let chatbox = document.getElementById("chatbox");
    let message = chatInput.value.trim();
    let playerName = sessionStorage.getItem("player_name");
    let gameID = document.getElementById("gameID").innerText;

    // Retrieve codename and color from session storage
    let codename = sessionStorage.getItem("codename");
    let color = sessionStorage.getItem("color");

    if (!message || !playerName || !gameID) return;

    let response = await fetch(`${SERVER_URL}/send_message`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ game_id: gameID, player_name: playerName, codename: codename, color: color, message: message })
    });

    let data = await response.json();
    if (data.status === "success") {
        chatInput.value = "";
        fetchMessages();
    } else {
        console.error("Error sending message:", data.message);
    }
}


// async function fetchMessages() {
//     let gameID = document.getElementById("gameID").innerText;
//     let chatbox = document.getElementById("chatbox");

//     if (!gameID || !chatbox) return;

//     let response = await fetch(`${SERVER_URL}/get_messages/${gameID}`);

//     // Log the raw response
//     let data = await response.json();
//     console.log(data);  // This will log the entire response data to the console

//     if (response.ok && Array.isArray(data.messages)) {
//         let messages = data.messages;
//         chatbox.innerHTML = messages
//             .map(msg >= `<p><strong>${msg.player_name}:</strong> ${msg.message}</p>`)
//             .join("");
//     } else {
//         console.error("Error: Invalid message format", data);
//     }
// }
async function fetchMessages() {
    let gameID = document.getElementById("gameID").innerText;
    let chatbox = document.getElementById("chatbox");

    if (!gameID || !chatbox) return;

    let response = await fetch(`${SERVER_URL}/get_messages/${gameID}`);
    if (response.ok) {
        let data = await response.json();

        chatbox.innerHTML = data.messages.map(msg => {
            return `<p><strong style="color:${msg.color}">${msg.codename}:</strong> ${msg.message}</p>`;
        }).join("");
    } else {
        console.error("Error fetching messages:", await response.json());
    }
}


// Refreshes screens
document.addEventListener("DOMContentLoaded", () => {
    let path = window.location.pathname;

    if (path === "/lobby") {
        fetchLobbies();
        setInterval(fetchLobbies, 3000);
    }

    if (path.startsWith("/waiting_room/")) {
        let lobby_id = path.split("/").pop();
        loadLobbyData(lobby_id);
        setInterval(() => fetchLobbyDetails(lobby_id), 3000);
    }

    if (path === "/game") {
        fetchMessages();
        setInterval(fetchMessages, 2000);
        let game_id = sessionStorage.getItem("game_id");
        setInterval(() => fetchGameStatus(game_id), 3000);
    }
});