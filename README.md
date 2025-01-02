# see_to_solve

Tool to detect a chess board position given an image.

## Setup
```
pip install opencv-python torch torchvision scikit-learn matplotlib stockfish

```
Install the Chrome Extension
1. Go to Extensions. chrome://extensions/
2. Enable "Developer mode"
3. Load unpacked
4. Select the directory of the "see_to_solve_chrome_ext"


## How to use

```
python main.py
```

The tool has two modes:

**A. Train and test a new model**
- Takes the images in the image folder and trains the model.

**B. Evaluate a model**
- This looks at a previous model and evalutes using the data in the image folder.

To-do:

a. Expand images and image preparation to include larger variety of chess boards including real world boards.
b. Build method to take a single image and preduce a [FEN](https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation).
c. Connect to Stockfish or another chess engine to get a recommended move (or moves) based on the supplied FEN.

## Notes and Acknowledgement
This tools borrows substantially from a Kaggle.com Notebook and dataset found [here](https://www.kaggle.com/code/ashwinbhatt/improved-version-using-pytorch/notebook).


