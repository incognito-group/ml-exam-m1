// Game constants
const STATE_EMPTY = 0;
const STATE_X = 1;
const STATE_O = -1;

// Game variables
let gameMode = '2_players';  // '2_players', 'hybrid', 'vs_ml'
let sessionId = null;
let currentPlayer = 1;  // 1 for X, -1 for O
let gameOver = false;
let gameBoard = [0, 0, 0, 0, 0, 0, 0, 0, 0];

// API endpoint
const API_URL = 'http://localhost:5000/api';

// DOM elements
const modal = document.querySelector('.modal_hidden');
const modalMessage = document.getElementById('message');
const closeButton = document.querySelector('.close-button');
const modeButtons = document.querySelectorAll('.mode ul li');
const cells = document.querySelectorAll('.tableau table td');

// Event listeners
closeButton.addEventListener('click', () => {
    modal.style.display = 'none';
});

// Mode selection
modeButtons.forEach((button, index) => {
    button.addEventListener('click', () => {
        selectMode(index);
    });
});

// Cell clicks
cells.forEach((cell, index) => {
    cell.addEventListener('click', () => {
        makeMove(index);
    });
});

// Initialize game
async function selectMode(modeIndex) {
    const modes = ['2_players', 'hybrid', 'vs_ml'];
    const modeNames = ['2 Joueurs', 'Mode Hybride', 'Vs IA'];
    gameMode = modes[modeIndex];
    
    console.log(`Starting game in ${gameMode} mode`);
    
    try {
        const response = await fetch(`${API_URL}/game/new`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ mode: gameMode })
        });
        
        const data = await response.json();
        
        // Check for errors
        if (data.error) {
            alert(`❌ Erreur: ${data.error}`);
            console.error('Error:', data);
            return;
        }
        
        sessionId = data.session_id;
        gameBoard = data.board;
        currentPlayer = 1;
        gameOver = false;
        
        console.log('Game started:', data);
        updateBoard();
        
        // Highlight selected mode
        modeButtons.forEach((btn, idx) => {
            btn.style.backgroundColor = idx === modeIndex ? 'grey' : '';
        });
        
        // Show success message
        console.log(`✓ ${modeNames[modeIndex]} commencé!`);
        
    } catch (error) {
        console.error('Error starting game:', error);
        alert('❌ Erreur: Le serveur n\'est pas disponible sur le port 5000');
    }
}

async function makeMove(cellIndex) {
    if (!sessionId || gameMode === null) {
        alert('❌ Veuillez sélectionner un mode de jeu d\'abord');
        return;
    }
    
    if (gameOver) {
        alert('Game over. Cliquer "Rejouer" pour commencer une nouvelle partie');
        return;
    }
    
    if (gameBoard[cellIndex] !== STATE_EMPTY) {
        alert('Cellue déjà remplie');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/game/${sessionId}/move`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ position: cellIndex })
        });
        
        const data = await response.json();
        
        if (data.error) {
            alert(data.error);
            return;
        }
        
        gameBoard = data.board;
        currentPlayer = data.current_player;
        gameOver = data.game_over;
        
        updateBoard();
        
        // If AI made a move, update that too
        if (data.ai_move !== null) {
            console.log('AI moved to position:', data.ai_move);
            gameBoard = data.board;
            updateBoard();
        }
        
        // Check if game ended
        if (data.game_over) {
            endGame(data.winner);
        }
        
    } catch (error) {
        console.error('Error making move:', error);
    }
}

async function getAIMove() {
    if (!sessionId || gameMode !== 'hybrid') {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/game/${sessionId}/ai_move`);
        const data = await response.json();
        
        console.log('AI suggests move at position:', data.best_move);
        return data.best_move;
        
    } catch (error) {
        console.error('Error getting AI move:', error);
    }
}

function updateBoard() {
    console.log('Board state:', gameBoard);
    
    cells.forEach((cell, index) => {
        if (gameBoard[index] === STATE_X) {
            cell.textContent = 'X';
            cell.style.color = 'blue';
        } else if (gameBoard[index] === STATE_O) {
            cell.textContent = 'O';
            cell.style.color = 'red';
        } else {
            cell.textContent = '';
        }
    });
}

function endGame(winner) {
    setInterval(() => {
        gameOver = true;
        modal.style.display = 'flex';
    
        if (winner === 1) {
            modalMessage.textContent = 'X a gagné!';
        } else if (winner === -1) {
            modalMessage.textContent = 'O a gagné!';
        } else if (winner === 0) {
            modalMessage.textContent = "Match null";
        }
    }, 500)
}

function restart() {
    // Reset variables
    gameBoard = [0, 0, 0, 0, 0, 0, 0, 0, 0];
    currentPlayer = 1;
    gameOver = false;
    modal.style.display = 'none';
    updateBoard();
    
    // If we have a session, reset it on the server
    if (sessionId) {
        fetch(`${API_URL}/game/${sessionId}/reset`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        }).then(response => response.json())
          .then(data => {
              console.log('Game reset:', data);
              // Reload the window after reset
              location.reload();
          })
          .catch(error => {
              console.error('Error resetting game:', error);
              // Reload anyway if error
              location.reload();
          });
    }
}

// Initial message
window.addEventListener('load', () => {
    console.log('Game interface loaded. Select a game mode to start playing.');
    console.log('Available modes:');
    console.log('  1. 2 players - Play against another player');
    console.log('  2. Hybrid - Get AI suggestions');
    console.log('  3. Vs ML - Play against the AI');
});