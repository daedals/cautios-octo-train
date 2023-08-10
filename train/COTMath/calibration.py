from math import sin, asin, cos, atan2, degrees, sqrt
# import numpy as np

class CameraCalibration:
    def __init__(self, image_points, real_world_width: int):

        # order points
        a, b, c, d = self.assign_points_to_assumed_order(image_points)
        width = real_world_width

        x_2D = [a[0], b[0], c[0], d[0]]
        y_2D = [a[1], b[1], c[1], d[1]]

        A, B, C = get_abc(x_2D, y_2D)
        S = get_s(A, B, C)
        s, t, p, f, h = FY(x_2D, y_2D, A, B, C, S, width)
        print(degrees(s), degrees(t), degrees(p), f, h)

        # Swing angle s is the rotation angle of the camera along its optical axis.
        swing_angle = 0
        # Tilt angle t is the vertical angle of the optical axis of the camera
        # with respect to the X-Y plane of the world coordinate system.
        tilt_angle = 0
        # Pan angle p is the horizontal angle of the optical axis of the camera with respect
        # to the Y axis of the world coordinate system
        pan_angle = 0

        # Helper variables
        alpha_ab, beta_ab, chi_ab = b[0] - a[0], b[1] - a[1], a[0]*b[1] - b[0]*a[1]
        alpha_ac, beta_ac, chi_ac = c[0] - a[0], c[1] - a[1], a[0]*c[1] - c[0]*a[1]
        alpha_bd, beta_bd, chi_bd = d[0] - b[0], d[1] - b[1], b[0]*d[1] - d[0]*b[1]
        alpha_cd, beta_cd, chi_cd = d[0] - c[0], d[1] - c[1], c[0]*d[1] - d[0]*c[1]

        # calculation of swing angle s
        num = - beta_ab * beta_ac * chi_bd * alpha_cd + beta_ac * alpha_bd * beta_ab * chi_cd \
              + beta_cd * chi_ab * beta_bd * alpha_ac - beta_ab * chi_cd * beta_bd * alpha_ac \
              - beta_cd * beta_bd * chi_ac * alpha_ab - beta_ac * chi_ab * alpha_bd * beta_cd \
              + beta_ab * chi_ac * beta_bd * alpha_cd + beta_cd * beta_ac * chi_bd * alpha_ab

        den = - beta_ab * chi_ac * alpha_bd * alpha_cd + beta_ac * chi_ab * alpha_bd * alpha_cd \
              - beta_ac * alpha_bd * alpha_ab * chi_cd - alpha_ac * chi_bd * beta_cd * alpha_ab \
              - alpha_cd * chi_ab * beta_bd * alpha_ac + beta_ab * alpha_ac * chi_bd * alpha_cd \
              + alpha_ab * chi_cd * beta_bd * alpha_ac + alpha_bd * chi_ac * beta_cd * alpha_ab

        # tan_s = num / den
        swing_angle = atan2(num, den)

        print("swing angle:", degrees(swing_angle))

        # helper variables for angular functions of the swing angle s
        sin_s = sin(swing_angle)
        cos_s = cos(swing_angle)

        # calculation of tilt angle t
        num = ((alpha_bd * chi_ac - alpha_ac * chi_bd) * sin_s + (beta_bd * chi_ac - beta_ac * chi_bd) * cos_s) * \
              ((alpha_cd * chi_ab - alpha_ab * chi_cd) * sin_s + (beta_cd * chi_ab - beta_ab * chi_cd) * cos_s)

        den = ((alpha_cd * chi_ab - alpha_ab * chi_cd) * cos_s + (beta_ab * chi_cd - beta_cd * chi_ab) * sin_s) * \
              ((beta_bd * chi_ac - beta_ac * chi_bd) * sin_s + (alpha_ac * chi_bd - alpha_bd * chi_ac) * cos_s)

        if num/den < 0:
            num = -num

        sin_t = (num/den)**(1/2)
        tilt_angle = asin(sin_t)

        print("tilt angle:", degrees(tilt_angle))

        # helper variables for angular functions of the tilt angle
        cos_t = cos(tilt_angle)

        # calculation of pan angle p
        num = sin_t * \
              ((beta_bd * chi_ac - beta_ac * chi_bd) * sin_s + \
               (alpha_ac * chi_bd - alpha_bd * chi_ac) * cos_s)
        den = (alpha_bd * chi_ac - alpha_ac * chi_bd) * sin_s + \
              (beta_bd * chi_ac - beta_ac * chi_bd) * cos_s

        # tan_p = num/den
        pan_angle = atan2(num, den)
        
        print("pan angle:", degrees(pan_angle))

        # helper variables for angular functions of the pan angle
        sin_p = sin(pan_angle)
        cos_p = cos(pan_angle)

        # calculation of focal length f
        num = chi_bd * cos_p * cos_t
        den = beta_bd * sin_p * cos_s - beta_bd * cos_p * sin_t * sin_s + \
              alpha_bd * sin_p * sin_s + alpha_bd * cos_p * sin_t * cos_s
        
        focal_length = num/den

        print("focal length:", focal_length)

        # calculation of camera distance
        num = width * (focal_length * sin_t + a[0] * cos_t * sin_s + a[1] * cos_t * cos_s) * \
                      (focal_length * sin_t + c[0] * cos_t * sin_s + c[1] * cos_t * cos_s)
        
        den = -(focal_length * sin_t + a[0] * cos_t * sin_s + a[1] * cos_t * cos_s) * \
          (c[0] * cos_p * sin_s - c[0] * sin_p * sin_t * cos_s + c[1] * cos_p * cos_s + c[1] * sin_p * sin_t * sin_s) + \
          (focal_length * sin_t + c[0] * cos_t * sin_s + c[1] * cos_t * cos_s) * \
          (a[0] * cos_p * sin_s - a[0] * sin_p * sin_t * cos_s + a[1] * cos_p * cos_s + a[1] * sin_p * sin_t * sin_s)

        length_to_world_plane = num/den

        print("distance to world plane:", length_to_world_plane)
        print("height:", length_to_world_plane * sin(tilt_angle))

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


