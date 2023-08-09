import math
import numpy as np

class CameraCalibration:
    def __init__(self, image_dimensions, image_points, real_world_dimensions):

        # a, b, c, d represent vectors
        a = image_points[0]
        b = image_points[1]
        c = image_points[2]
        d = image_points[3]

        alpha_ab, beta_ab, chi_ab = b[0] - a[0], b[1] - a[1], a[0]*b[1] - b[1]*a[1]
        alpha_ac, beta_ac, chi_ac = c[0] - a[0], c[1] - a[1], a[0]*c[1] - c[1]*a[1]
        alpha_bd, beta_bd, chi_bd = d[0] - b[0], d[1] - b[1], b[0]*d[1] - d[1]*b[1]
        alpha_cd, beta_cd, chi_cd = d[0] - c[0], d[1] - c[1], c[0]*d[1] - d[1]*c[1]
        
        nom = [
            - beta_ab * beta_ac * chi_bd * alpha_cd + beta_ac * alpha_bd * beta_ab * chi_cd,
              beta_cd * chi_ab * beta_bd * alpha_ac - beta_ab * chi_cd * beta_bd * alpha_ac,
            - beta_cd * beta_bd * chi_ac * alpha_ab - beta_ac * chi_ab * alpha_bd * beta_cd,
              beta_ab * chi_ac * beta_bd * alpha_cd + beta_cd * beta_ac * chi_bd * alpha_ab
        ]

        denom = [
            - beta_ab * chi_ac * alpha_bd * alpha_cd + beta_ac * chi_ab * alpha_bd * alpha_cd,
            - beta_ac * alpha_bd * alpha_ab * chi_cd - alpha_ac * chi_bd * beta_cd * alpha_ab,
            - alpha_cd * chi_ab * beta_bd * alpha_ac + beta_ab * alpha_ac * chi_bd * alpha_cd,
              alpha_ab * chi_cd * beta_bd * alpha_ac + alpha_bd * chi_ac * beta_cd * alpha_ab
        ]


# if __name__ == "__main__":
#     # Example usage
#     image_dimensions = (1920, 1080)  # Example image dimensions
#     image_points = [(0, 0), (300, 0), (300, 300), (0, 300)]  # Example image points
#     real_world_dimensions = (10, 10)  # Example real world dimensions

#     calibration = CameraCalibration(image_dimensions, image_points, real_world_dimensions)
#     focal_length = calibration.calculate_focal_length()
#     field_of_view = calibration.calculate_field_of_view()

#     print("Calculated Focal Length:", focal_length)
#     print("Calculated Field of View:", field_of_view, "degrees")
