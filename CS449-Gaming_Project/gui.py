
import tkinter as tk
from tkinter import ttk, messagebox

from game import Game
from graphics import BoardGraphics


class SolitaireGUI:

    def __init__(self, root):
        self.root = root
        self.root.title("Peg Solitaire")
        self.root.geometry("950x850")
        self.root.configure(bg="#171B22")

        # Create the game
        self.game = Game(7, "English")

        # Track the currently selected peg
        self.selected_peg = None

        # Prevent repeated game-over messages
        self.game_finished = False

        # Board settings
        self.board_type = tk.StringVar(value="English")
        self.board_size = tk.StringVar(value="7")

        # Build the interface
        self.create_widgets()

        # Connect our graphics class
        self.graphics = BoardGraphics(self.canvas)

        # Display the starting board
        self.draw_board()

    def create_widgets(self):

        # Title
        title = tk.Label(
            self.root,
            text="PEG SOLITAIRE",
            font=("Arial", 26, "bold"),
            bg="#171B22",
            fg="#E6E6E6"
        )
        title.pack(pady=(20, 10))

        # Settings container
        settings = tk.Frame(
            self.root,
            bg="#171B22"
        )
        settings.pack(pady=10)

        # Board type label
        tk.Label(
            settings,
            text="Board Type:",
            font=("Arial", 12),
            bg="#171B22",
            fg="white"
        ).grid(row=0, column=0, padx=10)

        # Board type dropdown
        self.board_selector = ttk.Combobox(
            settings,
            textvariable=self.board_type,
            values=["English", "Diamond", "Hexagon"],
            state="readonly",
            width=12
        )
        self.board_selector.grid(
            row=0, column=1, padx=10
        )

        # Board size label
        tk.Label(
            settings,
            text="Board Size:",
            font=("Arial", 12),
            bg="#171B22",
            fg="white"
        ).grid(row=0, column=2, padx=10)

        # Board size dropdown
        self.size_selector = ttk.Combobox(
            settings,
            textvariable=self.board_size,
            values=["7"],
            state="readonly",
            width=6
        )
        self.size_selector.grid(
            row=0, column=3, padx=10
        )

        # New game button
        self.new_game_button = tk.Button(
            self.root,
            text="NEW GAME",
            font=("Arial", 12, "bold"),
            bg="#825536",
            fg="white",
            activebackground="#A56B42",
            activeforeground="white",
            command=self.start_new_game,
            padx=25,
            pady=8,
            cursor="hand2"
        )
        self.new_game_button.pack(pady=15)

        # Canvas for our custom graphics
        self.canvas = tk.Canvas(
            self.root,
            width=850,
            height=600,
            bg="#171B22",
            highlightthickness=0
        )
        self.canvas.pack(pady=10)

        # Listen for mouse clicks
        self.canvas.bind(
            "<Button-1>",
            self.handle_click
        )

        # Remaining peg count
        self.peg_count_label = tk.Label(
            self.root,
            text="",
            font=("Arial", 14, "bold"),
            bg="#171B22",
            fg="#DCE5ED"
        )
        self.peg_count_label.pack(pady=5)

        # Status message
        self.status_label = tk.Label(
            self.root,
            text="Select a peg to begin.",
            font=("Arial", 11),
            bg="#171B22",
            fg="#AAB5C0"
        )
        self.status_label.pack(pady=5)

    def start_new_game(self):

        # Read selected settings
        size = int(self.board_size.get())
        board_type = self.board_type.get()

        # Reset the game
        self.game.new_game(size, board_type)

        # Clear the previous selection
        self.selected_peg = None
        self.game_finished = False

        # Update the screen
        self.draw_board()

        self.update_status(
            "New game started. Select a peg."
        )

    def draw_board(self):

        # Let graphics.py handle all drawing
        self.graphics.draw_board(
            self.game.board,
            self.selected_peg
        )

        # Update the remaining peg count
        self.update_peg_count()

    def handle_click(self, event):

        # Ignore clicks after the game ends
        if self.game_finished:
            return

        # Determine which board position was clicked
        clicked_cell = self.graphics.find_clicked_cell(
            event.x, event.y
        )

        # Ignore clicks outside the board positions
        if clicked_cell is None:
            return

        row, col = clicked_cell

        cell_value = self.game.board.cells[row][col]

        # First click: select a peg
        if self.selected_peg is None:

            if cell_value == 1:
                self.selected_peg = (row, col)
                self.draw_board()

                self.update_status(
                    f"Selected peg at ({row}, {col})."
                )

            return

        # Clicking the same peg deselects it
        if self.selected_peg == (row, col):

            self.selected_peg = None
            self.draw_board()

            self.update_status(
                "Peg deselected."
            )
            return

        # Clicking another peg changes selection
        if cell_value == 1:

            self.selected_peg = (row, col)
            self.draw_board()

            self.update_status(
                f"Selected peg at ({row}, {col})."
            )
            return

        # Attempt to move into an empty hole
        start_row, start_col = self.selected_peg

        move_successful = self.game.make_moves(
            start_row,
            start_col,
            row,
            col
        )

        # Clear the selection
        self.selected_peg = None

        # Redraw the board
        self.draw_board()

        if not move_successful:

            self.update_status(
                "Invalid move. Try again."
            )
            return

        self.update_status(
            "Move completed successfully."
        )

        # Check whether the game has ended
        self.check_game_status()

    def update_peg_count(self):

        peg_count = sum(
            cell == 1
            for row in self.game.board.cells
            for cell in row
        )

        self.peg_count_label.config(
            text=f"Pegs Remaining: {peg_count}"
        )

    def update_status(self, message):

        self.status_label.config(
            text=message
        )

    
    def check_game_status(self):

        if self.game.is_game_over():

            self.game_finished = True

            # Count the remaining pegs
            remaining_pegs = sum(
                row.count(1) for row in self.game.board.cells
            )

            # Determine the player's rating
            if remaining_pegs == 1:
                rating = "Outstanding"
            elif remaining_pegs == 2:
                rating = "Very Good"
            elif remaining_pegs == 3:
                rating = "Good"
            else:
                rating = "Average"

            # Determine the game result
            if self.game.is_game_won():
                result = "Congratulations! You won!"
            else:
                result = "No valid moves remain."

            # Display result, rating, and replay option
            message = (
                f"{result}\n\n"
                f"Pegs remaining: {remaining_pegs}\n"
                f"Your rating: {rating}\n\n"
                "Would you like to play again?"
            )

            play_again = messagebox.askyesno(
                "Game Over",
                message
            )

            if play_again:
                self.start_new_game()
            else:
                self.root.destroy()