# Calculate variables
def get_abc(x_2D, y_2D):

    a = (x_2D[1]-x_2D[0], x_2D[2]-x_2D[0], x_2D[3]-x_2D[1], x_2D[3]-x_2D[2])
    b = (y_2D[1]-y_2D[0], y_2D[2]-y_2D[0], y_2D[3]-y_2D[1], y_2D[3]-y_2D[2])
    c = ((x_2D[0]*y_2D[1]-x_2D[1]*y_2D[0], x_2D[0]*y_2D[2]-x_2D[2]*y_2D[0],
          x_2D[1]*y_2D[3]-x_2D[3]*y_2D[1], x_2D[2]*y_2D[3]-x_2D[3]*y_2D[2]))
    return a, b, c

# Calculate the swing angle
def get_s(a, b, c):
    num = ((b[2]*b[3]*a[1]*c[0]) - (b[1]*b[3]*a[2]*c[0])
         + (b[0]*b[2]*a[3]*c[1]) - (b[2]*b[3]*a[0]*c[1])
         + (b[1]*b[3]*a[0]*c[2]) - (b[0]*b[1]*a[3]*c[2])
         + (b[0]*b[1]*a[2]*c[3]) - (b[0]*b[2]*a[1]*c[3]))

    den = ((a[2]*a[3]*b[1]*c[0]) - (a[1]*a[3]*b[2]*c[0])
         + (a[0]*a[2]*b[3]*c[1]) - (a[2]*a[3]*b[0]*c[1])
         + (a[1]*a[3]*b[0]*c[2]) - (a[0]*a[1]*b[3]*c[2])
         + (a[0]*a[1]*b[2]*c[3]) - (a[0]*a[2]*b[1]*c[3]))

    s = atan2(num, den)
    return s

# Calculate the camera parameters using Fung and Yung's method
def FY(x_2D, y_2D, a, b, c, s, w):
    # Calculate the tilt angle
    num = (((a[2]*c[1]-a[1]*c[2])*sin(s) + (b[2]*c[1]-b[1]*c[2])*cos(s)) *
           ((a[3]*c[0]-a[0]*c[3])*sin(s) + (b[3]*c[0]-b[0]*c[3])*cos(s)))
    den = (((a[3]*c[0]-a[0]*c[3])*cos(s) + (b[0]*c[3]-b[3]*c[0])*sin(s)) *
           ((b[2]*c[1]-b[1]*c[2])*sin(s) + (a[1]*c[2]-a[2]*c[1])*cos(s)))

    # Bodge :(
    nd = num/den
    if nd < 0:
        print("Bodge")
        nd = -nd

    t = asin(-sqrt(nd))

    # Calculate the pan angle
    num = sin(t) * ((b[2]*c[1]-b[1]*c[2])*sin(s) + (a[1]*c[2]-a[2]*c[1])*cos(s))

    den = (a[2]*c[1]-a[1]*c[2])*sin(s) + (b[2]*c[1]-b[1]*c[2])*cos(s)

    p = atan2(num, den)

    # Calculate the focal length
    num = c[2] * cos(p) * cos(t)

    den = (b[2]*sin(p)*cos(s) - b[2]*cos(p)*sin(t)*sin(s)
         + a[2]*sin(p)*sin(s) + a[2]*cos(p)*sin(t)*cos(s))

    f = num / den

    # Calculate the camera height
    num = w * (f*sin(t) + x_2D[0]*cos(t)*sin(s) + y_2D[0]*cos(t)*cos(s)) * (f*sin(t) + x_2D[2]*cos(t)*sin(s) + y_2D[2]*cos(t)*cos(s))

    den = (-(f*sin(t) + x_2D[0]*cos(t)*sin(s) + y_2D[0]*cos(t)*cos(s)) *
            (x_2D[2]*cos(p)*sin(s) - x_2D[2]*sin(p)*sin(t)*cos(s) + y_2D[2]*cos(p)*cos(s) + y_2D[2]*sin(p)*sin(t)*sin(s))
           +(f*sin(t) + x_2D[2]*cos(t)*sin(s) + y_2D[2]*cos(t)*cos(s)) *
            (x_2D[0]*cos(p)*sin(s) - x_2D[0]*sin(p)*sin(t)*cos(s) + y_2D[0]*cos(p)*cos(s) + y_2D[0]*sin(p)*sin(t)*sin(s)))

    h = sin(t) * num/den

    #if f < 0:
    #    f = -f
    #    s = s + pi
    #if h < 0:
    #    h = -h
    #    p = p + pi

    return [s, t, p, f, h]
