# Masonry Wall Builder

This repository contains three Python programs that simulate and visualize the construction of masonry walls using different brick bond patterns:

- **Stretcher Bond** (`masonry_wall_builder.py`)
- **Flemish Bond** (`masonry_wall_builder_flemish.py`)
- **Wild Bond** (`masonry_wall_builder_wild.py`)

The visualization is interactive, allowing users to step through the building process brick by brick by pressing the ENTER key. The programs optimize the build order to minimize the number of movements (strides) required by a robot, grouping bricks into strides that can be built without repositioning.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Algorithm Logic](#algorithm-logic)
  - [Stretcher Bond](#stretcher-bond)
  - [Flemish Bond](#flemish-bond)
  - [Wild Bond](#wild-bond)
- [Installation](#installation)
- [Usage](#usage)

## Overview
- **Language**: Python 3
- **Library**: Tkinter (for GUI visualization)
- **Patterns**: Stretcher Bond, Flemish Bond, and Wild Bond

The programs dynamically calculate the brick layout based on the wall dimensions and brick sizes. They ensure that the specified bond patterns are correctly implemented, adhering to various constraints to maintain structural integrity and visual appeal.

## Features
- **Wall Visualization**: Displays an entire wall using specified brick bond patterns.
- **Interactive Building**: Allows users to build the wall one brick at a time by pressing the ENTER key.
- **Optimized Build Order**: Minimizes robot movements by grouping bricks into strides based on the robot's reach.
- **Stride Coloring**: Colors each stride differently to visualize the building sequence and robot movements.

## Algorithm Logic

### Stretcher Bond
- **Pattern Description**: Bricks are laid with their long sides parallel to the wall face. Each brick is centered over the joint between two bricks below, creating a staggered pattern.
- **Brick Placement Logic**:
  - **Even Courses**: Start with a full brick at the left edge of the wall.
  - **Odd Courses**: Start with a half brick to create the necessary offset.
  - **Right Edge Alignment**: Ensures bricks at the right edge do not extend beyond the wall width, adjusting the last brick's length if necessary.
- **Optimization**:
  - Bricks are grouped into strides based on the robot's horizontal and vertical reach to minimize repositioning.
  - The build order is determined by sorting bricks from bottom to top and left to right.

### Flemish Bond
- **Pattern Description**: Alternates between stretchers (full bricks) and headers (half bricks) in each course.
  - **Even Courses**: Start with a half brick (header), followed by a full brick (stretcher), and repeat.
  - **Odd Courses**: Start with a full brick, followed by a half brick, and repeat.
- **Brick Placement Logic**:
  - Alternates brick sizes according to the course number and adjusts the last brick to fit the wall width if necessary.
- **Optimization**:
  - Similar to the stretcher bond, bricks are grouped into strides.
  - The build order is optimized to reduce robot movements.

### Wild Bond
- **Pattern Description**: Less regular and includes several constraints to ensure structural integrity.
- **Constraints**:
  - No vertical joints align between courses.
  - Not more than 6 consecutive staggered steps (to avoid a "falling teeth" pattern).
  - No more than 3 consecutive half bricks.
  - No two half bricks next to each other except at edges.
- **Brick Placement Logic**:
  - Generates all possible valid brick patterns for each course that meet the constraints.
  - Selects patterns that avoid aligning vertical joints and adhere to the maximum number of consecutive half bricks.
  - Shifts between courses are introduced to reset the staggered steps counter.
- **Optimization**:
  - Bricks are grouped into strides based on the robot's reach.
  - The build order is optimized, and the strides are colored differently.

## Installation

### Downloading the Code
1. Clone or download this repository to your local machine.
2. Ensure all three Python files are in the same directory:
   - `masonry_wall_builder.py`
   - `masonry_wall_builder_flemish.py`
   - `masonry_wall_builder_wild.py`

## Usage

### Stretcher Bond Usage
1. **Navigate to the Script Location**:
   Open a terminal or command prompt and navigate to the directory containing `masonry_wall_builder.py`.
2. **Run the Program**:
   ```bash
   python masonry_wall_builder.py
