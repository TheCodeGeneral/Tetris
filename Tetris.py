#!\Tetris\Scripts\python
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

move_down_event = pygame.USEREVENT
end_game_event = pygame.USEREVENT + 1
 
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

    # Starting Position
    x = 3
    y = -1

    def __init__(self, shape = None):
        if shape == None:
            self.currentPieceType = self.PIECE_INDEX[random.randint(0,6)]
            self.currentShape = self.PIECE_TYPES[self.currentPieceType][0]
        else:
            self.currentPieceType = shape
            self.currentShape = self.PIECE_TYPES[shape][0]
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
    def RotateTo(self, index):
        self.currentShape = self.PIECE_TYPES[self.currentPieceType][index]

    def GetColor(self):
        return self.PIECE_COLORS[self.currentPieceType]

    def MovePieceLeft(self):
        self.x -= 1

    def MovePieceRight(self):
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
    def CheckIntersections(self):
        for x in range(rowWidth):
            for y in range(rowHeight):
                if self.board[y][x].numOccupied > 1:
                    return True
        
        return False
                
    # Check if piece will go out of bounds
    def CheckBoundaries(self, piece = None):
        if piece is None:
            piece = self.currentPiece
            if piece is None:
                return False
        for x in range(len(piece.currentShape[0])):
            for y in range(len(piece.currentShape)):
                if piece.currentShape[y][x] == 'X':
                    if (piece.x + x) >= rowWidth or (piece.x + x) < 0 or (piece.y + y) >= rowHeight:
                        return True
        return False

    # Remove piece from board and retore the squares to their previous color
    def UnoccupyBoard(self, piece = None):
        if piece is None:
            piece = self.currentPiece
        for x in range(len(piece.currentShape[0])):
            for y in range(len(piece.currentShape)):
                if piece.currentShape[y][x] == 'X' and not self.CheckBoundaries(piece):
                    self.board[y + piece.y][x + piece.x].numOccupied -= 1
                    self.board[y + piece.y][x + piece.x].PieceColor = self.board[y + piece.y][x + piece.x].PreviousColor
                    self.board[y + piece.y][x + piece.x].PreviousColor = (0,0,0)


    # Add piece to board and store their previous color
    def OccupyBoard(self, piece = None):
        if piece is None:
            piece = self.currentPiece
        for x in range(len(piece.currentShape[0])):
            for y in range(len(piece.currentShape)):
                if piece.currentShape[y][x] == 'X' and not self.CheckBoundaries(piece):
                    self.board[y + piece.y][x + piece.x].numOccupied += 1
                    self.board[y + piece.y][x + piece.x].PreviousColor = self.board[y + piece.y][x + piece.x].PieceColor
                    self.board[y + piece.y][x + piece.x].PieceColor = piece.GetColor()

    # Returns True if location of piece is not occupied
    def GenerateNewPiece(self, isHoldPiece = False):
        if not isHoldPiece:
            # Generate new piece
            self.currentPiece = self.nextPiece
            self.nextPiece = Piece()
            
        elif self.holdPiece == None:
            # Store current piece for the first time
            self.UnoccupyBoard()
            self.holdPiece = Piece(self.currentPiece.currentPieceType)
            self.currentPiece = self.nextPiece
            self.nextPiece = Piece()
            
        else:
            # Swap current piece and hold piece
            temp = Piece(self.currentPiece.currentPieceType)
            self.UnoccupyBoard()

            self.currentPiece = Piece(self.holdPiece.currentPieceType)
            self.holdPiece = temp
        
        board.ClearRows()
        self.OccupyBoard()
        if self.CheckIntersections():
            # New Piece is inside another end game
            EndGame()
        
    # Draw the lines where each piece can be
    def DrawGrid(self):
        for x in range(topLeftX, topLeftX + rowWidth * blockSize, blockSize):
            for y in range(topLeftY, topLeftY + rowHeight * blockSize, blockSize):
                rect = pygame.Rect(x, y, blockSize, blockSize)
                pygame.draw.rect(screen, (255, 255, 255), rect, 1)
                
    def DrawHoldBox(self):
        boxTopLeftX = blockSize
        boxTopLeftY = 3 * blockSize
        # Draw box
        rect = pygame.Rect(boxTopLeftX, boxTopLeftY, 5 * blockSize, 4 * blockSize)
        pygame.draw.rect(screen, (255, 255, 255), rect, 1)

        # Draw "Hold Piece" above box
        text = font.render("Hold Piece", True, (255, 255, 255))
        textRect = text.get_rect()
        textRect.x = boxTopLeftX
        textRect.y = boxTopLeftY - blockSize

        screen.blit(text, textRect)

        # Draw Piece in box
        if self.holdPiece is not None:
            for x in range(len(self.holdPiece.currentShape[0])):
                for y in range(len(self.holdPiece.currentShape)):
                    if self.holdPiece.currentShape[y][x] == 'X':
                        # Center piece in box
                        if self.holdPiece.currentPieceType == 'Square':
                            rect = pygame.Rect((blockSize // 2) + boxTopLeftX + x * blockSize, boxTopLeftY + y * blockSize, blockSize, blockSize)
                        elif self.holdPiece.currentPieceType == 'I':
                            rect = pygame.Rect((blockSize // 2) + boxTopLeftX + x * blockSize, (blockSize // 2) + boxTopLeftY + y * blockSize, blockSize, blockSize)
                        else:
                            rect = pygame.Rect(boxTopLeftX + x * blockSize, boxTopLeftY + y * blockSize, blockSize, blockSize)
                        pygame.draw.rect(screen, self.holdPiece.GetColor(), rect)
                        pygame.draw.rect(screen, (255,255,255), rect, 1)
    
    def DrawNextPieces(self):
        boxTopLeftX = windowWidth - 6 * blockSize
        boxTopLeftY = 3 * blockSize
        rect = pygame.Rect(boxTopLeftX, boxTopLeftY, 5 * blockSize, 4 * blockSize)
        pygame.draw.rect(screen, (255, 255, 255), rect, 1)

        # Draw "Next Piece" Above box
        text = font.render("Next Piece", True, (255, 255, 255))
        textRect = text.get_rect()
        textRect.x = boxTopLeftX
        textRect.y = boxTopLeftY - blockSize

        screen.blit(text, textRect)


        if self.nextPiece is not None:
            for x in range(len(self.nextPiece.currentShape[0])):
                for y in range(len(self.nextPiece.currentShape)):
                    if self.nextPiece.currentShape[y][x] == 'X':
                        # Center piece in box
                        if self.nextPiece.currentPieceType == 'Square':
                            rect = pygame.Rect((blockSize // 2) + boxTopLeftX + x * blockSize, boxTopLeftY + y * blockSize, blockSize, blockSize)
                        elif self.nextPiece.currentPieceType == 'I':
                            rect = pygame.Rect((blockSize // 2) + boxTopLeftX + x * blockSize, (blockSize // 2) + boxTopLeftY + y * blockSize, blockSize, blockSize)
                        else:
                            rect = pygame.Rect(boxTopLeftX + x * blockSize, boxTopLeftY + y * blockSize, blockSize, blockSize)

                        pygame.draw.rect(screen, self.nextPiece.GetColor(), rect)
                        pygame.draw.rect(screen, (255,255,255), rect, 1)
    
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

    def DrawGhost(self, ghostX, ghostY):
        for x in range(len(self.currentPiece.currentShape[0])):
            for y in range(len(self.currentPiece.currentShape)):
                if self.currentPiece.currentShape[y][x] == 'X':
                    s = pygame.Surface((blockSize, blockSize)) 
                    s.set_alpha(128) # Make ghost piece transparent
                    s.fill(self.currentPiece.GetColor()) 
                    screen.blit(s, (topLeftX + (x + ghostX) * blockSize, topLeftY + (y + ghostY) * blockSize))



    # Calculate where piece would be when dropped instantly
    def CalculatePieceGhostPostion(self):
        self.UnoccupyBoard()
        ghost = Piece(self.currentPiece.currentPieceType)
        ghost.MovePiece(self.currentPiece.x, self.currentPiece.y)
        ghost.RotateTo(self.currentPiece.currentRoationIndex)
        self.OccupyBoard(ghost)

        while not self.CheckBoundaries(ghost) and not self.CheckIntersections():
            self.UnoccupyBoard(ghost)
            ghost.MovePieceDown()
            self.OccupyBoard(ghost)

        self.UnoccupyBoard(ghost)
        self.OccupyBoard()
        ghost.MovePieceUp()

        return (ghost.x, ghost.y)

    def ClearRows(self):
        rowsComplete = []
        for y in range(rowHeight):
            numInRow = 0
            for x in range(rowWidth):
                if self.board[y][x].numOccupied == 1:
                    numInRow += 1
            if numInRow == rowWidth:
                rowsComplete.append(y)
        
        maxConsecutive = 0
        try:
            for i in range(1, len(rowsComplete)):
                if rowsComplete[i - 1] + 1 == rowsComplete[i]:
                    maxConsecutive += 1
                else:
                    maxConsecutive = 0
            if maxConsecutive == 4:
                # Apply tetris score modifer
                pass
            elif maxConsecutive == 3:
                # Apply 3 row modifier
                pass
            elif maxConsecutive == 2:
                # Apply 2 row modifer
                pass
        # expecting index out of bounds
        except:
            pass

        # Remove complete rows and shift board down
        for y in rowsComplete:
            self.board.pop(y)
            self.board.insert(0, [BoardSquare((0,0,0), 0) for x in range(rowWidth)])

    def MoveDown(self):
        self.UnoccupyBoard()
        self.currentPiece.MovePieceDown()
        self.OccupyBoard()
        if self.CheckBoundaries() or self.CheckIntersections():
            self.UnoccupyBoard()
            self.currentPiece.MovePieceUp()
            self.OccupyBoard()
            self.GenerateNewPiece()

    def MoveLeft(self):
        self.UnoccupyBoard()
        self.currentPiece.MovePieceLeft()
        self.OccupyBoard()
        if self.CheckBoundaries() or self.CheckIntersections():
            self.UnoccupyBoard()
            self.currentPiece.MovePieceRight()
            self.OccupyBoard()

    def MoveRight(self):
        self.UnoccupyBoard()
        self.currentPiece.MovePieceRight()
        self.OccupyBoard()
        if self.CheckBoundaries() or self.CheckIntersections():
            self.UnoccupyBoard()
            self.currentPiece.MovePieceLeft()
            self.OccupyBoard()

    def MovePiece(self, x, y):
        self.UnoccupyBoard()
        self.currentPiece.MovePiece(x, y)
        self.OccupyBoard()

        self.GenerateNewPiece()

    def RotateClockWise(self):
        self.UnoccupyBoard()
        self.currentPiece.RotateClockwise()
        self.OccupyBoard()
        if self.CheckBoundaries() or self.CheckIntersections():
            # TODO Kick piece away from boarder/piece
            self.UnoccupyBoard()
            self.currentPiece.RotateCouterClockwise()
            self.OccupyBoard()

    def RotateCounterClockWise(self):
        self.UnoccupyBoard()
        self.currentPiece.RotateCouterClockwise()
        self.OccupyBoard()
        if self.CheckBoundaries() or self.CheckIntersections():
            # TODO Kick piece away from boarder/piece
            self.UnoccupyBoard()
            self.currentPiece.RotateClockwise()
            self.OccupyBoard()

    def HoldPiece(self):
        board.GenerateNewPiece(True)

def EndGame():
    pygame.event.post(end_game_event) 

if __name__ == "__main__":
    # Initialize game window
    pygame.init()
    font = pygame.font.Font('freesansbold.ttf', 25)
    screen = pygame.display.set_mode((windowWidth,windowHeight))
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()
    # Initilize Board
    board = Board()
    ghostX, ghostY = board.CalculatePieceGhostPostion()
    running = True
    
    # Initialize block move timer
    moveDownTick = 1000
    pygame.time.set_timer(move_down_event, moveDownTick)
    
    while running:

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                running = False
            elif event.type == end_game_event:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # TODO Pause menu
                    running = False
                elif event.key == pygame.K_SPACE:
                    board.MovePiece(ghostX, ghostY)
                    # instant place
                    pass
                elif event.key == pygame.K_e:
                    # rotate clockwise
                    board.RotateClockWise()

                elif event.key == pygame.K_q:
                    # rotate couter clockwise
                    board.RotateCounterClockWise()
                elif event.key == pygame.K_UP:
                    # Hold current piece
                    board.HoldPiece()

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


        # Draws
        screen.fill((0,0,0))
        board.DrawBoard()
        ghostX, ghostY = board.CalculatePieceGhostPostion()
        board.DrawGhost(ghostX, ghostY)
        board.DrawGrid()
        board.DrawHoldBox()
        board.DrawNextPieces()
        board.DrawScoreBox()
        pygame.display.update()
        clock.tick(10)
