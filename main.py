import tkinter as tk
from tkinter import filedialog
import torch
import numpy
import cv2
import string
import time
import os
from stockfish import Stockfish, StockfishException
from configparser import ConfigParser
from flask import Flask, request, jsonify
from flask_cors import CORS


# Update this path to where you placed stockfish.exe
# comment out for Mac
stockfish = Stockfish(path="stockfish.exe")

DELETE_DUP = "delete_dup"
DEBUG = True


class CONST:
    PIECES = ["k", "q", "r", "b", "n", "p", "K", "Q", "R", "B", "N", "P"]

    PIECES_LEN = 12
    img_dim = 25


    if torch.cuda.is_available():
        device = torch.device("cuda:0")
    elif torch.backends.mps.is_available():
        device = torch.device("mps")
    else:
        device  = torch.device("cpu")

class Utils():
    @staticmethod
    def playing_black(fen):
        '''
        returns
        b, if playing black
        w, if paying white
        None, if unknown
        '''
        balance = 0  # when balance < 0 assume from black perspective
        n = 1
        total = 0

        fen_array = fen.split("-")
        for row in range(0,8):
            if row > 3:
                n = -1
            for i in fen_array[row]:
                if i.islower():
                    total += 1
                    balance += n
                elif i.isupper():
                    balance -= n
                    total += 1
        if total > 10:
            if balance < -2:
                return "b"
            elif balance > 2:
                return "w"
        return None
    
    @staticmethod
    def lb_to_fen(label):
        s = ''
        count = 0
        for i in range(len(label)):
            if i % 8 == 0:
                if count != 0:
                    s = s + str(count)
                    count = 0
                s = s + '-'
            if label[i] == 0:
                count = count + 1
            else:
                if count != 0:
                    s = s + str(count)
                    count = 0

                if 0 < label[i] <= CONST.PIECES_LEN:
                    s = s + CONST.PIECES[label[i] - 1]
                else:
                    print('Invalid Error#######################################')
        if count != 0:
            s = s + str(count)
        return s[1:]
    
    @staticmethod
    def img_processing(img):
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img_shrink = cv2.resize(img_gray, (200, 200))
        box_list = Utils.blockshaped(img_shrink, CONST.img_dim, CONST.img_dim)
        flatten_list = box_list.reshape(box_list.shape[0], -1)
        return flatten_list
    
    @staticmethod
    def blockshaped(arr, nrows, ncols):
        h, w = arr.shape
        return (arr.reshape(h // nrows, nrows, -1, ncols)
                .swapaxes(1, 2)
                .reshape(-1, nrows, ncols))
    
        return Utils.lb_to_fen(my_pred_label)
    
    @staticmethod
    def pred_single_img(model_path, file):
        my_model = torch.jit.load(model_path)
        my_model.to(CONST.device)  # make sure on device
        my_model.eval()

        # Read the file's bytes directly into memory
        file_bytes = file.read()

        # Convert the bytes data to a NumPy array
        np_arr = numpy.frombuffer(file_bytes, numpy.uint8)

        # Decode the NumPy array to an image
        img_unprocessed = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        my_image = Utils.img_processing(img_unprocessed)

        img_array = numpy.array(my_image)  # Convert to numpy array first
        with torch.no_grad():  # Add this for inference
            my_pred_label = my_model(torch.FloatTensor(img_array).to(CONST.device))
            my_pred_label = torch.log_softmax(my_pred_label, dim=1)  # Explicitly specify dimension
            my_pred_label = my_pred_label.argmax(1).cpu().numpy().astype(numpy.int32).tolist()

        return Utils.lb_to_fen(my_pred_label)

class SeeToSolve():

    def __init__(self):
        self.image_path = None
        self.image_file = None
        self.model_path = "position_predict.pt"
        self.my_model = torch.jit.load(self.model_path)
        self.print_board = True
        self.playing = None
        self.last_fen = None
        self.current_fen = None

    @staticmethod
    def fen_to_positions(fen):
        label_array = []
        for i in fen:
            if str.isdigit(i):
                label_array += ['0'] * int(i)
            elif i != "-":
                label_array.append(i)
        return label_array

    @staticmethod
    def annotated_move(fen, good_move_item):
        move = good_move_item['Move']
        centipawn = good_move_item['Centipawn']
        mate_in = good_move_item['Mate']
        position_array = SeeToSolve.fen_to_positions(fen)
        start_position = string.ascii_lowercase.index(move[0]) + 8 * (8 - int(move[1]))
        end_position = string.ascii_lowercase.index(move[2]) + 8 * (8 - int(move[3]))

        piece_names = {"p": "Pawn", "b": "Bishop", "n": "Knight", "r": "Rook", "k": "King", "q": "Queen"}

        moving_piece_desc = piece_names[position_array[start_position].lower()]

        extra_info = "("
        advantage = "white"  # default
        if (centipawn and centipawn < 0) or (mate_in and mate_in < 0):
            advantage = "black"

        if centipawn is None:
            pass
        elif centipawn == 0:
            extra_info += "even game"
        else:
            extra_info += advantage + " +" + str(abs(centipawn))

        if not mate_in:
            pass
        else:
            extra_info += advantage + " mate in " + str(abs(mate_in))

        extra_info += ")"
        
        if position_array[end_position] != '0':  # Check if target square is not empty
            end_piece_desc = piece_names[position_array[end_position].lower()]
            response = "Take " + end_piece_desc + " (" + move[2:4] + ") with " + moving_piece_desc + " (" + move[0:2] + ") " + extra_info
        else:
            response = "Move " + moving_piece_desc + " (" + move[0:2] + ") to (" + move[2:4] + ") " + extra_info
        print(response)
        return(response)
   
    def get_last_image(self, image_ext=('jpg','jpeg','png')):
            files = [os.path.join(self.screenshots_path, filename) for filename in os.listdir(self.screenshots_path)]
            valid = [f for f in files if '.' in f and f.rsplit('.',1)[-1] in image_ext and os.path.isfile(f)]
            if valid:
                return max(valid, key=os.path.getmtime)
            return False

    def set_playing(self, fen):
        playing_black_or_white = Utils.playing_black(fen)
        if self.playing == None and playing_black_or_white == None:
            playing = input("are you playing White (w) or Black (b)?").lower()
            if playing != "b":
                self.playing = "w"
            else:
                self.playing = "b"
        elif playing_black_or_white != None:
            if self.playing != playing_black_or_white:
                print("Playing:", playing_black_or_white)
            self.playing = playing_black_or_white
        return
    
    def print_board_to_console(self):
        try:
            if self.playing == "b": 
                print(stockfish.get_board_visual(False))
            else:
                print(stockfish.get_board_visual())
        except StockfishException:
            if DEBUG: 
                print("crash when printing visual:",  self.current_fen)
                response = {"error": "unexpected error"}
            stockfish.send_quit_command()
            return response    
        
    def recommend_move(self):
        pred_fen = fen = Utils.pred_single_img(self.model_path, self.image_file)
        self.set_playing(pred_fen)
        if self.playing == "b":
            fen = fen[::-1]
        self.current_fen = fen.replace("-", "/") + " " + self.playing

        if pred_fen != self.last_fen:
            self.last_fen = pred_fen
        
        potential_moves = False
        is_valid = True        
        
        try:
            stockfish.set_fen_position(self.current_fen)
        except StockfishException:
            is_valid = False
            if DEBUG: print("crash when setting fen")
            stockfish.send_quit_command()
            return False

        if self.print_board: self.print_board_to_console()
        
        if is_valid:
            try:
                potential_moves = self.get_good_enough_move()  # (stockfish.get_best_move())
            except StockfishException:
                if DEBUG: print('crash when getting best move',  self.current_fen)
                stockfish.send_quit_command()
                potential_moves = False
                response = {"error": "unexpected error"}
                return False
        else:
            response = {"error": "not a valid fen (" +  self.current_fen + ")"}
            print(response)

        response = ""
        if potential_moves:
            i = 0
            for m in potential_moves:
                if i > 0:
                    print(' or ')
                    response += " or \n\n"
                response += self.annotated_move(fen, m)
                i = 1

        return response

    def get_good_enough_move(self):
        stockfish.set_fen_position(self.current_fen)
        good_moves = stockfish.get_top_moves(2)

        # if best move is Mate in 2 or better use it!
        if len(good_moves) < 2 or (good_moves[0]['Mate'] and good_moves[0]['Mate'] < 3):
            if len(good_moves) > 0:
                return [good_moves[0]]
            return False

        # if Centipawn doesn't exist return top move
        if not good_moves[0]['Centipawn'] or not good_moves[1]['Centipawn']:
            return [good_moves[0]]

        same_advantage = good_moves[0]['Centipawn'] * good_moves[1]['Centipawn'] >= 0
        move_centipawn_delta = abs(good_moves[0]['Centipawn'] - good_moves[1]['Centipawn'])

        # if Centipawn is similar across moves give options
        if same_advantage and move_centipawn_delta < 25:
            return good_moves
        else:
            return [good_moves[0]]

app = Flask(__name__)
see_to_solve = SeeToSolve()
CORS(app)  # Enables Cross-Origin Resource Sharing (CORS) for all routes

@app.route('/process-image', methods=['POST'])
def process_image():
    # Check if the request contains an 'image' file.
    if 'image' not in request.files:
        return jsonify({'error': 'No image part in the request'}), 400

    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    see_to_solve.image_file = file
    
    text_response = see_to_solve.recommend_move()

    return jsonify({'text': text_response})

if __name__ == '__main__':
    app.run(port=5000, debug=True)