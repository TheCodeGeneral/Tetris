#!\TermProject\Scripts\python
from dataclasses import dataclass
import pygame
import random
from collections import namedtuple 
 
# GLOBALS VARS
windowWidth = 800
windowHeight = 700
playWidth = 300  
playHeight = 600  
blockSize = 30
 
topLeftX = (windowWidth - playWidth) // 2
topLeftY = windowHeight - playHeight 
 
class Piece(object):
    # Shapes and their rotations
    # Each shape has an array of rotations
    # Each rotation is a 4x4 grid of whitespace and an X mark where each block will be
    PIECE_TYPES = {
    "S" : [
            ["    ",
             "  XX",
             " XX ",
             "    "],
            [" X  ",
             " XX ",
             "  X ",
             "    "]
        ],
    "Z" : [
            ["    ",
             " XX ",
             "  XX",
             "    "],
            ["  X ",
             " XX ",
             " X  ",
             "    "]
         ],
    "I" : [
            [" X  ",
             " X  ",
             " X  ",
             " X  "],
            ["    ",
             "XXXX",
             "    ",
             "    "]
        ],
    "Square" : [["    ",
                 " XX ",
                 " XX ",
                 "    "]],
    "J" : [
            ["    ",
             " X  ",
             " XXX",
             "    "],
            ["    ",
             " XX ",
             " X  ",
             " X  "],
            ["    ",
             "    ",
             " XXX",
             "   X"],
            ["    ",
             "  X ",
             "  X ",
             " XX ",
             "    "]
        ], 
    "L" : [
            ["    ",
             "   X",
             " XXX",
             "    "],
            ["    ",
             " X  ",
             " X  ",
             " XX "],
            ["    ",
             " XXX",
             " X  ",
             "    "],
            ["    ",
             " XX ",
             "  X ",
             "  X "]
        ], 
    "T" : [
            ["    ",
             "  X ",
             " XXX",
             "    "],
            ["    ",
             "  X ",
             "  XX",
             "  X "],
            ["    ",
             " XXX",
             "  X ",
             "    "],
            ["    ",
             "  X ",
             " XX ",
             "  X "]
        ]
    } 

    # RGB Values
    PIECE_COLORS = {
        "S" : (0, 255, 0), # Green
        "Z" : (255, 0, 0), # Red
        "I" : (0, 255, 255), # Cyan
        "Square" : (255, 255, 0), # Yellow
        "J" : (0, 0, 255), # Blue
        "L" : (255, 165, 0), # Orange
        "T" : (128, 0, 128) # Purple
    }
    # Used for random number generator
    PIECE_INDEX = {
        0 : "S",
        1 : "Z",
        2 : "I",
        3 : "Square",
        4 : "J",
        5 : "L",
        6 : "T"
    }
    currentPieceType = None
    currentShape = None
    currentRoationIndex = 0

    x = 3
    y = 0

    def __init__(self, shape = None):
        if shape == None:
            self.currentPieceType = self.PIECE_INDEX[random.randint(0,6)]
            self.currentShape = self.PIECE_TYPES[self.currentPieceType][0]
        else:
            self.currentPieceType = shape
            self.currentShape = self.PIECE_TYPES[shape]
    def RotateClockwise(self):
        try:
            if self.currentPieceType != "Square":
                # Try to choose previous rotation for piece type
                self.currentShape = self.PIECE_TYPES[self.currentPieceType][self.currentRoationIndex + 1]
                self.currentRoationIndex += 1

        except: # Expecting Index out of bounds
            # Choose lowest possible piece rotation
            self.currentRoationIndex = 0
            self.currentShape = self.PIECE_TYPES[self.currentPieceType][self.currentRoationIndex]

    def RotateCouterClockwise(self):
        try:
            if self.currentPieceType != "Square":
                # Try to choose previous rotation for piece type
                self.currentShape = self.PIECE_TYPES[self.currentPieceType][self.currentRoationIndex - 1]
                self.currentRoationIndex -= 1

        except: # Expecting Index out of bounds
            # Choose highest possible piece rotation
            self.currentRoationIndex = len(self.PIECE_TYPES[self.currentPieceType]) - 1
            self.currentShape = self.PIECE_TYPES[self.currentPieceType][self.currentRoationIndex]
    
    def GetColor(self):
        return self.PIECE_COLORS[self.currentPieceType]

    def MovePieceLeft(self):
        # TODO Check for collision
        self.x += 1
    def MovePieceRight(self):
        # TODO Check for collision
        self.x -= 1
    def MovePieceDown(self):
        self.y += 1
        
    def CheckForCollision(self):
        pass
        return True
    
    
class dumb(object):
    PieceColor = None
    numOccupied = None
    def __init__(self, PieceColor, numOccupied):
        self.PieceColor = PieceColor
        self.numOccupied = numOccupied

