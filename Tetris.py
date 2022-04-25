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
 
rowWidth = 10
rowHeight = 20
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
            ["  X ",
             "  XX",
             "   X",
             "    "]
        ],
    "Z" : [
            ["    ",
             " XX ",
             "  XX",
             "    "],
            ["   X",
             "  XX",
             "  X ",
             "    "]
         ],
    "I" : [
            ["    ",
             "XXXX",
             "    ",
             "    "],
            ["  X ",
             "  X ",
             "  X ",
             "  X "]
        ],
    "Square" : [["    ",
                 " XX ",
                 " XX ",
                 "    "]],
    "J" : [
            ["    ",
             " XXX",
             "   X",
             "    "],
            ["  X ",
             "  X ",
             " XX ",
             "    "],
            [" X  ",
             " XXX",
             "    ",
             "    "],
            ["  XX",
             "  X ",
             "  X ",
             "    "]
        ], 
    "L" : [
            ["    ",
             " XXX",
             " X  ",
             "    "],
            [" XX ",
             "  X ",
             "  X ",
             "    "],
            ["   X",
             " XXX",
             "    ",
             "    "],
            ["  X ",
             "  X ",
             "  XX",
             "    "]
        ], 
    "T" : [
            ["    ",
             " XXX",
             "  X ",
             "    "],
            ["  X ",
             " XX ",
             "  X ",
             "    "],
            ["  X ",
             " XXX",
             "    ",
             "    "],
            ["  X ",
             "  XX",
             "  X ",
             "    ",]
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
    y = -1

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
        self.x -= 1
    def MovePieceRight(self):
        # TODO Check for collision
        self.x += 1
    def MovePieceDown(self):
        self.y += 1
    def MovePieceUp(self):
        self.y -= 1
    def MovePiece(self, x, y):
        self.x = x
        self.y = y
    
    
class BoardSquare(object):
    PieceColor = None
    numOccupied = None
    PreviousColor = None
    def __init__(self, PieceColor, numOccupied):
        self.PieceColor = PieceColor
        self.numOccupied = numOccupied
        self.PreviousColor = (0,0,0)

class Board(object):
    # Create 2d array of BoardSquares of size rowWidth x RowHeight for tetris board
    # Num Occupied = 1 defines that space is occupied, 0 defines it is unoccupied, numOccupied > 1 means pieces are intersecting
    board = [[BoardSquare((0,0,0), 0) for x in range(rowWidth)] for y in range(rowHeight)]
    
    currentPiece = None
    holdPiece = None
    nextPiece = None
    score = 0

    def __init__(self):
        self.currentPiece = Piece()
        self.nextPiece = Piece()
        self.holdPiece = None

        self.OccupyBoard()

    # Checks if any squares have more than 1 piece in it
    def CheckInterSections(self):
        for x in range(rowWidth):
            for y in range(rowHeight):
                if self.board[y][x].numOccupied > 1:
                    return True
        
        return False
                
    # Check if piece will go out of bounds
    def CheckBoundaries(self):
        for x in range(len(self.currentPiece.currentShape[0])):
            for y in range(len(self.currentPiece.currentShape)):
                if self.currentPiece.currentShape[y][x] == 'X':
                    if (self.currentPiece.x + x) >= rowWidth or (self.currentPiece.x + x) < 0 or (self.currentPiece.y + y) >= rowHeight:
                        return True
        return False

    def UnoccupyBoard(self):
        num = 1
        for x in range(len(self.currentPiece.currentShape[0])):
            for y in range(len(self.currentPiece.currentShape)):
                if self.currentPiece.currentShape[y][x] == 'X' and not self.CheckBoundaries():
                    self.board[y + self.currentPiece.y][x + self.currentPiece.x].numOccupied -= 1
                    self.board[y + self.currentPiece.y][x + self.currentPiece.x].PieceColor = self.board[y + self.currentPiece.y][x + self.currentPiece.x].PreviousColor
                    self.board[y + self.currentPiece.y][x + self.currentPiece.x].PreviousColor = (0,0,0)


    
    def OccupyBoard(self):
        for x in range(len(self.currentPiece.currentShape[0])):
            for y in range(len(self.currentPiece.currentShape)):
                if self.currentPiece.currentShape[y][x] == 'X' and not self.CheckBoundaries():
                    self.board[y + self.currentPiece.y][x + self.currentPiece.x].numOccupied += 1
                    self.board[y + self.currentPiece.y][x + self.currentPiece.x].PreviousColor = self.board[y + self.currentPiece.y][x + self.currentPiece.x].PieceColor
                    self.board[y + self.currentPiece.y][x + self.currentPiece.x].PieceColor = self.currentPiece.GetColor()

    # Returns True if location of piece is not occupied
    def GenerateNewPiece(self, isHoldPiece):
        if not isHoldPiece:
            self.currentPiece = self.nextPiece
            self.nextPiece = Piece()
            
        elif self.holdPiece == None:
            self.UnoccupyBoard()
            self.holdPiece = Piece(self.currentPiece.currentPieceType)
            self.currentPiece = self.nextPiece()
            
        else:
            temp = self.currentPiece
            self.UnoccupyBoard()
            self.currentPiece = Piece(self.holdPiece.currentPieceType)
            self.holdPiece = Piece(temp.currentPieceType)
        
        if self.CheckInterSections():
            return False
        else:
            return True
        
    # Draw the lines where each piece can be
    def DrawGrid(self):
        for x in range(topLeftX, topLeftX + rowWidth * blockSize, blockSize):
            for y in range(topLeftY, topLeftY + rowHeight * blockSize, blockSize):
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
        for x in range(rowWidth):
            for y in range(rowHeight):
                if self.board[y][x].PieceColor != (0,0,0):
                    rect = pygame.Rect(topLeftX + x * blockSize, topLeftY + y * blockSize, blockSize, blockSize)
                    pygame.draw.rect(screen, self.board[y][x].PieceColor, rect)

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
                if rowsComplete[i - 1] + 1 == rowsComplete[i]:
                    tetrisCheck += 1
                else:
                    tetrisCheck = 0
            if tetrisCheck == 4:
                # Apply tetris score modifer
                pass
        # expecting index out of bounds
        except:
            pass

    def MoveDown(self):
        intersections = False
        self.UnoccupyBoard()
        self.currentPiece.MovePieceDown()
        self.OccupyBoard()
        if self.CheckBoundaries() or self.CheckInterSections():
            self.UnoccupyBoard()
            self.currentPiece.MovePieceUp()
            self.OccupyBoard()
            self.GenerateNewPiece(False)

        return

    def MoveLeft(self):
        self.UnoccupyBoard()
        self.currentPiece.MovePieceLeft()
        self.OccupyBoard()
        if self.CheckBoundaries() or self.CheckInterSections():
            self.UnoccupyBoard()
            self.currentPiece.MovePieceRight()
            self.OccupyBoard()

        return
        
    def MoveRight(self):
        self.UnoccupyBoard()
        self.currentPiece.MovePieceRight()
        self.OccupyBoard()
        if self.CheckBoundaries() or self.CheckInterSections():
            self.UnoccupyBoard()
            self.currentPiece.MovePieceLeft()
            self.OccupyBoard()

        return

    def MovePiece(self, x, y):
        self.currentPiece.SetLocation(x, y)

    def RotateClockWise(self):
        self.UnoccupyBoard()
        self.currentPiece.RotateClockwise()
        self.OccupyBoard()
        if self.CheckBoundaries() or self.CheckInterSections():
            self.UnoccupyBoard()
            self.currentPiece.RotateCouterClockwise()
            self.OccupyBoard()

    def RotateCounterClockWise(self):
        self.UnoccupyBoard()
        self.currentPiece.RotateCouterClockwise()
        self.OccupyBoard()
        if self.CheckBoundaries() or self.CheckInterSections():
            self.UnoccupyBoard()
            self.currentPiece.RotateClockwise()
            self.OccupyBoard()

    def HoldPiece(self):
        if not board.GenerateNewPiece(True):
            # Game Over
            pass

 
if __name__ == "__main__":
    # Initialize game window
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((windowWidth,windowHeight))
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()
    
    # Initilize Board
    board = Board()
    running = True
    
    # Initialize block move timer
    move_down_event = pygame.USEREVENT
    moveDownTick = 1000
    pygame.time.set_timer(move_down_event, moveDownTick)
    while running:

        # --- events ---
        screen.fill((0,0,0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # TODO Pause menu
                    running = False
                elif event.key == pygame.K_SPACE:
                    board.MovePiece(board.CalculatePieceGhostPostion())
                    # instant place
                    pass
                elif event.key == pygame.K_e:
                    # rotate clockwise
                    board.RotateClockWise()

                elif event.key == pygame.K_q:
                    # rotate couter clockwise
                    board.RotateCounterClockWise()

            # Block move timed event
            elif event.type == move_down_event:
               board.MoveDown()

        # Check if key is held down for movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_DOWN]:
            # move piece downward faster
            board.MoveDown()
        if keys[pygame.K_LEFT]:
            # move piece left while held
            board.MoveLeft()

        if keys[pygame.K_RIGHT]:
            # move piece right while held
            board.MoveRight()

        # --- updates ---
        board.DrawBoard()
        board.DrawGrid()
        board.DrawHoldBox()
        board.DrawNextPieces()
        board.DrawScoreBox()
        pygame.display.update()
        clock.tick(10)
