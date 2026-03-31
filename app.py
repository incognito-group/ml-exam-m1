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
minimax_stats = {
    'total_calls': 0,
    'hybrid_mode_calls': 0,
    'vs_ml_mode_calls': 0
}

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
    
    data = request.json
    mode = data.get('mode')  # '2_players', 'hybrid', 'vs_ml'
    
    # Validate mode is provided
    if not mode:
        return jsonify({
            'error': 'Veuillez sélectionner un mode de jeu',
            'valid_modes': ['2_players', 'hybrid', 'vs_ml']
        }), 400
    
    # Validate mode is valid
    valid_modes = ['2_players', 'hybrid', 'vs_ml']
    if mode not in valid_modes:
        return jsonify({
            'error': f'Mode "{mode}" invalide',
            'valid_modes': valid_modes
        }), 400
    
    session_counter += 1
    session_id = str(session_counter)
    
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
        
        # If it's AI's turn in vs_ml or hybrid mode
        if game['mode'] in ['vs_ml', 'hybrid'] and game['current_player'] == -1:
            ai_move = get_best_move(game['board'], game['mode'])
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

def get_best_move(board, mode='vs_ml'):
    """Compute best move using Minimax for O (AI)"""
    global minimax_stats
    
    node = list_to_board(board)
    
    # Track minimax calls
    minimax_stats['total_calls'] += 1
    if mode == 'hybrid':
        minimax_stats['hybrid_mode_calls'] += 1
    else:
        minimax_stats['vs_ml_mode_calls'] += 1
    
    # Run minimax to depth 9 (full game tree)
    print(f"[MINIMAX] Computing best move for O with depth 9 (mode: {mode})...")
    minimax_value = Node.minimax(node, 9, Node.O)
    
    if node.best is None:
        print("[MINIMAX] No best move found!")
        return None
    
    # Find which position changed
    for i in range(9):
        if node.etat[i] != node.best.etat[i]:
            print(f"[MINIMAX] Best move: position {i} (evaluation: {minimax_value})")
            return i
    
    return None

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get server statistics including Minimax usage"""
    return jsonify({
        'total_sessions': len(game_sessions),
        'active_sessions': sum(1 for g in game_sessions.values() if not check_game_over(g['board'])[0]),
        'minimax': {
            'total_calls': minimax_stats['total_calls'],
            'hybrid_calls': minimax_stats['hybrid_mode_calls'],
            'vs_ml_calls': minimax_stats['vs_ml_mode_calls']
        }
    })

@app.route('/api/minimax/info', methods=['GET'])
def minimax_info():
    """Get Minimax configuration and statistics"""
    return jsonify({
        'status': 'active',
        'depth': 9,
        'algorithm': 'Minimax with Alpha-Beta pruning',
        'modes': ['vs_ml', 'hybrid'],
        'statistics': minimax_stats,
        'description': 'Minimax is connected to both vs_ml and hybrid modes. The AI plays as O and computes optimal moves.'
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    print("Starting Tic-Tac-Toe AI API Server...")
    print("=" * 60)
    print("Minimax Algorithm ACTIVE")
    print("Modes: 2_players, hybrid, vs_ml")
    print("Hybrid Mode: AI plays automatically (uses Minimax)")
    print("VS ML Mode: AI plays automatically (uses Minimax)")
    print("Minimax Depth: 9 (full game tree)")
    print("=" * 60)
    print("Check /api/minimax/info for configuration details")
    print("Check /api/stats for usage statistics")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
