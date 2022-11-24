import tkinter as tk
from tkinter import filedialog
import torch
import time
import os
from board_detector.chessposition import Utils
from stockfish.stockfish import Stockfish, StockfishException
stockfish = Stockfish()


class SeeToSolve:
    def __init__(self):
        self.image_path = None
        self.model_path = "board_detector/models/position_predict.pt"
        self.my_model = torch.jit.load(self.model_path)

    @staticmethod
    def get_last_image(dirpath, image_ext=('jpg','jpeg','png')):
            files = [os.path.join(dirpath, filename) for filename in os.listdir(dirpath)]
            valid = [f for f in files if '.' in f and f.rsplit('.',1)[-1] in image_ext and os.path.isfile(f)]
            if valid:
                return max(valid, key=os.path.getmtime)

    def recommend_move(self):
        fen = Utils.pred_single_img(self.model_path, self.image_path)
        print(fen)
        new_fen = fen.replace("-", "/")
        white_fen = new_fen.strip() + " w"
        black_fen = new_fen.strip() + " b"
        white_valid = stockfish.is_fen_valid(white_fen)
        black_valid = stockfish.is_fen_valid(black_fen)
        stockfish.set_fen_position(white_fen)
        # print(stockfish.get_board_visual())
        white_valid = black_valid = True
        try:
            stockfish.set_fen_position(white_fen)
            whites_best_move = stockfish.get_best_move()
        except StockfishException:
            whites_best_move = "Not a thing"
            white_valid = False
        # print(stockfish.get_board_visual())
        try:
            stockfish.set_fen_position(black_fen)
            blacks_best_move = stockfish.get_best_move()
        except StockfishException:
            blacks_best_move = "Not a thing"
            black_valid = False
        if not black_valid and not white_valid:
            print("no valid moves - checkmate?")
        else:
            if white_valid: print("white's best move: ", whites_best_move)
            if black_valid: print("black's best move: ", blacks_best_move)

    def check_for_new_image(self):
        new_image = self.get_last_image(screenshot_path)
        if self.image_path is None or new_image != self.image_path:
            self.image_path = new_image
            self.recommend_move()

if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()
    screenshot_path = filedialog.askdirectory()
    see_to_solve = SeeToSolve()
    starttime = time.time()
    interval = 1.0 # seconds
    while True:
        see_to_solve.check_for_new_image()
        time.sleep(interval - ((time.time() - starttime) % interval))

