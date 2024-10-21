import tkinter as tk
from tkinter import messagebox
import random

# Brick and wall dimensions
BRICK_FULL_LENGTH = 210       # Length of a full brick in mm
BRICK_HALF_LENGTH = 105       # Length of a half brick in mm (should be half of full brick including cuts)
BRICK_WIDTH = 100             # Width of a brick in mm
BRICK_HEIGHT = 50             # Height of a brick in mm
HEAD_JOINT = 10               # Vertical joint size in mm
BED_JOINT = 12.5              # Horizontal joint size in mm
COURSE_HEIGHT = BRICK_HEIGHT + BED_JOINT  # Height of one course (brick plus bed joint)

WALL_WIDTH = 2300             # Total wall width in mm
WALL_HEIGHT = 2000            # Total wall height in mm

# Robot stride dimensions
STRIDE_WIDTH = 800            # Robot's horizontal reach in mm
STRIDE_HEIGHT = 1300          # Robot's vertical reach in mm

# Calculate the number of courses (rows of bricks)
NUM_COURSES = int(WALL_HEIGHT // COURSE_HEIGHT)

def generate_random_color():
    # Generate a random hex color code
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))

class Brick:
    # Class representing a single brick
    def __init__(self, x, y, length, is_built=False, stride=0):
        self.x = x                    # X-coordinate of the brick's top-left corner
        self.y = y                    # Y-coordinate of the brick's top-left corner
        self.length = length          # Length of the brick (full or half)
        self.is_built = is_built      # Whether the brick has been built
        self.stride = stride          # The stride number the brick belongs to
        self.color = "light grey"     # Color of the brick (changes after assignment to a stride)

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
    def __init__(self):
        self.bricks = []              # List to store all bricks
        self.current_brick_index = 0  # Index to track the current brick being built
        self.stride_colors = {}       # Dictionary to store colors for each stride
        self.calculate_bricks()       # Initialize bricks layout
        self.optimize_build_order()   # Optimize the build order to minimize robot movements

    def calculate_bricks(self):
        # Calculate the positions and sizes of all bricks in the wall
        y = WALL_HEIGHT - COURSE_HEIGHT  # Start from the bottom
        for course in range(NUM_COURSES):
            x = 0
            is_even_course = (course % 2 == 0)
            bricks_in_course = []

            if is_even_course:
                # Even courses start with a full brick
                while x < WALL_WIDTH:
                    length = BRICK_FULL_LENGTH
                    # Adjust length to not exceed wall width
                    if x + length > WALL_WIDTH:
                        length = WALL_WIDTH - x  # Adjust last brick to fit wall width
                    brick = Brick(x, y, length)
                    bricks_in_course.append(brick)
                    x += length + HEAD_JOINT
            else:
                # Odd courses start with a half brick
                length = BRICK_HALF_LENGTH
                brick = Brick(x, y, length)
                bricks_in_course.append(brick)
                x += length + HEAD_JOINT

                # Add full bricks
                while x + BRICK_FULL_LENGTH <= WALL_WIDTH:
                    length = BRICK_FULL_LENGTH
                    brick = Brick(x, y, length)
                    bricks_in_course.append(brick)
                    x += length + HEAD_JOINT

                # Add half brick if needed
                if x < WALL_WIDTH:
                    length = BRICK_HALF_LENGTH
                    brick = Brick(x, y, length)
                    bricks_in_course.append(brick)
                    x += length + HEAD_JOINT

            self.bricks.extend(bricks_in_course)
            y -= COURSE_HEIGHT  # Move up to the next course

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
        self.root.title("Masonry Wall Builder - Stretcher Bond")

        # Dynamically adjust the scale to fit the entire wall in the window
        self.scale = min(800 / WALL_WIDTH, 600 / WALL_HEIGHT)

        self.canvas_width = int(WALL_WIDTH * self.scale) + 20  # Canvas width with margin
        self.canvas_height = int(WALL_HEIGHT * self.scale) + 20  # Canvas height with margin

        self.canvas = tk.Canvas(root, width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack()

        self.wall = Wall()
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
