import pygame
import random
 
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
second_elapsed_event = pygame.USEREVENT + 2
 
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
    board = None
    
    currentPiece = None
    holdPiece = None
    nextPiece = None
    score = 0
    linesComplete = 0
    level = 0
    moveDownTick = 0
    secondsElapsed = 0

    def __init__(self):
        self.board = [[BoardSquare((0,0,0), 0) for x in range(rowWidth)] for y in range(rowHeight)] 
        self.currentPiece = Piece()
        self.nextPiece = Piece()
        self.holdPiece = None
        self.linesComplete = 0
        self.level = 0
        self.ClearRows()

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
        
        self.ClearRows()
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
        
        # Draw hold box
        rect = pygame.Rect(boxTopLeftX, boxTopLeftY, 5 * blockSize, 4 * blockSize)
        pygame.draw.rect(screen, (255, 255, 255), rect, 1)

        # Draw "Hold Piece" above box
        DrawText("Hold Piece", boxTopLeftX, boxTopLeftY - blockSize)

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

        # Draw next piece box
        rect = pygame.Rect(boxTopLeftX, boxTopLeftY, 5 * blockSize, 4 * blockSize)
        pygame.draw.rect(screen, (255, 255, 255), rect, 1)

        # Draw "Next Piece" Above box
        DrawText("Next Piece", boxTopLeftX, boxTopLeftY - blockSize)

        # Draw next piece in box
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
    
    def DrawTime(self):
        boxTopLeftX = windowWidth // 2 - 5 * blockSize
        boxTopLeftY =  1.5 * blockSize

        # Draw Time box
        rect = pygame.Rect(boxTopLeftX, boxTopLeftY, 4 * blockSize, 1.5 * blockSize)
        pygame.draw.rect(screen, (255, 255, 255), rect, 1)
        
        # Draw "Time" above box
        DrawText("Time", boxTopLeftX + blockSize, boxTopLeftY - blockSize)

        # Draw Time elapsed
        DrawText(f"{self.secondsElapsed // 60:02}:{self.secondsElapsed % 60:02}", boxTopLeftX + blockSize, boxTopLeftY + 0.5 * blockSize)

    def DrawScore(self):
        boxTopLeftX = windowWidth // 2 + 1* blockSize
        boxTopLeftY =  1.5 * blockSize

        # Draw Score box
        rect = pygame.Rect(boxTopLeftX, boxTopLeftY, 4 * blockSize, 1.5 * blockSize)
        pygame.draw.rect(screen, (255, 255, 255), rect, 1)
        
        # Draw "Score" above box
        DrawText("Score", boxTopLeftX + blockSize, boxTopLeftY - blockSize)

        # Draw score
        DrawText(self.score,boxTopLeftX + 0.25 * blockSize, boxTopLeftY + 0.5 * blockSize)
    

    # Draw color of each square of board
    def DrawBoard(self):
        for x in range(rowWidth):
            for y in range(rowHeight):
                if self.board[y][x].PieceColor != (0,0,0):
                    rect = pygame.Rect(topLeftX + x * blockSize, topLeftY + y * blockSize, blockSize, blockSize)
                    pygame.draw.rect(screen, self.board[y][x].PieceColor, rect)

    # Draw where current piece would be if placed instantly
    def DrawGhost(self, ghostX, ghostY):
        for x in range(len(self.currentPiece.currentShape[0])):
            for y in range(len(self.currentPiece.currentShape)):
                if self.currentPiece.currentShape[y][x] == 'X':
                    s = pygame.Surface((blockSize, blockSize)) 
                    s.set_alpha(64) # Make ghost piece transparent
                    s.fill(self.currentPiece.GetColor()) 
                    screen.blit(s, (topLeftX + (x + ghostX) * blockSize, topLeftY + (y + ghostY) * blockSize))



    # Calculate where piece would be when dropped instantly
    def CalculatePieceGhostPostion(self):
        # Remove current piece from board to remove potential conflicts
        self.UnoccupyBoard()
        # Create copy of current piece
        ghost = Piece(self.currentPiece.currentPieceType)
        ghost.MovePiece(self.currentPiece.x, self.currentPiece.y)
        ghost.RotateTo(self.currentPiece.currentRoationIndex)
        self.OccupyBoard(ghost)

        # While piece is not intersecting our out of bounds, move down
        while not self.CheckBoundaries(ghost) and not self.CheckIntersections():
            self.UnoccupyBoard(ghost)
            ghost.MovePieceDown()
            self.OccupyBoard(ghost)

        # Remove copy and add original piece
        self.UnoccupyBoard(ghost)
        self.OccupyBoard()
        ghost.MovePieceUp()

        return (ghost.x, ghost.y)

    def ClearRows(self):
        # Check which rows are complete, append to list
        rowsComplete = []
        for y in range(rowHeight):
            numInRow = 0
            for x in range(rowWidth):
                if self.board[y][x].numOccupied == 1:
                    numInRow += 1
            if numInRow == rowWidth:
                rowsComplete.append(y)
        
        # Count number of consecutive rows
        maxConsecutive = 0
        temp = 1
        if len(rowsComplete) > 1:
            for i in range(1, len(rowsComplete)):
                if rowsComplete[i - 1] + 1 == rowsComplete[i]:
                    temp += 1
                else:
                    temp = 1
                maxConsecutive = temp if temp > maxConsecutive else maxConsecutive
        elif len(rowsComplete) == 1:
            maxConsecutive = 1

        modifier = 0
        # Update lines complete and set score modifer
        if maxConsecutive == 4:
            self.linesComplete += 8
            modifier = 1200
        elif maxConsecutive == 3:
            self.linesComplete += 5
            modifier = 300
        elif maxConsecutive == 2:
            self.linesComplete += 3
            modifier = 100
        elif maxConsecutive == 1:
            self.linesComplete += 1
            modifier = 40
        else:
            modifier = 0
        
        # Update score
        self.score += (self.level + 1) * modifier #+ (40 * (maxConsecutive - len(rowsComplete))) 
        
        # Update current level
        if self.level >= 9 and self.linesComplete >= 100:
            self.level += 1
            self.linesComplete = 0
        elif self.linesComplete >= (self.level + 1) * 10:
            self.level += 1
            self.linesComplete = 0

        # Remove complete rows and shift board down
        for y in rowsComplete:
            self.board.pop(y)
            self.board.insert(0, [BoardSquare((0,0,0), 0) for x in range(rowWidth)])

        # Update drop rate
        moveDownTick = int(((10 - self.level) * .05) * 1000)
        pygame.time.set_timer(move_down_event, 0)
        pygame.time.set_timer(move_down_event, moveDownTick)

    def MoveDown(self):
        # Remove piece from board, move it down, add piece to board
        self.UnoccupyBoard()
        self.currentPiece.MovePieceDown()
        self.OccupyBoard()
        # if piece is out of bounds or intersecting, move piece up
        if self.CheckBoundaries() or self.CheckIntersections():
            self.UnoccupyBoard()
            self.currentPiece.MovePieceUp()
            self.OccupyBoard()
            self.GenerateNewPiece()

    def MoveLeft(self):
        # Remove piece from board, move it left, add piece to board
        self.UnoccupyBoard()
        self.currentPiece.MovePieceLeft()
        self.OccupyBoard()
        # if piece is out of bounds or intersecting, move piece right
        if self.CheckBoundaries() or self.CheckIntersections():
            self.UnoccupyBoard()
            self.currentPiece.MovePieceRight()
            self.OccupyBoard()

    def MoveRight(self):
        # Remove piece from board, move it right, add piece to board
        self.UnoccupyBoard()
        self.currentPiece.MovePieceRight()
        self.OccupyBoard()
        # if piece is out of bounds or intersecting, move piece left
        if self.CheckBoundaries() or self.CheckIntersections():
            self.UnoccupyBoard()
            self.currentPiece.MovePieceLeft()
            self.OccupyBoard()

    # Move piece to set location
    # Used for instant place
    def MovePiece(self, x, y):
        self.UnoccupyBoard()
        self.currentPiece.MovePiece(x, y)
        self.OccupyBoard()

        self.GenerateNewPiece()

    # Remove piece from board, rotate clockwise, add piece to board
    def RotateClockWise(self):
        self.UnoccupyBoard()
        self.currentPiece.RotateClockwise()
        self.OccupyBoard()
        if self.CheckBoundaries() or self.CheckIntersections():
            # TODO Kick piece away from boarder/piece
            self.UnoccupyBoard()
            self.currentPiece.RotateCouterClockwise()
            self.OccupyBoard()

    # Remove piece from board, rotate counter-clockwise, add piece to board
    def RotateCounterClockWise(self):
        self.UnoccupyBoard()
        self.currentPiece.RotateCouterClockwise()
        self.OccupyBoard()
        if self.CheckBoundaries() or self.CheckIntersections():
            # TODO Kick piece away from boarder/piece
            self.UnoccupyBoard()
            self.currentPiece.RotateClockwise()
            self.OccupyBoard()

    # Make current piece the held piece, and generate a new piece
    def HoldPiece(self):
        self.GenerateNewPiece(True)

