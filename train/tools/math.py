from math import sin, asin, cos, atan2, degrees, sqrt, radians

from COTdataclasses import KeyFrame, IntrinsicCameraParameters, ExtrinsicCameraParameters

def determine_camera_parameters(keyframe: KeyFrame, width: int) -> (IntrinsicCameraParameters, ExtrinsicCameraParameters):

    a, b, c, d = assign_points_to_assumed_order(keyframe.image_point.to_list())

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

    # print("swing angle:", degrees(swing_angle))

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

    # print("tilt angle:", degrees(tilt_angle))

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
    
    # print("pan angle:", degrees(pan_angle))

    # helper variables for angular functions of the pan angle
    sin_p = sin(pan_angle)
    cos_p = cos(pan_angle)

    # calculation of focal length f
    num = chi_bd * cos_p * cos_t
    den = beta_bd * sin_p * cos_s - beta_bd * cos_p * sin_t * sin_s + \
            alpha_bd * sin_p * sin_s + alpha_bd * cos_p * sin_t * cos_s
    
    focal_length = num/den

    # print("focal length:", focal_length)

    # calculation of principal length
    num = width * (focal_length * sin_t + a[0] * cos_t * sin_s + a[1] * cos_t * cos_s) * \
                    (focal_length * sin_t + c[0] * cos_t * sin_s + c[1] * cos_t * cos_s)
    
    den = -(focal_length * sin_t + a[0] * cos_t * sin_s + a[1] * cos_t * cos_s) * \
        (c[0] * cos_p * sin_s - c[0] * sin_p * sin_t * cos_s + c[1] * cos_p * cos_s + c[1] * sin_p * sin_t * sin_s) + \
        (focal_length * sin_t + c[0] * cos_t * sin_s + c[1] * cos_t * cos_s) * \
        (a[0] * cos_p * sin_s - a[0] * sin_p * sin_t * cos_s + a[1] * cos_p * cos_s + a[1] * sin_p * sin_t * sin_s)

    principal_length = num/den

    z_offset = principal_length * sin(tilt_angle)

    planar_distance = principal_length * cos(tilt_angle)

    x_offset = planar_distance * sin(pan_angle)
    y_offset = planar_distance * cos(pan_angle)

    intrinsics = IntrinsicCameraParameters(
        abs(focal_length),
        principal_length
    )

    extrinsics = ExtrinsicCameraParameters(
        degrees(swing_angle),
        degrees(tilt_angle),
        degrees(pan_angle),
        x_offset,
        y_offset,
        z_offset
    )

    return (intrinsics, extrinsics)

def assign_points_to_assumed_order(_image_points):
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

    return a, b, c, d

def distance_between_geo_coordinates(lat_1: float, lon_1: float, lat_2: float, lon_2: float) -> float:
    """ calculates the distance between 2 gps coordinates

    formula copied from:
    https://stackoverflow.com/questions/365826/calculate-distance-between-2-gps-coordinates
    """

    # earth radius in meter
    earth_radius = 6371000

    # difference between both latitudes and longitudes in radians
    d_lat = radians(lat_2-lat_1)
    d_lon = radians(lon_2-lon_1)

    # both latitudes in radians
    lat_1 = radians(lat_1)
    lat_2 = radians(lat_2)

    a = sin(d_lat/2) * sin(d_lat/2) + sin(d_lon/2) * sin(d_lon/2) * cos(lat_1) * cos(lat_2)
    c = 2 * atan2(sqrt(a), sqrt(1-a))

    return earth_radius * c
