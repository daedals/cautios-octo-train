import math
import numpy as np

class CameraCalibration:
    def __init__(self, image_points, real_world_width: int):

        # order points
        a, b, c, d = self.assign_points_to_assumed_order(image_points)

        width = real_world_width

        # Swing angle s is the rotation angle of the camera along its optical axis.
        swing_angle = 0
        # Tilt angle t is the vertical angle of the optical axis of the camera with respect to the X-Y plane of the world coordinate system.
        tilt_angle = 0
        # Pan angle p is therefore the horizontal angle of the optical axis with respect to the X-Z of the world coordinate system.
        pan_angle = 0

        # Helper variables
        alpha_ab, beta_ab, chi_ab = b[0] - a[0], b[1] - a[1], a[0]*b[1] - b[1]*a[0]
        alpha_ac, beta_ac, chi_ac = c[0] - a[0], c[1] - a[1], a[0]*c[1] - c[1]*a[0]
        alpha_bd, beta_bd, chi_bd = d[0] - b[0], d[1] - b[1], b[0]*d[1] - d[1]*b[0]
        alpha_cd, beta_cd, chi_cd = d[0] - c[0], d[1] - c[1], c[0]*d[1] - d[1]*c[0]

        # calculation of swing angle s
        num = - beta_ab * beta_ac * chi_bd * alpha_cd + beta_ac * alpha_bd * beta_ab * chi_cd \
              + beta_cd * chi_ab * beta_bd * alpha_ac - beta_ab * chi_cd * beta_bd * alpha_ac \
              - beta_cd * beta_bd * chi_ac * alpha_ab - beta_ac * chi_ab * alpha_bd * beta_cd \
              + beta_ab * chi_ac * beta_bd * alpha_cd + beta_cd * beta_ac * chi_bd * alpha_ab

        denom = - beta_ab * chi_ac * alpha_bd * alpha_cd + beta_ac * chi_ab * alpha_bd * alpha_cd \
                - beta_ac * alpha_bd * alpha_ab * chi_cd - alpha_ac * chi_bd * beta_cd * alpha_ab \
                - alpha_cd * chi_ab * beta_bd * alpha_ac + beta_ab * alpha_ac * chi_bd * alpha_cd \
                + alpha_ab * chi_cd * beta_bd * alpha_ac + alpha_bd * chi_ac * beta_cd * alpha_ab

        print(num, denom)

        if denom == 0:
            swing_angle = np.pi/2
        else:
            tan_s = num / denom
            swing_angle = np.arctan(tan_s)

        print(swing_angle / np.pi * 180)

        # helper variables for angular functions of the swing angle s
        sin_s = np.sin(swing_angle)
        cos_s = np.cos(swing_angle)

        # calculation of tilt angle t
        num = ((alpha_bd * chi_ac - alpha_ac * chi_bd) * sin_s + (beta_bd * chi_ac - beta_ac * chi_bd) * cos_s) * \
              ((alpha_cd * chi_ab - alpha_ab * chi_cd) * sin_s + (beta_cd * chi_ab - beta_ab * chi_cd) * cos_s)

        denom = ((alpha_cd * chi_ab - alpha_ab * chi_cd) * cos_s + (beta_ab * chi_cd - beta_cd * chi_ab) * sin_s) * \
                ((beta_bd * chi_ac - beta_ac * chi_bd) * sin_s + (alpha_ac * chi_bd - alpha_bd * chi_ac) * cos_s)

        print(num, denom)

        if denom == 0:
            sin_t = 0
        else:
            sin_t = (num/denom)**(1/2)
        tilt_angle = np.arcsin(sin_t)

        print(tilt_angle)

        # helper variables for angular functions of the tilt angle
        cos_t = np.cos(tilt_angle)

        # calculation of pan angle p
        num = sin_t * ((beta_bd * chi_ac - beta_ac * chi_bd) * sin_s + \
                      (alpha_ac * chi_bd - alpha_bd * chi_ac) * cos_s)
        denom = (alpha_bd * chi_ac - alpha_ac * chi_bd) * sin_s + \
                (beta_bd * chi_ac - beta_ac * chi_bd) * cos_s

        if denom == 0:
            pan_angle = np.pi/2
        else:
            tan_p = num/denom
            pan_angle = np.arctan(tan_p)
        
        # helper variables for angular functions of the pan angle
        sin_p = np.sin(pan_angle)
        cos_p = np.cos(pan_angle)

        # calculation of focal length f
        num = chi_bd * cos_p * cos_t
        denom = beta_bd * sin_p * cos_s - beta_bd * cos_p * sin_t * sin_s + \
                alpha_bd * sin_p * sin_s + alpha_bd * cos_p * sin_t * cos_s
        
        focal_length = num/denom

        # calculation of camera distance
        num = width * (focal_length * sin_t + a[0] * cos_t * sin_s + a[1] * cos_t * cos_s) * \
                      (focal_length * sin_t + c[0] * cos_t * sin_s + c[1] * cos_t * cos_s)
        
        denom = -(focal_length * sin_t + a[0] * cos_t * sin_s + a[1] * cos_t * cos_s) * \
          (c[0] * cos_p * sin_s - c[0] * sin_p * sin_t * cos_s + c[1] * cos_p * cos_s + c[1] * sin_p * sin_t * sin_s) + \
          (focal_length * sin_t + c[0] * cos_t * sin_s + c[1] * cos_t * cos_s) * \
          (a[0] * cos_p * sin_s - a[0] * sin_p * sin_t * cos_s + a[1] * cos_p * cos_s + a[1] * sin_p * sin_t * sin_s)

        length_to_world_plane = num/denom

        print(swing_angle, tilt_angle, pan_angle, focal_length, length_to_world_plane)

    def assign_points_to_assumed_order(self, _image_points):
        """ assigns points to their assumed order in the paper, returns a, b, c, d
        The equation of the paper assume a certain order of points namely:
         -------> Y
        |  A    C
        |
        |  B    D
        v
        X
        """
        # sort by addition of their coordinate values
        sorted_points = sorted(_image_points, key= lambda point: point[0]+point[1])
        # we can assume a it sorted to either ABCD or ACBD (this might not always be true but in case of this application it is safe to assume so)
        a = sorted_points[0]
        d = sorted_points[3]

        # compare x values of second and third point
        if sorted_points[1][0] > sorted_points[2][0]:
            b = sorted_points[1]
            c = sorted_points[2]
        else:
            b = sorted_points[2]
            c = sorted_points[1]

        print(_image_points)
        print(a, b, c, d)

        return a, b, c, d