class Board(object):
    # Create 2d array of booleans of size 10x24 for tetris board
    # True defines that space is occupied, false defines it is unoccupied
    board = [[dumb((0,0,0), 0) for y in range(24)] for x in range(10)]
    oldPieces = []
    
    currentPiece = None
    holdPiece = None
    score = 0
    def CheckIfLost(self):
        # If piece is in the top 4 rows end game
        for x in range(10):
            for y in range(4):
                if self.board[x][y].numOccupied == 1:
                    return True
        
        return False
                
    def GenerateNewPiece(self, isHoldPiece):
        if not isHoldPiece:
            if self.currentPiece != None:
                self.oldPieces.append(self.currentPiece)
            self.currentPiece = Piece()
            
        elif self.holdPiece == None:
            self.holdPiece = self.currentPiece
            self.currentPiece = Piece()
            
        else:
            self.currentPiece, self.holdPiece = self.holdPiece, self.currentPiece
        
        #if CheckIfLost(self):
           # holdPiece = None
        
    def DrawPiece(self, piece):
        for x in range(len(piece.currentShape[0])):
            for y in range(len(piece.currentShape)):
                if piece.currentShape[y][x] == 'X':
                    rect = pygame.Rect(topLeftX + (piece.x + x)* blockSize, topLeftY + (piece.y + y) * blockSize, blockSize, blockSize)
                    pygame.draw.rect(screen, piece.GetColor(), rect)
    
    # Draw the lines where each piece can be
    def DrawGrid(self):
        for x in range(topLeftX, topLeftX + 10 * blockSize, blockSize):
            for y in range(topLeftY, topLeftY + 20 * blockSize, blockSize):
                rect = pygame.Rect(x, y, blockSize, blockSize)
                pygame.draw.rect(screen, (255, 255, 255), rect, 1)
                
    
                
    def DrawHoldBox(self):
        rect = pygame.Rect(0,0, 7 * blockSize, 7 * blockSize)
        pygame.draw.rect(screen, (255, 255, 255), rect, 1)
        # TODO Draw Hold under box
        # TODO Draaw Hold Piece in box
    
    def DrawNextPieces(self):
        rect = pygame.Rect(windowWidth - 7 * blockSize, 0, 7 * blockSize, 7 * blockSize)
        pygame.draw.rect(screen, (255, 255, 255), rect, 1)
        # TODO Draw next pieces under box
        # TODO Draw next piece in box
    
    def DrawScoreBox(self):
        rect = pygame.Rect(windowWidth // 2 - 2 * blockSize, 0, 4 * blockSize, 2 * blockSize)
        pygame.draw.rect(screen, (255, 255, 255), rect, 1)
        # TODO Draw Score under box
        # TODO Draw current score in box
    
    def DrawBoard(self):
        self.DrawPiece(self.currentPiece)
        for piece in self.oldPieces:
            self.DrawPiece(piece)

    # TODO Draw where the piece would be if placed instantly
    def CalculatePieceGhostPostion(self):
        pass
            
    def ClearRows(self):
        rowLength = len(self.board[0])
        rowsComplete = []
        for x in range(rowLength):
            numLines = 0
            for y in range(len(self.board)):
                if self.board[y][x].numOccupied >= 1:
                    numLines += 1
            if numLines == rowLength:
                rowsComplete.append(y)
        tetrisCheck = 0
        try:
            for i in range(1, len(rowsComplete)):
                if rowsComplete[i-1] + 1 == rowsComplete[i]:
                    tetrisCheck += 1
                else:
                    tetrisCheck = 0
            if tetrisCheck == 4:
                # Apply tetris score modifer
                pass
        # expecting index out of bounds
        except:
            pass
 
if __name__ == "__main__":
    # Initialize game window
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((windowWidth,windowHeight))
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()
    
    
    
    board = Board()
    board.GenerateNewPiece(False)
    running = True
    
    while running:

        # --- events ---
        board.DrawGrid()
        board.DrawBoard()
        board.DrawHoldBox()
        board.DrawNextPieces()
        board.DrawScoreBox()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                # - start moving -
                elif event.key == pygame.K_SPACE:
                    # instant place
                    pass
                elif event.key == pygame.K_DOWN:
                    # move piece downward faster
                    pass
                elif event.key == pygame.K_LEFT:
                    # move piece left while held
                    pass
                elif event.key == pygame.K_RIGHT:
                    # move piece right while held
                    pass
                elif event.key == pygame.K_E:
                    # rotate clockwise
                    pass
                elif event.key == pygame.K_Q:
                    # rotate couter clockwise
                    pass
                #elif event.key == 
        # --- updates ---
        pygame.display.update()
    


        #clock.tick(FPS)
        ## board.currentPiece.MoveDown()
        ## board.CheckCollisions
        ##
        ##
        ##
        ##