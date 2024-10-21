import tkinter as tk
from tkinter import messagebox
import random
import itertools

# Brick and wall dimensions (in mm)
BRICK_FULL_LENGTH = 210       # Length of a full brick
BRICK_HALF_LENGTH = 100       # Length of a half brick
BRICK_WIDTH = 100             # Width of a brick
BRICK_HEIGHT = 50             # Height of a brick
HEAD_JOINT = 10               # Vertical joint size
BED_JOINT = 12.5              # Horizontal joint size
COURSE_HEIGHT = BRICK_HEIGHT + BED_JOINT  # Height of one course

WALL_WIDTH = 2300             # Total wall width
WALL_HEIGHT = 2000            # Total wall height

# Robot stride dimensions (in mm)
STRIDE_WIDTH = 800            # Robot's horizontal reach
STRIDE_HEIGHT = 1300          # Robot's vertical reach

# Calculate the number of courses (rows of bricks)
NUM_COURSES = int(WALL_HEIGHT // COURSE_HEIGHT)

def generate_random_color():
    # Generate a random hex color code
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))

def generate_valid_course_patterns(wall_width):
    # Generate all possible valid brick patterns for a course that meet the constraints
    patterns = []
    brick_lengths = [BRICK_FULL_LENGTH, BRICK_HALF_LENGTH]
    max_bricks = wall_width // (min(brick_lengths) + HEAD_JOINT) + 1

    # Generate all combinations of brick lengths up to the maximum number of bricks that can fit
    for num_bricks in range(1, max_bricks + 1):
        # Generate all possible combinations with replacement
        for combination in itertools.product(brick_lengths, repeat=num_bricks):
            # Calculate total length including head joints
            total_length = sum(combination) + HEAD_JOINT * (num_bricks - 1)
            if total_length == wall_width:
                # Check for Constraint 4: No two half bricks next to each other except at edges
                valid = True
                for i in range(1, len(combination) - 1):
                    if combination[i] == BRICK_HALF_LENGTH and combination[i - 1] == BRICK_HALF_LENGTH:
                        valid = False
                        break
                if valid:
                    patterns.append(list(combination))
    return patterns

def is_pattern_valid(pattern, previous_joints):
    # Check if the pattern is valid against the constraints
    current_joints = []
    x = 0
    for length in pattern[:-1]:  # Exclude the last brick to avoid extra head joint
        x += length + HEAD_JOINT
        current_joints.append(x)

    # Constraint 1: No two head joints directly on top of each other
    for cj in current_joints:
        for pj in previous_joints:
            if abs(cj - pj) < 1e-6:
                return False  # Joint alignment too close

    # Constraint 4: No two half bricks next to each other except at edges
    for i in range(1, len(pattern) - 1):
        if pattern[i] == BRICK_HALF_LENGTH and pattern[i - 1] == BRICK_HALF_LENGTH:
            return False

    return True

def create_bricks_from_pattern(pattern, y):
    # Create Brick objects from the given pattern at the specified y-coordinate
    bricks = []
    x = 0
    for length in pattern:
        brick = Brick(x, y, length)
        bricks.append(brick)
        x += length + HEAD_JOINT
    return bricks

def compute_shift(current_pattern, previous_pattern):
    # Compute the horizontal shift between current and previous patterns
    # Calculate x-coordinate of the first head joint in current and previous patterns
    x_current = current_pattern[0]
    x_previous = previous_pattern[0]
    shift = x_current - x_previous
    return shift

class Brick:
    # Class representing a single brick
    def __init__(self, x, y, length, is_built=False, stride=0):
        self.x = x                    # X-coordinate of the brick's top-left corner
        self.y = y                    # Y-coordinate of the brick's top-left corner
        self.length = length          # Length of the brick (full or half)
        self.is_built = is_built      # Whether the brick has been built
        self.stride = stride          # The stride number the brick belongs to
        self.color = "light grey"     # Color of the brick

    def draw(self, canvas, scale):
        # Draw the brick on the canvas
        x1 = self.x * scale + 10      # Scaled x-coordinate with margin
        y1 = self.y * scale + 10      # Scaled y-coordinate with margin
        x2 = (self.x + self.length) * scale + 10
        y2 = (self.y + BRICK_HEIGHT) * scale + 10

        fill_color = self.color if self.is_built else "white"  # Color based on build status
        canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline="black")

