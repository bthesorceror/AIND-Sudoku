""" Solving sudokus """

from collections import defaultdict
from functools import partial
from itertools import product
from visualize import visualize_assignments

def cross(first, second):
    "Cross product of elements in first and elements in second."

    return [a+b for a in first for b in second]

def rows():
    """ returns valid rows """

    return 'ABCDEFGHI'

def cols():
    """ returns valid columns """

    return '123456789'

def build_unit_list():
    """builds unit list"""

    row_units = [cross(current_row, cols()) for current_row in rows()]
    column_units = [cross(rows(), current_column) for current_column in cols()]
    srows = ('ABC', 'DEF', 'GHI')
    scols = ('123', '456', '789')
    square_units = [cross(crows, ccols) for crows in srows for ccols in scols]
    diagonal_units = ["A1, B2, C3, D4, E5, F6, G7, H8, I9".split(", "),
                      "I1, H2, G3, F4, E5, D6, C7, B8, A9".split(", ")]

    return row_units + column_units + square_units + diagonal_units

assignments = []
boxes = cross(rows(), cols())
unitlist = build_unit_list()
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    values[box] = value

    if len(value) == 1:
        assignments.append(values.copy())

    return values

def remove_twins(values, unit, numbers):
    """removes naked twins from all other boxes"""

    for box, num in product(unit, numbers):
        values[box] = values[box].replace(num, "")

def valid_twins(values, first, second):
    """
    Validates that boxes are naked twins
    """

    return first != second and len(values[first]) == 2 and values[first] == values[second]


def naked_twins(values):
    """
    Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    result = dict(values)
    removal = partial(remove_twins, result)
    validate = partial(valid_twins, result)

    for unit in unitlist:
        for box, other in product(unit, unit):
            if validate(box, other):
                removal([cbox for cbox in unit if cbox != box and cbox != other], result[box])

    return result

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'.
                    If the box has no value, then the
                    value will be '123456789'.
    """

    result = {}

    for index, key in enumerate(boxes):
        if grid[index] == ".":
            result[key] = "123456789"
        else:
            result[key] = grid[index]

    return result

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """

    lengths = [len(values[s]) for s in boxes]
    width = 1 + max(lengths)
    line = '+'.join(['-' * (width * 3)] * 3)

    for crow in rows():
        print(''.join(values[crow + ccol].center(width) + ('|' if ccol in '36' else '')
                      for ccol in cols()))
        if crow in 'CF':
            print(line)

def eliminate(values):
    """
    Eliminate values from peers of each box with a single value.

    Go through all the boxes, and whenever there is a box with a single value,
    eliminate this value from the set of values of all its peers.

    Args:
        values: Sudoku in dictionary form.
    Returns:
        Resulting Sudoku in dictionary form after eliminating values.
    """

    for key in values:
        if len(values[key]) == 1:
            value = values[key][0]
            current_peers = peers[key]

            for peer in current_peers:
                assign_value(values, peer, values[peer].replace(value, ""))

    return values

def only_choice(values):
    """
    Finalize all values that are the only choice for a unit.

    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.

    Input: Sudoku in dictionary form.
    Output: Resulting Sudoku in dictionary form after filling in only choices.
    """

    new_values = values.copy()  # note: do not modify original values

    for unit in unitlist:
        tracker = defaultdict(list)

        for unit_key in unit:
            for number in values[unit_key]:
                tracker[number].append(unit_key)

        for option, box_list in tracker.items():
            if len(box_list) == 1:
                assign_value(new_values, box_list[0], option)

    return new_values

def reduce_puzzle(values):
    """ Reduces the number of options for each box in the puzzle """

    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        values = only_choice(eliminate(dict(values)))

        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False

    return values

def solved(values):
    """ returns if the current game is solved """

    return len([0 for value in values.values() if len(value) != 1]) == 0

def find_best_option(values):
    """
    Find box key with the least amount of options
    that has multiple options
    """

    result_key = None
    result_count = 9

    for key, value in values.items():
        count = len(value)
        if count < result_count and count > 1:
            result_key = key
            result_count = count

    return result_key

def search(values, strategy=naked_twins):
    """
    Using depth-first search and propagation,
    create a search tree and solve the sudoku.
    """

    reduced = strategy(reduce_puzzle(dict(values)))

    if not reduced:
        return values
    if solved(reduced):
        return reduced
    else:
        best_option = find_best_option(reduced)
        best_values = reduced[best_option]

        for num in best_values:
            current = dict(reduced)
            assign_value(current, best_option, num)
            result = search(current)

            if solved(result):
                return result

        return reduced

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
        Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """

    return search(grid_values(grid))

if __name__ == '__main__':
    DIAG_SUDOKU_GRID = '2.............62....1....7...6..8...' + \
                       '3...9...7...6..4...4....8....52.............3'
    display(solve(DIAG_SUDOKU_GRID))

    try:
        visualize_assignments(assignments)
    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue.')
        print('Not a problem! It is not a requirement.')
