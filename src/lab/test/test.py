import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.interpolate import CloughTocher2DInterpolator

# Given data
X = [0, 0, 0, 1, -1, -1, 1, -1, 1]
Y = [0, 1, -1, 0, 0, 1, 1, -1, -1]
L = [0, 100, -100, 100, -100, 50, 100, -50, -100]
R = [0, 100, -100, -100, 100, 100, 50, -100, -50]

# Create a structured array for points
points = np.array(list(zip(X, Y)))

# Define functions for left and right
def fLeft(X, Y):
    interp_function = CloughTocher2DInterpolator(points, L)
    result = interp_function(X, Y)
    return interp_function, result

def fRight(X, Y):
    interp_function = CloughTocher2DInterpolator(points, R)
    result = interp_function(X, Y)
    return interp_function, result

# Example usage
x_test = np.linspace(-1, 1, 100)
y_test = np.linspace(-1, 1, 100)
X_test, Y_test = np.meshgrid(x_test, y_test)

left_interp_function, left_result = fLeft(X_test, Y_test)
right_interp_function, right_result = fRight(X_test, Y_test)

# Visualization
fig = plt.figure(figsize=(12, 6))

# Left function
ax_left = fig.add_subplot(121, projection='3d')
ax_left.plot_surface(X_test, Y_test, left_result, cmap='viridis')
ax_left.set_title('fLeft(X, Y) Surface')

# Right function
ax_right = fig.add_subplot(122, projection='3d')
ax_right.plot_surface(X_test, Y_test, right_result, cmap='viridis')
ax_right.set_title('fRight(X, Y) Surface')

plt.show()