class Wall:
    # Class representing the wall composed of bricks
    def __init__(self, bond_type="wild"):
        self.bricks = []              # List to store all bricks
        self.current_brick_index = 0  # Index to track the current brick being built
        self.stride_colors = {}       # Dictionary to store colors for each stride
        self.bond_type = bond_type    # Type of brick bond
        self.staggered_steps_counter = 1  # Initialize staggered steps counter
        self.previous_shift = 0            # Initialize previous shift
        self.calculate_bricks()       # Initialize bricks layout
        self.optimize_build_order()   # Optimize the build order

    def calculate_bricks(self):
        # Calculate the positions and sizes of all bricks in the wall
        valid_patterns = generate_valid_course_patterns(WALL_WIDTH)
        if not valid_patterns:
            messagebox.showerror("Error", "No valid patterns could be generated for the wall width.")
            return

        y = WALL_HEIGHT - BRICK_HEIGHT  # Start from the bottom (excluding bed joints in drawing)
        previous_course_joints = []
        previous_course_pattern = None
        for course_number in range(NUM_COURSES):
            random.shuffle(valid_patterns)  # Randomize patterns to maintain randomness
            pattern_found = False
            for pattern in valid_patterns:
                # Compute current shift
                if previous_course_pattern is not None:
                    current_shift = compute_shift(pattern, previous_course_pattern)
                    if abs(current_shift - self.previous_shift) < 1e-6:
                        attempted_staggered_steps_counter = self.staggered_steps_counter + 1
                    else:
                        attempted_staggered_steps_counter = 1
                else:
                    current_shift = 0  # First course, shift is 0
                    attempted_staggered_steps_counter = 1

                if attempted_staggered_steps_counter > 6:
                    continue  # Skip this pattern, shift has occurred too many times

                # Check if pattern is valid
                is_valid = is_pattern_valid(pattern, previous_course_joints)

                if is_valid:
                    # Accept the pattern
                    self.staggered_steps_counter = attempted_staggered_steps_counter
                    self.previous_shift = current_shift
                    previous_course_pattern = pattern

                    bricks_in_course = create_bricks_from_pattern(pattern, y)
                    # Record current course head joint positions
                    current_course_joints = []
                    x = 0
                    for length in pattern[:-1]:  # Exclude the last brick to avoid extra head joint
                        x += length + HEAD_JOINT
                        current_course_joints.append(x)
                    # Update previous_course_joints
                    previous_course_joints = current_course_joints
                    # Add bricks to the wall
                    self.bricks.extend(bricks_in_course)
                    pattern_found = True
                    break
            if not pattern_found:
                # If no valid pattern is found, report and proceed
                print(f"Unable to find a valid pattern for course {course_number + 1}")
                # For simplicity, we'll proceed without adding bricks
                previous_course_joints = []  # Reset to allow next course to generate
                self.staggered_steps_counter = 1  # Reset counter
                self.previous_shift = 0
                previous_course_pattern = None
            y -= COURSE_HEIGHT  # Move up to the next course (including bed joints in calculation)

    def optimize_build_order(self):
        # Optimize the build order to minimize robot movements by grouping bricks into strides
        stride_number = 1
        current_stride_bricks = []
        current_stride_area = [0, WALL_HEIGHT - STRIDE_HEIGHT, STRIDE_WIDTH, WALL_HEIGHT]
        self.build_order = []

        # Sort bricks by position (bottom to top, left to right)
        for brick in sorted(self.bricks, key=lambda b: (-b.y, b.x)):
            brick_center_x = brick.x + brick.length / 2
            brick_center_y = brick.y + BRICK_HEIGHT / 2

            # Check if the brick is within the current stride area
            if (current_stride_area[0] <= brick_center_x <= current_stride_area[2] and
                current_stride_area[1] <= brick_center_y <= current_stride_area[3]):
                brick.stride = stride_number
                current_stride_bricks.append(brick)
            else:
                # Assign a random color to the completed stride
                color = generate_random_color()
                self.stride_colors[stride_number] = color
                for b in current_stride_bricks:
                    b.color = color
                self.build_order.extend(current_stride_bricks)

                # Start a new stride
                stride_number += 1
                current_stride_bricks = [brick]
                brick.stride = stride_number
                current_stride_area = [
                    brick.x, brick.y - STRIDE_HEIGHT + BRICK_HEIGHT,
                    brick.x + STRIDE_WIDTH, brick.y + BRICK_HEIGHT
                ]

        # Add the last stride
        if current_stride_bricks:
            color = generate_random_color()
            self.stride_colors[stride_number] = color
            for b in current_stride_bricks:
                b.color = color
            self.build_order.extend(current_stride_bricks)

    def build_next_brick(self, canvas, scale):
        # Build the next brick in the optimized build order
        if self.current_brick_index < len(self.build_order):
            brick = self.build_order[self.current_brick_index]
            brick.is_built = True
            brick.draw(canvas, scale)
            self.current_brick_index += 1
        else:
            messagebox.showinfo("Notice", "All bricks have been built.")

    def draw(self, canvas, scale):
        # Draw all bricks on the canvas
        for brick in self.bricks:
            brick.draw(canvas, scale)

class App:
    # Main application class to run the Tkinter GUI
    def __init__(self, root):
        self.root = root
        self.root.title("Masonry Wall Builder - Wild Bond")

        # Dynamically adjust the scale to fit the entire wall in the window
        self.scale = min(800 / WALL_WIDTH, 600 / WALL_HEIGHT)

        self.canvas_width = int(WALL_WIDTH * self.scale) + 20  # Canvas width with margin
        self.canvas_height = int(WALL_HEIGHT * self.scale) + 20  # Canvas height with margin

        self.canvas = tk.Canvas(root, width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack()

        self.wall = Wall(bond_type="wild")  # Specify the bond type here
        self.draw_wall()

        # Bind the ENTER key to build the next brick
        self.root.bind('<Return>', self.build_next_brick)

    def draw_wall(self):
        # Draw the initial wall design
        self.wall.draw(self.canvas, self.scale)

    def build_next_brick(self, event):
        # Handle the event to build the next brick when ENTER is pressed
        self.wall.build_next_brick(self.canvas, self.scale)

def main():
    # Main function to start the Tkinter application
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