# Draw Text on screen at x, y using optional color and x/y is center of text
def DrawText(text, x, y, color= (255, 255, 255), center = False):
    text = font.render(f"{text}", True, color)
    textRect = text.get_rect()
    if center:
        textRect.centerx = x
        textRect.centery = y
    else:
        textRect.x = x 
        textRect.y = y 
    screen.blit(text, textRect)

def EndGame():
    pygame.event.post(pygame.event.Event(end_game_event)) 

# Display Default Controls
def Welcome():
    while True:
        screen.fill((0,0,0))
        DrawText("Tetris", windowWidth // 2, windowHeight * 0.15, (255, 0, 0), True)
        DrawText("Default Controls:", windowWidth // 2, windowHeight * 0.25, (255, 0, 0), True)

        DrawText("Move Left: A or Left Arrow  Move Right: D or Right Arrow", windowWidth// 2, windowHeight * 0.35, (255, 255, 255), True)
        DrawText("Move Down: S or Down Arrow  Instant Place: Space Bar", windowWidth // 2, windowHeight * 0.45, (255, 255, 255), True)
        DrawText("Rotate Clockwise: E  Rotate Counter-Clockwise: Q", windowWidth // 2, windowHeight * 0.55, (255, 255, 255), True)
        DrawText("Store Current Piece: W or Up Arrow", windowWidth // 2, windowHeight * 0.65, (255, 255, 255), True)
        DrawText("Pause: Escape", windowWidth // 2, windowHeight * 0.75, (255, 255, 255), True)
        DrawText("Press any key to continue...", windowWidth // 2, windowHeight * 0.85, (255, 255, 255), True)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN:
                return
                
        pygame.display.update()
def GameOver(score):
    newGame = False
    running = True
    while running:
        screen.fill((0,0,0))
        DrawText("Game Over", windowWidth // 2, windowHeight * 0.25, (255, 0, 0), True)
        DrawText(f"Final Score: {score}", windowWidth // 2, windowHeight * 0.50, (255, 255, 255), True)
        DrawText("New Game?", windowWidth // 2, windowHeight * 0.75, (255, 255, 255), True)

        if newGame:
            DrawText("Yes", windowWidth * 0.33, windowHeight * 0.75, (255, 255, 0), True)
            DrawText("No", windowWidth * 0.66, windowHeight * 0.75, (255, 255, 255), True)
        else:
            DrawText("Yes", windowWidth * 0.33, windowHeight * 0.75, (255, 255, 255), True)
            DrawText("No", windowWidth * 0.66, windowHeight * 0.75, (255, 255, 0), True)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE or event.key == pygame.K_KP_ENTER:
                    running = False
                    return newGame
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    newGame = True
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    newGame = False
                
        pygame.display.update()

def PauseMenu():
    curPos = 0

    while True:
        screen.fill((0,0,0))
        DrawText("Game Paused", windowWidth // 2, windowHeight * 0.25, (255, 0, 0), True)

        if curPos == 0:
            DrawText("Resume", windowWidth // 2, windowHeight * 0.35, (255, 255, 0), True)
            DrawText("Controls", windowWidth // 2, windowHeight * 0.45, (255, 255, 255), True)
            DrawText("Quit", windowWidth // 2, windowHeight * 0.55, (255, 255, 255), True)
        elif curPos == 1:
            DrawText("Resume", windowWidth // 2, windowHeight * 0.35, (255, 255, 255), True)
            DrawText("Controls", windowWidth // 2, windowHeight * 0.45, (255, 255, 0), True)
            DrawText("Quit", windowWidth // 2, windowHeight * 0.55, (255, 255, 255), True)
        else:
            DrawText("Resume", windowWidth // 2, windowHeight * 0.35, (255, 255, 255), True)
            DrawText("Controls", windowWidth // 2, windowHeight * 0.45, (255, 255, 255), True)
            DrawText("Quit", windowWidth // 2, windowHeight * 0.55, (255, 255, 0), True)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE or event.key == pygame.K_KP_ENTER:
                    if curPos == 0:
                        return 
                    elif curPos == 1:
                        Welcome()
                    else:
                        EndGame()
                        return

                elif curPos != 3 and (event.key == pygame.K_s or event.key == pygame.K_DOWN):
                    curPos += 1
                elif curPos != 0 and (event.key == pygame.K_w or event.key == pygame.K_UP):
                    curPos -= 1

        pygame.display.update()

def NewGame():
    # Initilize Board
    board = Board()
    ghostX, ghostY = board.CalculatePieceGhostPostion()
    running = True
    
    # Initialize block move timer
    pygame.time.set_timer(second_elapsed_event, 1000)
    
    while running:

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                running = False
            if event.type == end_game_event:
                running = False
                return GameOver(board.score) 
            elif event.type == second_elapsed_event:
                board.secondsElapsed += 1

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    PauseMenu()
                elif event.key == pygame.K_SPACE:
                    # instant place
                    board.MovePiece(ghostX, ghostY)
                elif event.key == pygame.K_e:
                    # rotate clockwise
                    board.RotateClockWise()

                elif event.key == pygame.K_q:
                    # rotate couter clockwise
                    board.RotateCounterClockWise()
                elif event.key == pygame.K_UP or event.key == pygame.K_w:
                    # Hold current piece
                    board.HoldPiece()

            # Block move timed event
            elif event.type == move_down_event:
               board.MoveDown()

        # Check if key is held down for movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_DOWN] or keys[pygame.K_w]:
            # move piece downward faster
            board.MoveDown()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            # move piece left while held
            board.MoveLeft()

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
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
        board.DrawScore()
        board.DrawTime()
        pygame.display.update()
        clock.tick(10)
    return False

if __name__ == "__main__":
    # Initialize game window
    pygame.init()
    font = pygame.font.SysFont('consolas', 25)
    screen = pygame.display.set_mode((windowWidth,windowHeight))
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()
    
    Welcome()
    while NewGame():
        pass
