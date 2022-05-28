import copy
from tkinter import Tk, Canvas, Frame, Button, BOTH, TOP, LEFT

MARGIN = 20  # Pixels around the board
SIDE = 50  # Width of every board cell.
WIDTH = HEIGHT = MARGIN * 2 + SIDE * 9  # Width and height of the whole board
VALID_SET = set(range(1, 10))


class Game:
    """
    Game class represents a Sudoku game, it includes logic
    to set up the board, check for game status
    """

    # initializes the original board
    def __init__(self, input_file):
        self.orig_board = self.setup_board(input_file)
        self.curr_board = []
        self.game_over = False

    # set up board by reading from input file
    def setup_board(self, input_file):
        board = []
        for line in input_file:
            line = line.strip()
            # each row needs to have exactly 9 numbers
            if len(line) != 9:
                raise Exception("invalid input, line:", line)
            board.append([])

            for ch in line:
                # each character needs to be number
                if not ch.isdigit():
                    raise Exception("invalid character:", ch)
                board[-1].append(int(ch))

        # need exactly 9 rows
        if len(board) != 9:
            raise Exception("invalid number of lines, got: ", len(board))
        return board

    # play start a new round of game be resetting the status
    # and set up current board by copying from original board
    def play(self):
        self.game_over = False
        self.curr_board = []
        for i in range(9):
            self.curr_board.append([])
            for j in range(9):
                self.curr_board[i].append(self.orig_board[i][j])

    # check if the current board is solved
    def is_solved(self):
        # if all rows are solved
        for row_idx in range(9):
            if not self.is_row_solved(row_idx):
                return False

        # if all cols are solved
        for col_idx in range(9):
            if not self.is_col_solved(col_idx):
                return False

        # if all the 3*3 square block is solved, total of 9
        for row_idx in range(3):
            for col_idx in range(3):
                if not self.is_square_solved(row_idx, col_idx):
                    return False

        # if all solved, set game status
        self.game_over = True
        return True

    # check if the certain row satisfies the rule
    # since only 1-9 is allowed, check if by putting all numbers into a set
    # and get exactly 9 numbers
    def is_row_solved(self, row_idx):
        return set(self.curr_board[row_idx]) == VALID_SET

    # check if the certain column satisfies the rule
    def is_col_solved(self, col_idx):
        col = []
        for i in range(9):
            col.append(self.curr_board[i][col_idx])

        return set(col) == VALID_SET

    # checks if the specified 3*3 square satisfied the rule
    # there're total of 9 such 3*3 squares
    def is_square_solved(self, sq_row_idx, sq_col_idx):
        sqr = []
        for i in range(sq_row_idx*3, (sq_row_idx+1)*3):
            for j in range(sq_col_idx*3, (sq_col_idx+1)*3):
                sqr.append(self.curr_board[i][j])
        return set(sqr) == VALID_SET


