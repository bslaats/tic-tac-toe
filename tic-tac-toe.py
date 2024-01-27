import pygame
import sys

# Initialize pygame 
pygame.init()

# Constants
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600 
LINE_WIDTH = 15
BOARD_ROWS = 3
BOARD_COLS = 3
SQUARE_SIZE = 200
CIRCLE_RADIUS = 60
CROSS_WIDTH = 25
SPACE = 55
WIN_LINE_WIDTH = 15

# RGB Colors
RED = (255, 0, 0)
BG_COLOR = (28, 170, 156)
LINE_COLOR = (23, 145, 135)
CIRCLE_COLOR = (255, 0, 0) 
CROSS_COLOR = (66, 66, 66)

# Set up the screen
screen = pygame.display.set_mode( (SCREEN_WIDTH, SCREEN_HEIGHT) )
pygame.display.set_caption( 'TIC TAC TOE' )
screen.fill( BG_COLOR )

# Board 
board = [[None]*BOARD_COLS for i in range(BOARD_ROWS)]

# Function to draw lines
def draw_lines():
    
    # Horizontal lines
    pygame.draw.line( screen, LINE_COLOR, (0, SQUARE_SIZE), (SCREEN_WIDTH, SQUARE_SIZE), LINE_WIDTH )
    pygame.draw.line( screen, LINE_COLOR, (0, 2 * SQUARE_SIZE), (SCREEN_WIDTH, 2 * SQUARE_SIZE), LINE_WIDTH )

    # Vertical lines 
    pygame.draw.line( screen, LINE_COLOR, (SQUARE_SIZE, 0), (SQUARE_SIZE, SCREEN_HEIGHT), LINE_WIDTH )
    pygame.draw.line( screen, LINE_COLOR, (2 * SQUARE_SIZE, 0), (2 * SQUARE_SIZE, SCREEN_HEIGHT), LINE_WIDTH)
    
# Draw the lines on the screen	
draw_lines()

# Function to draw shapes		
def draw_shapes():
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if board[row][col] == 1:
                pygame.draw.circle( screen, CIRCLE_COLOR, (int( col * SQUARE_SIZE + SQUARE_SIZE//2 ), int( row * SQUARE_SIZE + SQUARE_SIZE//2 )), CIRCLE_RADIUS, LINE_WIDTH )
            elif board[row][col] == 2: 
                pygame.draw.line( screen, CROSS_COLOR, (col * SQUARE_SIZE + SPACE, row * SQUARE_SIZE + SQUARE_SIZE - SPACE), (col * SQUARE_SIZE + SQUARE_SIZE - SPACE, row * SQUARE_SIZE + SPACE), CROSS_WIDTH )	
                pygame.draw.line( screen, CROSS_COLOR, (col * SQUARE_SIZE + SPACE, row * SQUARE_SIZE + SPACE), (col * SQUARE_SIZE + SQUARE_SIZE - SPACE, row * SQUARE_SIZE + SQUARE_SIZE - SPACE), CROSS_WIDTH )

# Function to mark square			
def mark_square(row, col, player):
    board[row][col] = player

# Function to check for win
def check_win(player):
    
    # Vertical win check
    for col in range(BOARD_COLS):
        if board[0][col] == player and board[1][col] == player and board[2][col] == player:
            draw_vertical_winning_line(col, player)
            return True
            
    # Horizontal win check		
    for row in range(BOARD_ROWS):
        if board[row][0] == player and board[row][1] == player and board[row][2] == player:
            draw_horizontal_winning_line(row, player)
            return True
    
    # Ascending diagonal win check
    if board[2][0] == player and board[1][1] == player and board[0][2] == player:
        draw_asc_diagonal(player)
        return True

    # Descending diagonal win check
    if board[0][0] == player and board[1][1] == player and board[2][2] == player:
        draw_desc_diagonal(player)
        return True
    
    return False
    
# Function for vertical win line    
def draw_vertical_winning_line(col, player):
    posX = col * SQUARE_SIZE + SQUARE_SIZE//2

    if player == 1:
        color = CIRCLE_COLOR
    elif player == 2:
        color = CROSS_COLOR

    pygame.draw.line( screen, color, (posX, 15), (posX, SCREEN_HEIGHT - 15), LINE_WIDTH )

# Function for horizontal win line
def draw_horizontal_winning_line(row, player):
    posY = row * SQUARE_SIZE + SQUARE_SIZE//2

    if player == 1:
        color = CIRCLE_COLOR
    elif player == 2:
        color = CROSS_COLOR

    pygame.draw.line( screen, color, (15, posY), (SCREEN_WIDTH - 15, posY), WIN_LINE_WIDTH )  
    
# Function for ascending diagonal win line
def draw_asc_diagonal(player):
    if player == 1:
        color = CIRCLE_COLOR
    elif player == 2:
        color = CROSS_COLOR

    pygame.draw.line( screen, color, (15, SCREEN_HEIGHT - 15), (SCREEN_WIDTH - 15, 15), WIN_LINE_WIDTH )

# Function for descending diagonal win line
def draw_desc_diagonal(player):
    if player == 1:
        color = CIRCLE_COLOR
    elif player == 2:
        color = CROSS_COLOR

    pygame.draw.line( screen, color, (15, 15), (SCREEN_WIDTH - 15, SCREEN_HEIGHT - 15), WIN_LINE_WIDTH )

# Function for tie  
def check_tie():
    if all([all(row) for row in board]): 
        game_over_text = "Match Tie!"
        return True
    return False

# Function to check if square is available 
def available_square(row, col):
    return board[row][col] == None


# Main loop
game_over = False 

# Player 1 - Circle
player = 1				
game_runnigng = True
while game_runnigng:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_runnigng = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                game_runnigng = False

        if event.type == pygame.MOUSEBUTTONDOWN and not game_over:

            mouseX = event.pos[0] 
            mouseY = event.pos[1] 

            clicked_row = int(mouseY // SQUARE_SIZE)
            clicked_col = int(mouseX // SQUARE_SIZE)

            if available_square(clicked_row, clicked_col):
                mark_square(clicked_row, clicked_col, player)
                if check_win(player):
                    game_over = True
                player = player % 2 + 1

                draw_shapes()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                board = [[None]*BOARD_COLS for i in range(BOARD_ROWS)]
                print(board)
                game_over = False
                player = 1

                screen.fill(BG_COLOR)
                draw_lines()

    pygame.display.update() 

# Close game window
pygame.quit()