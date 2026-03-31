#!/usr/bin/env python3
"""
Web server API to connect the frontend with the Tic-Tac-Toe AI model (Minimax)
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from node import Node
import json

app = Flask(__name__)
CORS(app)

# Game sessions storage
game_sessions = {}
session_counter = 0

def board_to_list(node):
    """Convert Node board state to list"""
    return node.etat.copy()

def list_to_board(board_list):
    """Create Node from list"""
    node = Node()
    node.etat = board_list.copy()
    # Determine whose turn it is by counting X and O
    x_count = sum(1 for cell in board_list if cell == Node.X)
    o_count = sum(1 for cell in board_list if cell == Node.O)
    if x_count > o_count:
        node.tour = Node.O
    else:
        node.tour = Node.X
    return node

def check_winner(board):
    """Check if there's a winner. Returns 1 (X wins), -1 (O wins), 0 (no winner)"""
    node = Node()
    node.etat = board
    return node.eval_heuristique(1)

def check_game_over(board):
    """Check if game is over. Returns (game_over, winner)"""
    winner = check_winner(board)
    node = Node()
    node.etat = board
    is_full = node.is_full()
    
    if winner > 0:
        return True, 1  # X wins
    elif winner < 0:
        return True, -1  # O wins
    elif is_full:
        return True, 0  # Draw
    else:
        return False, None

@app.route('/api/game/new', methods=['POST'])
def new_game():
    """Start a new game"""
    global session_counter
    session_counter += 1
    session_id = str(session_counter)
    
    data = request.json
    mode = data.get('mode', '2_players')  # '2_players', 'hybrid', 'vs_ml'
    
    game_sessions[session_id] = {
        'board': [0] * 9,
        'mode': mode,
        'x_is_ai': mode == 'vs_ml',  # In vs_ml mode, AI plays as O
        'current_player': 1,  # 1 for X, -1 for O
    }
    
    return jsonify({
        'session_id': session_id,
        'board': game_sessions[session_id]['board'],
        'mode': mode,
        'message': f'New game started in {mode} mode'
    })

@app.route('/api/game/<session_id>/move', methods=['POST'])
def make_move(session_id):
    """Make a move in the game"""
    if session_id not in game_sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    game = game_sessions[session_id]
    data = request.json
    position = data.get('position')
    
    if not isinstance(position, int) or position < 0 or position > 8:
        return jsonify({'error': 'Invalid position'}), 400
    
    if game['board'][position] != 0:
        return jsonify({'error': 'Position already occupied'}), 400
    
    # Check game over
    game_over, winner = check_game_over(game['board'])
    if game_over:
        return jsonify({'error': 'Game is already over'}), 400
    
    # Make the move
    game['board'][position] = game['current_player']
    
    # Check if game is over
    game_over, winner = check_game_over(game['board'])
    
    response = {
        'board': game['board'],
        'current_player': game['current_player'],
        'game_over': game_over,
        'winner': winner,
        'ai_move': None
    }
    
    if not game_over:
        game['current_player'] = -game['current_player']
        
        # If it's AI's turn in vs_ml mode
        if game['mode'] == 'vs_ml' and game['current_player'] == -1:
            ai_move = get_best_move(game['board'])
            if ai_move is not None:
                game['board'][ai_move] = -1
                response['ai_move'] = ai_move
                response['board'] = game['board']
                
                # Check if AI move ended the game
                game_over, winner = check_game_over(game['board'])
                response['game_over'] = game_over
                response['winner'] = winner
                
                if not game_over:
                    game['current_player'] = 1  # Back to X
    
    return jsonify(response)

@app.route('/api/game/<session_id>/ai_move', methods=['GET'])
def get_ai_move(session_id):
    """Get AI's best move (for hybrid mode or debugging)"""
    if session_id not in game_sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    game = game_sessions[session_id]
    best_move = get_best_move(game['board'])
    
    return jsonify({
        'best_move': best_move,
        'eval': 'Optimal move computed by Minimax'
    })

@app.route('/api/game/<session_id>/state', methods=['GET'])
def get_game_state(session_id):
    """Get current game state"""
    if session_id not in game_sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    game = game_sessions[session_id]
    game_over, winner = check_game_over(game['board'])
    
    return jsonify({
        'board': game['board'],
        'mode': game['mode'],
        'current_player': game['current_player'],
        'game_over': game_over,
        'winner': winner,
    })

@app.route('/api/game/<session_id>/reset', methods=['POST'])
def reset_game(session_id):
    """Reset the current game"""
    if session_id not in game_sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    game = game_sessions[session_id]
    game['board'] = [0] * 9
    game['current_player'] = 1
    
    return jsonify({
        'board': game['board'],
        'message': 'Game reset'
    })

def get_best_move(board):
    """Compute best move using Minimax for O (AI)"""
    node = list_to_board(board)
    
    # Run minimax to depth 9 (full game tree)
    Node.minimax(node, 9, Node.O)
    
    if node.best is None:
        return None
    
    # Find which position changed
    for i in range(9):
        if node.etat[i] != node.best.etat[i]:
            return i
    
    return None

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get server statistics"""
    return jsonify({
        'total_sessions': len(game_sessions),
        'active_sessions': sum(1 for g in game_sessions.values() if not check_game_over(g['board'])[0])
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    print("Starting Tic-Tac-Toe AI API Server...")
    print("Frontend should connect to: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
