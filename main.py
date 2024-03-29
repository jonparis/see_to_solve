import tkinter as tk
from tkinter import filedialog
import torch
import numpy
import string
import time
import os
import random
from board_detector.chessposition import Utils, CONST
from stockfish.stockfish import Stockfish, StockfishException
from configparser import ConfigParser
stockfish = Stockfish()

DELETE_DUP = "delete_dup"
DEBUG = True

class SeeToSolve():
    def __init__(self):
        self.screenshots_path = self.get_screenshots_path()
        self.image_path = None
        self.model_path = "board_detector/models/position_predict_latest.pt"
        self.my_model = torch.jit.load(self.model_path)
        self.rename = True
        self.playing = None
        self.last_fen = None
        self.current_fen = None
        self.interval = 1

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
        
        if not str.isdigit(str(position_array[end_position])):
            end_piece_desc = piece_names[position_array[end_position].lower()]
            print("Move", moving_piece_desc, "on", move[0:2], "to take", end_piece_desc, "on", move[2:4], extra_info)
        else:
            print("Move", moving_piece_desc, "on", move[0:2], "to", move[2:4], extra_info)

    
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
        
    def recommend_move(self):
        pred_fen = fen = Utils.pred_single_img(self.model_path, self.image_path)
        if pred_fen == self.last_fen:
            return DELETE_DUP
        else:
            self.last_fen = pred_fen
        self.set_playing(pred_fen)
        if self.playing == "b":
            fen = fen[::-1]
        self.current_fen = fen.replace("-", "/") + " " + self.playing
        potential_moves = False
        is_valid = True        
        
        try:
            stockfish.set_fen_position(self.current_fen)
        except StockfishException:
            is_valid = False
            if DEBUG: print("crash when setting fen")
            stockfish.send_quit_command()
            self.interval = 5
            return False

        try:
            if self.playing == "b": 
                print(stockfish.get_board_visual(False))
            else:
                print(stockfish.get_board_visual())
        except StockfishException:
            if DEBUG: print("crash when printing visual:",  self.current_fen)
            stockfish.send_quit_command()
            return False
        
        if is_valid:
            try:
                potential_moves = self.get_good_enough_move()  # (stockfish.get_best_move())
            except StockfishException:
                if DEBUG: print('crash when getting best move',  self.current_fen)
                stockfish.send_quit_command()
                potential_moves = False
                self.interval = 5
                return False
        else:
            print("not a valid fen (" +  self.current_fen + ")")

        if potential_moves:
            i = 0
            for m in potential_moves:
                if i > 0:
                    print(' or ')
                self.annotated_move(fen, m)
                i = 1

        if self.rename:
            original = self.image_path
            new_name = os.path.dirname(self.image_path) + "/" + pred_fen + " " +  str(time.time()) + ".png"
            os.rename(original, new_name)
            self.image_path = new_name

        return True

    def get_good_enough_move(self):
        stockfish.set_fen_position(self.current_fen)
        good_moves = stockfish.get_top_moves(2)

        # if best move is Mate in 2 or better use it!
        if len(good_moves) < 2 or (good_moves[0]['Mate'] and good_moves[0]['Mate'] < 3):
            return [good_moves[0]]

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


    def check_for_new_image(self):
        new_image = self.get_last_image()
        if new_image and (self.image_path is None or new_image.split()[0] != self.image_path.split()[0]):
            self.image_path = new_image
            if self.recommend_move() == DELETE_DUP:
                os.remove(new_image)  # Delete image if we have seen it before
    
    def fix_images(self):
        files = [os.path.join(self.screenshots_path, filename) for filename in os.listdir(self.screenshots_path)]
        for original in files:
            filename = os.path.basename(original)
            new_name = os.path.dirname(original) + "/" + filename.replace("/", "-").replace(":", "-")
            os.rename(original, new_name)

    def update_interval(self):
        if self.interval > 1:
            self.interval -= 1


if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()
    see_to_solve = SeeToSolve()
    starttime = time.time()
    see_to_solve.interval
    while True:
        # see_to_solve.fix_images()  # use to fix images created through other mechanism
        see_to_solve.check_for_new_image()
        time.sleep(see_to_solve.interval - ((time.time() - starttime) % see_to_solve.interval))
        see_to_solve.update_interval()

