import tkinter as tk
from tkinter import filedialog
import torch
import numpy
import string
import time
import os
from board_detector.chessposition import Utils
from stockfish.stockfish import Stockfish, StockfishException
stockfish = Stockfish()


class SeeToSolve():
    def __init__(self, playing):
        if playing != "b":
            self.playing = "w"
        else:
            self.playing = "b"
        print(self.playing)
        self.image_path = None
        self.model_path = "board_detector/models/position_predict.pt"
        self.my_model = torch.jit.load(self.model_path)
        self.rename = True

    @staticmethod
    def fen_to_positions(fen):
        label_array = []
        for i in fen:
            if str.isdigit(i):
                label_array += numpy.zeros(int(i), numpy.int16).tolist()
            elif i != "-":
                label_array.append(i)
        return label_array

    @staticmethod
    def annotated_move(fen, move):
        position_array = SeeToSolve.fen_to_positions(fen)
        start_position = string.ascii_lowercase.index(move[0]) + 8 * (8 - int(move[1]))
        end_position = string.ascii_lowercase.index(move[2]) + 8 * (8 - int(move[3]))

        piece_names = {"p": "Pawn", "b": "Bishop", "n": "Knight", "r": "Rook", "k": "King", "q": "Queen"}

        moving_piece_desc = piece_names[position_array[start_position].lower()]

        if not str.isdigit(str(position_array[end_position])):
            end_piece_desc = piece_names[position_array[end_position].lower()]
            print("Move", moving_piece_desc, "on", move[0:2], "to take", end_piece_desc, "on", move[2:4])
        else:
            print("Move", moving_piece_desc, "on", move[0:2], "to", move[2:4])

    @staticmethod
    def get_last_image(dirpath, image_ext=('jpg','jpeg','png')):
            files = [os.path.join(dirpath, filename) for filename in os.listdir(dirpath)]
            valid = [f for f in files if '.' in f and f.rsplit('.',1)[-1] in image_ext and os.path.isfile(f)]
            if valid:
                return max(valid, key=os.path.getmtime)

    def recommend_move(self):
        fen = Utils.pred_single_img(self.model_path, self.image_path)
        if self.playing == "b":
            fen = fen[::-1]
        print(fen)
        new_fen = fen.replace("-", "/")  + " " + self.playing
        # print(stockfish.get_board_visual())
        valid_move = True
        try:
            stockfish.set_fen_position(new_fen)
            best_move = stockfish.get_best_move()
        except StockfishException:
            best_move = None
            valid_move = False
        if not valid_move:
            print("no valid moves - checkmate?")
        else:
            self.annotated_move(fen, best_move)
        if self.rename:
            original = self.image_path
            new_name = os.path.dirname(self.image_path) + "/" + fen + " " +  str(time.time()) + ".png"
            os.rename(original, new_name)
            self.image_path = new_name

    def check_for_new_image(self):
        new_image = self.get_last_image(screenshot_path)
        if self.image_path is None or new_image != self.image_path:
            self.image_path = new_image
            self.recommend_move()

if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()
    screenshot_path = filedialog.askdirectory()
    playing = input("are you playing White (w) or Black (b)?").lower()
    see_to_solve = SeeToSolve(playing)
    starttime = time.time()
    interval = 0.5 # seconds
    while True:
        see_to_solve.check_for_new_image()
        time.sleep(interval - ((time.time() - starttime) % interval))