class Sudoku(Frame):
    """
    This class represents the Sudoku game UI, including methods to
    draw the boards, take input, set individual boxes and check if
    game is solved.
    """

    def __init__(self, parent, new_game):
        self.new_game = new_game
        Frame.__init__(self, parent)
        self.parent = parent
        self.row, self.col = -1, -1
        self.draw_board()

    # draws the initial board without placing any numbers yet
    def draw_board(self):
        self.parent.title("Sudoku")
        self.pack(fill=BOTH)
        self.canvas = Canvas(self, width=WIDTH, height=HEIGHT)
        self.canvas.pack(fill=BOTH, side=TOP)
        check_button = Button(self,
                              text="Check answers!",
                              command=self.check_answers)
        check_button.pack(fill=BOTH, side=LEFT, expand=True)
        reset_button = Button(self,
                              text="Reset",
                              command=self.reset)
        reset_button.pack(fill=BOTH, side=LEFT, expand=True)
        find_button = Button(self,
                              text="Solve for me!",
                              command=self.solve)
        find_button.pack(fill=BOTH, side=LEFT, expand=True)

        self.draw_grid()
        self.draw_game()

        self.canvas.bind("<Button-1>", self.box_clicked)
        self.canvas.bind("<Key>", self.key_pressed)

    # draws the grids into 3*3 squares
    def draw_grid(self):
        for i in range(10):
            color = "blue" if i % 3 == 0 else "gray"

            x0 = MARGIN + i * SIDE
            y0 = MARGIN
            x1 = MARGIN + i * SIDE
            y1 = HEIGHT - MARGIN
            self.canvas.create_line(x0, y0, x1, y1, fill=color)

            x0 = MARGIN
            y0 = MARGIN + i * SIDE
            x1 = WIDTH - MARGIN
            y1 = MARGIN + i * SIDE
            self.canvas.create_line(x0, y0, x1, y1, fill=color)

    # draws the individual numbers in the boxes
    def draw_game(self):
        self.canvas.delete("numbers")
        for i in range(9):
            for j in range(9):
                answer = self.new_game.curr_board[i][j]
                if answer != 0:
                    x = MARGIN + j * SIDE + SIDE / 2
                    y = MARGIN + i * SIDE + SIDE / 2
                    original = self.new_game.orig_board[i][j]
                    color = "black" if answer == original else "sea green"
                    self.canvas.create_text(
                        x, y, text=answer, tags="numbers", fill=color
                    )

    # highlights the current selected box element
    def draw_cursor(self):
        self.canvas.delete("cursor")
        if self.row >= 0 and self.col >= 0:
            x0 = MARGIN + self.col * SIDE + 1
            y0 = MARGIN + self.row * SIDE + 1
            x1 = MARGIN + (self.col + 1) * SIDE - 1
            y1 = MARGIN + (self.row + 1) * SIDE - 1
            self.canvas.create_rectangle(
                x0, y0, x1, y1,
                outline="red", tags="cursor"
            )

    # print msg when game solved
    def print_win_msg(self):
        x0 = MARGIN + SIDE * 2
        y0 = MARGIN + SIDE * 3

        x1 = MARGIN + SIDE * 7
        y1 = MARGIN + SIDE * 6

        self.canvas.create_rectangle(
            x0, y0, x1, y1,
            tags="victory", fill="dark orange", outline="orange"
        )
        # create text
        x = y = MARGIN + 4 * SIDE + SIDE / 2
        self.canvas.create_text(
            x, y,
            text="Solved!", tags="victory",
            fill="white", font=("Arial", 20)
        )

    # print msg when game not solved
    def print_lose_msg(self):
        x0 = MARGIN + SIDE * 2
        y0 = MARGIN + SIDE * 3
        x1 = MARGIN + SIDE * 7
        y1 = MARGIN + SIDE * 6
        self.canvas.create_rectangle(
            x0, y0, x1, y1,
            tags="failure", fill="dark orange", outline="orange"
        )
        # create text
        x = y = MARGIN + 4 * SIDE + SIDE / 2
        self.canvas.create_text(
            x, y,
            text="Not solved! \nReset and Try Again!", tags="failure",
            fill="white", font=("Arial", 20)
        )

    # responds to a box clicked event by setting the current row & col
    # and highlighted the box
    def box_clicked(self, event):
        if self.new_game.game_over:
            return
        x, y = event.x, event.y
        if MARGIN < x < WIDTH - MARGIN and MARGIN < y < HEIGHT - MARGIN:
            self.canvas.focus_set()

            # get row and col numbers from x,y coordinates
            row, col = (y - MARGIN) // SIDE, (x - MARGIN) // SIDE

            # do no modify is the box comes from original board
            if self.new_game.orig_board[row][col] != 0:
                self.row, self.col = -1, -1
            else:
                self.row, self.col = row, col
        else:
            self.row, self.col = -1, -1

        self.draw_cursor()

    # takes keyboard input and place it into the selected box
    def key_pressed(self, event):
        if self.new_game.game_over:
            return
        if self.row >= 0 and self.col >= 0 and event.char in "1234567890":
            self.new_game.curr_board[self.row][self.col] = int(event.char)
            self.col, self.row = -1, -1
            self.draw_game()
            self.draw_cursor()

    # check if current game is solved and prints messages accordingly
    def check_answers(self):
        if self.new_game.is_solved():
            self.print_win_msg()
        else:
            self.print_lose_msg()

    # reset the game by clearing all inputs
    def reset(self):
        self.new_game.play()
        self.canvas.delete("victory")
        self.canvas.delete("failure")
        self.draw_game()

    # solve the game by running a recursive algorithm
    def solve(self):
        # make a copy of original board
        board = copy.deepcopy(self.new_game.orig_board)

        # check if current move is valid
        def _is_valid(i, j, num):
            for k in range(9):
                # row i
                if k != j and board[i][k] == num:
                    return False
                # column j
                if k != i and board[k][j] == num:
                    return False

            bi, bj = i // 3, j // 3
            for r in range(bi * 3, (bi + 1) * 3):
                for c in range(bj * 3, (bj + 1) * 3):
                    if r != i and c != j and board[r][c] == num:
                        return False
            return True

        # explore the board by tentative putting numbers and
        # checking for validity
        def _dfs(idx):
            if idx == 9 * 9:
                self.new_game.curr_board = copy.deepcopy(board)
                return
            i, j = idx // 9, idx % 9

            if board[i][j] == 0:
                # candidate
                for num in range(1, 10):
                    board[i][j] = num
                    if _is_valid(i, j, num):
                        _dfs(idx + 1)
                    board[i][j] = 0
            else:
                _dfs(idx + 1)

        _dfs(0)
        # print(self.new_game.curr_board)
        self.draw_game()


# entry point to the game
if __name__ == '__main__':
    with open('resources/regular.txt', 'r') as infile:
        sudoku_game = Game(infile)
        sudoku_game.play()

        root = Tk()
        Sudoku(root, sudoku_game)
        root.geometry("%dx%d" % (WIDTH, HEIGHT + 40))
        root.mainloop()
