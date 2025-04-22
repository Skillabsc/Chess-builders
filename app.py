from flask import Flask, request, jsonify
import chess
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
board = chess.Board()

def evaluate_board(board):
    if board.is_checkmate():
        return -9999 if board.turn == chess.WHITE else 9999
    if board.is_stalemate() or board.is_insufficient_material():
        return 0
    piece_values = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0}
    score = 0
    for piece in board.piece_map().values():
        score += piece_values[piece.piece_type] if piece.color == chess.WHITE else -piece_values[piece.piece_type]
    return score

def minimax(board, depth, alpha, beta):
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)
    legal_moves = list(board.legal_moves)
    if board.turn == chess.WHITE:
        max_eval = float('-inf')
        for move in legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta)
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for move in legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta)
            board.pop()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

def get_ai_move(board, depth=3):
    best_move = None
    best_value = float('-inf')
    legal_moves = list(board.legal_moves)
    for move in legal_moves:
        board.push(move)
        value = minimax(board, depth - 1, float('-inf'), float('inf'))
        board.pop()
        if value > best_value:
            best_value = value
            best_move = move
    return best_move

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/move', methods=['POST'])
def make_move():
    global board
    data = request.get_json()
    move_uci = data.get('move')
    try:
        move = chess.Move.from_uci(move_uci)
        if move in board.legal_moves:
            board.push(move)
            ai_move = get_ai_move(board)
            if ai_move:
                board.push(ai_move)
                return jsonify({'status': 'success', 'fen': board.fen(), 'ai_move': ai_move.uci()})
            return jsonify({'status': 'game_over', 'fen': board.fen()})
        return jsonify({'status': 'invalid_move'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/reset', methods=['POST'])
def reset_board():
    global board
    board = chess.Board()
    return jsonify({'status': 'success', 'fen': board.fen()})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 
