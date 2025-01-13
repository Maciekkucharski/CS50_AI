import itertools
import random
from typing import Set, List, Tuple
import copy
class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """
    def __init__(self, cells: List[Tuple], count: int):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self)-> Set[Tuple]: 
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        return self.cells if self.count == len(self.cells) else set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        return self.cells if not self.count else set()

    def mark_mine(self, cell: Set):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell not in self.cells:
            return
        self.cells.remove(cell)
        self.count -= 1

    def mark_safe(self, cell: Set):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell not in self.cells:
            return
        self.cells.remove(cell)

class MinesweeperAI():
    """
    Minesweeper game player
    """
    def __init__(self, height=8, width=8):
        # Set initial height and width
        self.height = height
        self.width = width
        # Keep track of which cells have been clicked on
        self.moves_made = set()
        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()
        # List of sentences about the game known to be true
        self.knowledge: List[Sentence] = []

    def mark_mine(self, cell: Set):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell: Set):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell: Set, count: int):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        self.moves_made.add(cell)
        self.mark_safe(cell)
        self.knowledge.append(self.create_sentence(cell, count))
        changes = True
        while changes:
            changes = False
            #Infere new sentences
            for sentence in copy.deepcopy(self.knowledge):
                    for sentence_2 in copy.deepcopy(self.knowledge):
                        if sentence==sentence_2:
                            continue
                        sentence_difference = None
                        infered_sentence = None
                        if sentence_2.cells.issubset(sentence.cells):
                            sentence_difference = sentence.cells.difference(sentence_2.cells)
                            infered_sentence = Sentence(sentence_difference, sentence.count - sentence_2.count)
                        elif sentence.cells.issubset(sentence_2.cells):
                            sentence_difference = sentence_2.cells.difference(sentence.cells)
                            infered_sentence = Sentence(sentence_difference, sentence_2.count - sentence.count)
                        if infered_sentence and infered_sentence not in self.knowledge:
                            self.knowledge.append(infered_sentence)
                            changes = True
            #mark known safe and mines fields and remove empty sentences
            for sentence in copy.deepcopy(self.knowledge):
                for save in sentence.known_safes():
                    changes = True
                    self.mark_safe(save)
                for mine in sentence.known_mines():
                    changes = True
                    self.mark_mine(mine)
            for sentence in copy.deepcopy(self.knowledge):
                if not sentence.cells:
                    self.knowledge.remove(sentence)

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for safe in self.safes:
            if safe not in self.moves_made:
                return safe

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        moves = [(x,y) for x in range(self.height) for y in range(self.width)]
        for move in moves:
            if move not in self.moves_made and move not in self.mines:
                return move

    def create_sentence(self, cell: Set, count: int)-> Sentence:
        cells = [(cell[0] + column, cell[1] + row) for row in range(-1, 2) for column in range(-1, 2) if 0<=cell[1]+row<self.width and 0<=cell[0]+column<self.height and not (cell[1] + row == cell[1] and cell[0]+column == cell[0])]
        for new_cell in copy.deepcopy(cells):
            if new_cell in self.safes:
                cells.remove(new_cell)
            if new_cell in self.mines:
                cells.remove(new_cell)
                count -=1
        return Sentence(cells, count)

