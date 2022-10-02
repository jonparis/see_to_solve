import tkinter as tk
from tkinter import filedialog
import torch
import cv2
import numpy
from board_detector.chessposition import Utils
from stockfish import Stockfish, StockfishException
stockfish = Stockfish()


if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()
    image_path = filedialog.askopenfilename()
    print("image Path", image_path)
    model_path = "board_detector/models/position_predict_20.pt"
    my_model = torch.jit.load(model_path)
    print(model_path, "model loaded")
    my_model.eval()
    print(model_path, "ready for evaluation")

    img_unprocessed = cv2.imread(image_path)
    my_image = Utils.img_processing(img_unprocessed)

    # cv2.destroyAllWindows()  # destroy all windows
    img_array = []
    img_array.extend(my_image)
    my_pred_label = my_model(torch.FloatTensor(img_array))
    my_pred_label = \
        my_pred_label.view(len(my_pred_label), -1).argmax(1).cpu().numpy().astype(numpy.int32).tolist()


    fen = Utils.lb_to_fen(my_pred_label)
    print(fen)
    new_fen = fen.replace("-", "/")
    print(new_fen)

    white_fen = new_fen.strip() + " w"
    black_fen = new_fen.strip() + " b"
    white_valid = stockfish.is_fen_valid(white_fen)
    black_valid = stockfish.is_fen_valid(black_fen)
    stockfish.set_fen_position(white_fen)
    # print(stockfish.get_board_visual())
    white_valid = white_valid = True

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