
import math
# from tools.math import CameraCalibration
from gpswidgets.interactivemap import main

# def rotate_points(_points, _degree):
#     radians = _degree/180*math.pi
#     ret = []
#     for point in points:
#         x =  point[0] * math.cos(radians) + point[1] * math.sin(radians)
#         y = -point[0] * math.sin(radians) + point[1] * math.cos(radians)
#         ret.append([x, y])
#     return ret

# def add_to_points(_points, _x, _y):
#     return [[point[0]+_x, point[1]+_y] for point in _points]

# if __name__ == "__main__":
#     points = [[905, 940], [904, 1046], [1198, 1044], [1146, 939]]
    
#     average_x = sum([point[0] for point in points])//len(points)
#     average_y = sum([point[1] for point in points])//len(points)

#     points = [[points[0]-average_x, points[1]-average_y] for points in points]

#     w_points = add_to_points(points, average_x, average_y)
#     cw_points = add_to_points(rotate_points(points, 30), average_x, average_y)
#     ccw_points = add_to_points(rotate_points(points, -30), average_x, average_y)

#     CameraCalibration(w_points, 1435)

main()