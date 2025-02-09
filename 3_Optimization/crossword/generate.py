import sys
from typing import Dict, Set, List
from crossword import Crossword, Variable
import copy

class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword: Crossword = crossword
        self.domains: Dict[Variable, Set[str]] = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for variable in self.domains:
            self.domains[variable] = set([val for val in self.domains[variable] if len(val)==variable.length])


    def revise(self, x:Variable, y:Variable):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revision = False
        overlap_cell = list(set(x.cells) & set(y.cells))
        if not overlap_cell:
            return revision
        overlap_cell=overlap_cell[0]
        index_x = x.cells.index(overlap_cell)
        index_y = y.cells.index(overlap_cell)
        for word_x in self.domains[x].copy():
            correct_overlap = [word_y for word_y in self.domains[y] if word_x[index_x] == word_y[index_y]]
            if not correct_overlap:
                revision = True
                self.domains[x].remove(word_x)
        return revision

    def ac3(self, arcs: List=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs == None:
            arcs=[]
            for var in self.domains:
                arcs.extend([(var, x) for x in self.crossword.neighbors(var)])
            arcs = list(set(arcs))
        while arcs:
            x, y = arcs.pop(0)
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False
                neighbors = self.crossword.neighbors(x).copy()
                neighbors.remove(y)
                for var in neighbors:
                    if (var, x) not in arcs:
                        arcs.append((var, x))
        return True

    def assignment_complete(self, assignment: Dict[Variable, str]):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        return all([var in assignment for var in self.domains])

    def consistent(self, assignment: Dict[Variable, str]):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        consistent = True
        for variable, assign in assignment.items():
            if variable.length != len(assign):
                consistent = False
                break
            if list(assignment.values()).count(assign)!= 1:
                consistent = False
                break
            neighbors = self.crossword.neighbors(variable)
            for neighbor in neighbors:
                if neighbor not in assignment:
                    continue
                overlap_cell = list(set(variable.cells) & set(neighbor.cells))[0]
                variable_index = variable.cells.index(overlap_cell)
                neighbor_index = neighbor.cells.index(overlap_cell)
                if assignment[neighbor][neighbor_index] != assignment[variable][variable_index]:
                    consistent = False
                    break
        return consistent

    def order_domain_values(self, var: Variable, assignment: Dict[Variable, str]):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        neighbors = self.crossword.neighbors(var)
        constraints_dict = {}
        for var_word in self.domains[var]:
            constraints_dict[var_word] = 0
            for neighbor in neighbors:
                if neighbor in assignment:
                    continue
                overlap_cell = list(set(var.cells) & set(neighbor.cells))[0]
                var_index = var.cells.index(overlap_cell)
                neighbor_index = neighbor.cells.index(overlap_cell)
                incorrect_overlaps = [word_neighbor for word_neighbor in self.domains[neighbor] if var_word[var_index] != word_neighbor[neighbor_index]]
                constraints_dict[var_word]+=len(incorrect_overlaps)
        return [dict_items[0] for dict_items in sorted(constraints_dict.items(), key=lambda item: item[1])]
                

    def select_unassigned_variable(self, assignment: Dict[Variable, str]):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned = list(set(self.domains.keys()) - set(assignment.keys()))
        unassigned.sort(key = lambda x: (len(self.domains[x]), -len(self.crossword.neighbors(x))))
        return unassigned[0]

    def backtrack(self, assignment: Dict[Variable, str]):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        var = self.select_unassigned_variable(assignment)
        domains_copy = copy.deepcopy(self.domains)
        for val in self.order_domain_values(var, assignment):
            assignment[var] = val
            if self.consistent(assignment):
                self.domains[var] = {val}
                if (result:=self.backtrack(assignment)) and self.ac3([(other_var, var) for other_var in self.crossword.neighbors(var)]):
                    return result
            del assignment[var]
            self.domains = domains_copy
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
