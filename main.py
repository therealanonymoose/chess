import pygame, sys, random, time

pygame.init()

#Screen Setup
screenDim = width, height = 1000, 1000
screen = pygame.display.set_mode(screenDim)
pygame.display.set_caption('Chess')
gridSize = min(width, height) // 8
clock = pygame.time.Clock()

#Piece classes
class Piece:
    def __init__(self, color, pos):
        self.color = color #True = white, False = black
        self.pos = pos
    def isValidMove(self, board, newPosition):
        return newPosition in self.getPossibleMoves(board)
    def getMoves(self, board):
        pass
    def getPossibleMoves(self, board):
        return [m for m in self.getMoves(board) if isLegalMove(board, self, m)]
    def getAttackSquares(self, board):
        return self.getMoves(board)
    def drawLegalMoves(self, board, screen, gridSize):
        moves = self.getPossibleMoves(board)
        overlay = pygame.Surface((gridSize, gridSize), pygame.SRCALPHA)
        for move in moves:
            x, y = move[1] * gridSize, move[0] * gridSize
            overlay.fill((0, 0, 0, 0))
            pygame.draw.circle(overlay, (0, 0, 0, 100), (gridSize // 2, gridSize // 2), 20)
            screen.blit(overlay, (x, y))
            
class Pawn(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
    def getMoves(self, board):
        moves = []
        row, col = self.pos
        dr = -1 if self.color else 1
        if board[row + dr][col] == ' ':
            moves.append((row + dr, col))
            if row == (6 if self.color else 1) and board[row + 2 * dr][col] == ' ':
                moves.append((row + 2 * dr, col))
        for move in self.getAttackSquares(board):
            if board[move[0]][move[1]] != ' ' and board[move[0]][move[1]].color != self.color:
                moves.append(move)
            elif (move[0], move[1]) == enPassantSquare:
                moves.append(move)
        return moves
    def getAttackSquares(self, board):
        moves = []
        row, col = self.pos
        dr = -1 if self.color else 1
        for dc in [-1, 1]:
            newRow = row + dr
            newCol = col + dc
            if 0 <= newRow < 8 and 0 <= newCol < 8:
                moves.append((newRow, newCol))
        return moves

class Knight(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
    def getMoves(self, board):
        moves = []
        directions = [(-2, -1), (-1, -2), (-2, 1), (-1, 2), (2, -1), (1, -2), (2, 1), (1, 2)]
        row, col = self.pos
        for dr, dc in directions:
            newRow, newCol = row + dr, col + dc
            if 0 <= newRow < 8 and 0 <= newCol < 8:
                if board[newRow][newCol] == ' ' or board[newRow][newCol].color != self.color:
                    moves.append((newRow, newCol))
        return moves

class Bishop(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
    def getMoves(self, board):
        moves = []
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        row, col = self.pos
        for dr, dc in directions:
            newRow, newCol = row + dr, col + dc
            while 0 <= newRow < 8 and 0 <= newCol < 8:
                if board[newRow][newCol] == ' ':
                    moves.append((newRow, newCol))
                else:
                    if board[newRow][newCol].color != self.color:
                        moves.append((newRow, newCol))
                    break
                newRow += dr
                newCol += dc
        return moves

class Rook(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
        self.hasMoved = False
    def getMoves(self, board):
        moves = []
        directions = [(-1, 0), (0, -1), (0, 1), (1, 0)]
        row, col = self.pos
        for dr, dc in directions:
            newRow, newCol = row + dr, col + dc
            while 0 <= newRow < 8 and 0 <= newCol < 8:
                if board[newRow][newCol] == ' ':
                    moves.append((newRow, newCol))
                else:
                    if board[newRow][newCol].color != self.color:
                        moves.append((newRow, newCol))
                    break
                newRow += dr
                newCol += dc
        return moves

class Queen(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
    def getMoves(self, board):
        moves = []
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        row, col = self.pos
        for dr, dc in directions:
            newRow, newCol = row + dr, col + dc
            while 0 <= newRow < 8 and 0 <= newCol < 8:
                if board[newRow][newCol] == ' ':
                    moves.append((newRow, newCol))
                else:
                    if board[newRow][newCol].color != self.color:
                        moves.append((newRow, newCol))
                    break
                newRow += dr
                newCol += dc
        return moves

class King(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
        self.hasMoved = False
    def getMoves(self, board):
        moves = []
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        row, col = self.pos
        for dr, dc in directions:
            newRow, newCol = row + dr, col + dc
            if 0 <= newRow < 8 and 0 <= newCol < 8 and not isSquareUnderAttack(board, newRow, newCol, not self.color):
                if board[newRow][newCol] == ' ' or board[newRow][newCol].color != self.color:
                    moves.append((newRow, newCol))
        if not self.hasMoved and not isSquareUnderAttack(board, row, col, not self.color):
            if all(board[row][c] == ' ' and not isSquareUnderAttack(board, row, c, not self.color) for c in range(col + 1, col + 3)):
                rook = board[row][7]
                if isinstance(rook, Rook) and not rook.hasMoved:
                    moves.append((row, col + 2))
            if all(board[row][c] == ' ' and not isSquareUnderAttack(board, row, c, not self.color) for c in range(col - 2, col)):
                rook = board[row][0]
                if isinstance(rook, Rook) and not rook.hasMoved:
                    moves.append((row, col - 2))
        return moves
    def getAttackSquares(self, board):
        row, col = self.pos
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        return [(row + dr, col + dc) for dr, dc in directions if 0 <= row + dr < 8 and 0 <= col + dc < 8]

#Assets
images = {
    "wp": pygame.image.load("Assets/wp.png"),
    "wn": pygame.image.load("Assets/wn.png"),
    "wb": pygame.image.load("Assets/wb.png"),
    "wr": pygame.image.load("Assets/wr.png"),
    "wq": pygame.image.load("Assets/wq.png"),
    "wk": pygame.image.load("Assets/wk.png"),
    "bp": pygame.image.load("Assets/bp.png"),
    "bn": pygame.image.load("Assets/bn.png"),
    "bb": pygame.image.load("Assets/bb.png"),
    "br": pygame.image.load("Assets/br.png"),
    "bq": pygame.image.load("Assets/bq.png"),
    "bk": pygame.image.load("Assets/bk.png"),
}

#Functions
def getImageName(piece):
    symbol = 'w' if piece.color else 'b'
    if isinstance(piece, Pawn): symbol += 'p'
    elif isinstance(piece, Knight): symbol += 'n'
    elif isinstance(piece, Bishop): symbol += 'b'
    elif isinstance(piece, Rook): symbol += 'r'
    elif isinstance(piece, Queen): symbol += 'q'
    elif isinstance(piece, King): symbol += 'k'
    return symbol

def move(piece, row, col):
    global board, turn, enPassantSquare, gameOver
    if isinstance(piece, King) and abs(col - piece.pos[1]) == 2:
        if col > piece.pos[1]:
            move(board[row][7], row, 5)
        else:
            move(board[row][0], row, 3)
    
    if isinstance(piece, Pawn) and (row, col) == enPassantSquare:
        board[enPassantSquare[0] + (1 if piece.color else -1)][enPassantSquare[1]] = ' '
    if isinstance(piece, Pawn) and abs(row - piece.pos[0]) == 2:
        enPassantSquare = (row + (1 if piece.color else -1), col)
    else:
        enPassantSquare = None

    board[piece.pos[0]][piece.pos[1]] = ' '
    board[row][col] = piece
    piece.pos = (row, col)

    if isinstance(piece, Pawn) and row == (0 if piece.color else 7):
        board[row][col] = Queen(piece.color, (row, col)) #autopromote, change later
    if isinstance(piece, Rook) or isinstance(piece, King):
        piece.hasMoved = True
    turn = not turn

    if not getAllLegalMoves(board, turn):
        kingPos = getKingPos(board, turn)
        if isSquareUnderAttack(board, kingPos[0], kingPos[1], not turn):
            print("Checkmate!")
        else:
            print("Stalemate!")
        gameOver = True

def isSquareUnderAttack(board, row, col, attackingColor):
    for r in board:
        for piece in r:
            if isinstance(piece, Piece) and piece.color == attackingColor:
                if (row, col) in piece.getAttackSquares(board):
                    return True
    return False

def copyPiece(piece):
    new = type(piece)(piece.color, piece.pos)
    if isinstance(piece, Rook) or isinstance(piece, King): new.hasMoved = piece.hasMoved
    return new

def isLegalMove(board, piece, move):
    boardCopy = [[p if p == ' ' else copyPiece(p) for p in row] for row in board]
    oldRow, oldCol = piece.pos
    newRow, newCol = move
    moving = boardCopy[oldRow][oldCol]

    boardCopy[oldRow][oldCol] = ' '
    moving.pos = move
    boardCopy[newRow][newCol] = moving
    
    kingPos = getKingPos(boardCopy, piece.color)
    return not isSquareUnderAttack(boardCopy, kingPos[0], kingPos[1], not piece.color)

def getAllLegalMoves(board, color):
    moves = []
    for row in board:
        for piece in row:
            if isinstance(piece, Piece) and piece.color == color:
                moves += piece.getPossibleMoves(board)
    return moves

def getKingPos(board, color):
    for row in board:
        for p in row:
            if isinstance(p, King) and p.color == color:
                return p.pos

#board
board = [[' ' for i in range(8)] for j in range(8)]
board[0] = [
    Rook(False, (0, 0)), Knight(False, (0, 1)), Bishop(False, (0, 2)), Queen(False, (0, 3)),
    King(False, (0, 4)), Bishop(False, (0, 5)), Knight(False, (0, 6)), Rook(False, (0, 7))
]
board[1] = [Pawn(False, (1, i)) for i in range(8)]
board[6] = [Pawn(True, (6, i)) for i in range(8)]
board[7] = [
    Rook(True, (7, 0)), Knight(True, (7, 1)), Bishop(True, (7, 2)), Queen(True, (7, 3)),
    King(True, (7, 4)), Bishop(True, (7, 5)), Knight(True, (7, 6)), Rook(True, (7, 7))
]

#notation: board = [[f"{chr(i+65)}{8-j}" for i in range(8)] for j in range(8)]
turn = True
selected = None
dragged = None
dragOffset = (0, 0)
enPassantSquare = None
gameOver = False

while not gameOver:
    clock.tick(60)

    #Board Setup
    screen.fill((255, 255, 255))
    for x in range(0, 8 * gridSize, gridSize):
        for y in range(0, 8 * gridSize, gridSize):
            tile = pygame.Rect(x, y, gridSize, gridSize)
            pygame.draw.rect(screen, [(246, 225, 198), (202, 159, 133)][(x + y) // gridSize % 2], tile)
    
    #Draw pieces
    for row in board:
        for piece in row:
            if piece != ' ' and piece != dragged:
                img = images[getImageName(piece)]
                img = pygame.transform.scale(img, (gridSize, gridSize))
                screen.blit(img, (piece.pos[1] * gridSize, piece.pos[0] * gridSize))
    
    if dragged:
        x, y = pygame.mouse.get_pos()
        img = images[getImageName(dragged)]
        img = pygame.transform.scale(img, (gridSize, gridSize))
        screen.blit(img, (x - dragOffset[0], y - dragOffset[1]))

    if selected:
        selected.drawLegalMoves(board, screen, gridSize)

    #Inputs
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            x, y = event.pos
            row, col = y // gridSize, x // gridSize
            clicked = board[row][col]
            if selected:
                if (row, col) in selected.getPossibleMoves(board):
                    move(selected, row, col)
                    selected = None
                elif isinstance(clicked, Piece) and clicked.color == selected.color == turn:
                    selected = clicked
                else:
                    selected = None
            else:
                selected = clicked if isinstance(clicked, Piece) and clicked.color == turn else None
            if isinstance(clicked, Piece) and clicked.color == turn:
                dragged = clicked
                dragOffset = (x - col * gridSize, y - row * gridSize)

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if dragged and dragged.color == turn:
                x, y = event.pos
                row, col = y // gridSize, x // gridSize
                if (row, col) in dragged.getPossibleMoves(board):
                    move(dragged, row, col)
                    selected = None
            dragged = None

    pygame.display.flip()

pygame.quit()
sys.exit()
