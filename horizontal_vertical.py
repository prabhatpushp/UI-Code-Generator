import numpy as np


def check_approx_alignment(points, tolerance=0.5):
    x_coords, y_coords = zip(*points)  # Separate x and y coordinates

    std_x = np.std(x_coords)  # Standard deviation of x values
    std_y = np.std(y_coords)  # Standard deviation of y values

    if std_y <= tolerance:
        return "Approximately Horizontally Aligned"
    elif std_x <= tolerance:
        return "Approximately Vertically Aligned"
    else:
        return "Not Aligned"


# Example usage
points1 = [(1, 3), (4, 3.1), (6, 2.9)]  # Almost horizontally aligned
points2 = [(5.1, 1), (5, 4), (5.2, 7)]  # Almost vertically aligned
points3 = [(1, 2), (3, 4), (5, 6)]  # Not aligned

# Output: Approximately Horizontally Aligned
print(check_approx_alignment(points1))
# Output: Approximately Vertically Aligned
print(check_approx_alignment(points2))
print(check_approx_alignment(points3))  # Output: Not Aligned
