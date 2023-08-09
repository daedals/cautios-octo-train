import math

class CameraCalibration:
    def __init__(self, image_dimensions, image_points, real_world_dimensions):
        self.image_dimensions = image_dimensions
        self.image_points = image_points
        self.real_world_dimensions = real_world_dimensions

    def calculate_focal_length(self):
        image_width, image_height = self.image_dimensions
        real_width, real_height = self.real_world_dimensions
        square_width = math.sqrt(real_width * real_height)
        
        # Calculate the focal length based on the image dimensions and real world dimensions
        focal_length_x = (self.image_points[1][0] - self.image_points[0][0]) * square_width / image_width
        focal_length_y = (self.image_points[2][1] - self.image_points[1][1]) * square_width / image_height
        
        focal_length = (focal_length_x + focal_length_y) / 2
        return focal_length

    def calculate_field_of_view(self):
        # Calculate the field of view based on the calculated focal length
        focal_length = self.calculate_focal_length()
        sensor_width = self.real_world_dimensions[0]
        field_of_view = 2 * math.degrees(math.atan(sensor_width / (2 * focal_length)))
        return field_of_view


if __name__ == "__main__":
    # Example usage
    image_dimensions = (1920, 1080)  # Example image dimensions
    image_points = [(0, 0), (300, 0), (300, 300), (0, 300)]  # Example image points
    real_world_dimensions = (10, 10)  # Example real world dimensions

    calibration = CameraCalibration(image_dimensions, image_points, real_world_dimensions)
    focal_length = calibration.calculate_focal_length()
    field_of_view = calibration.calculate_field_of_view()

    print("Calculated Focal Length:", focal_length)
    print("Calculated Field of View:", field_of_view, "degrees")
