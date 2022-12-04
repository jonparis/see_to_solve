import tkinter as tk
from tkinter import filedialog
import torch
import numpy
import string
import time
import os
from board_detector.chessposition import Utils, CONST
from stockfish.stockfish import Stockfish, StockfishException
from configparser import ConfigParser
stockfish = Stockfish()

class SeeToSolve():
    def __init__(self):
        self.screenshots_path = self.get_screenshots_path()
        self.image_path = None
        self.model_path = "board_detector/models/position_predict_stable.pt"
        self.my_model = torch.jit.load(self.model_path)
        self.rename = True
        self.playing = None

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

    
    def get_screenshots_path(self):
        config = ConfigParser()

        if os.path.exists("config.ini"):
            config.read("config.ini")
            try:
                screenshots_path = config["DEFAULTS"]["screenshots_path"]
            except:
                print("Please select the folder where screenshots are saved")
                screenshots_path = filedialog.askdirectory(title="Please select the folder where screenshots are saved:")
                self.save_screenshots_path(screenshots_path)
        else:
            print("Please select the folder where screenshots are saved")
            screenshots_path = filedialog.askdirectory(title="Please select the folder where screenshots are saved:")
            self.save_screenshots_path(screenshots_path)

        return screenshots_path
   
    def save_screenshots_path(self, screenshots_path):
        config = ConfigParser()
        config["DEFAULTS"] = {"screenshots_path": screenshots_path}
        with open('config.ini', 'w') as conf:
            config.write(conf)

    def get_last_image(self, image_ext=('jpg','jpeg','png')):
            files = [os.path.join(self.screenshots_path, filename) for filename in os.listdir(self.screenshots_path)]
            valid = [f for f in files if '.' in f and f.rsplit('.',1)[-1] in image_ext and os.path.isfile(f)]
            if valid:
                return max(valid, key=os.path.getmtime)

    def set_playing(self, fen):
        if self.playing != None: 
            return
        playing_black = Utils.playing_black(fen)
        if playing_black == True: 
            self.playing = "b"
        elif playing_black == False:
            self.playing = "w"
        else:
            playing = input("are you playing White (w) or Black (b)?").lower()
            if playing != "b":
                self.playing = "w"
            else:
                self.playing = "b"
        print(self.playing)





    def recommend_move(self):
        pred_fen = fen = Utils.pred_single_img(self.model_path, self.image_path)
        self.set_playing(pred_fen)
        if self.playing == "b":
            fen = fen[::-1]
        new_fen = fen.replace("-", "/")  + " " + self.playing
        best_move = False
        is_valid = True        
        
        try:
            stockfish.set_fen_position(new_fen)
        except StockfishException:
            is_valid = False
            print("crash when setting fen")
        
        if is_valid:
            try:
                best_move = stockfish.get_best_move()
            except StockfishException:
                print('crash when getting best move')
                best_move = False
        else:
            print("not a valid fen:", new_fen)

        try:
            if self.playing == "b": 
                print(stockfish.get_board_visual(False))
            else:
                print(stockfish.get_board_visual())
        except StockfishException:
            print("crash when printing visual")
        

        if not best_move:
            print("no valid moves - checkmate?")
            stockfish.set_fen_position(new_fen)
        else:
            self.annotated_move(fen, best_move)
        if self.rename:
            original = self.image_path
            new_name = os.path.dirname(self.image_path) + "/" + pred_fen + " " +  str(time.time()) + ".png"
            os.rename(original, new_name)
            self.image_path = new_name

    def check_for_new_image(self):
        new_image = self.get_last_image()
        if self.image_path is None or new_image.split()[0] != self.image_path.split()[0]:
            self.image_path = new_image
            self.recommend_move()

if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()
    see_to_solve = SeeToSolve()
    starttime = time.time()
    interval = 0.5 # seconds
    while True:
        see_to_solve.check_for_new_image()
        time.sleep(interval - ((time.time() - starttime) % interval))

