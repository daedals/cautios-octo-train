"""GPSData class definition"""

import csv
from PySide6.QtPositioning import QGeoCoordinate

class Coordinate:
    """ Custom type representing a gps coordinate with associated time id, course and speed"""

    def __init__(self,
                 _tid: int, _lat: float, _lon: float,
                 _speed: float, _course: int, _alt: float
                ) -> None:
        
        """ Data initialization """

        self.data = tuple([_tid, _lat, _lon, _speed, _course, _alt])
        self.coord = QGeoCoordinate(_lat, _lon, _alt)

    @property
    def timeid(self) -> int:
        """ returns the time id """
        return self.data[0]

    @property
    def latitude(self) -> float:
        """ returns latitude """
        return self.data[1]

    @property
    def longitude(self) -> float:
        """ return longitude """
        return self.data[2]

    @property
    def speed(self) -> int:
        """ returns the time id """
        return self.data[3]

    @property
    def course(self) -> float:
        """ returns latitude """
        return self.data[4]

    @property
    def altitude(self) -> float:
        """ return longitude """
        return self.data[5]

    def coords_as_qgeocoordinate(self) -> QGeoCoordinate:
        """ returns coords as a QGeoCoordinate """
        return self.coord


class GPSData:
    """Data container for GPS data from specific csv format"""
    data = []

    def read_csv_data(self, _file_path):
        """Reads data from specific gps csv files and converts them to a list of tuples"""

        with open(_file_path, 'r', encoding='ascii') as file:
            csv_reader = csv.reader(file)
            _header = next(csv_reader)  # skip the header line

            prev_lat = 0
            prev_lon = 0

            for row in csv_reader:
                try:
                    # catch all header values as strings
                    tid, lat, lon, speed, course, alt = row

                    # skip coordinate if the train didn't move
                    if prev_lat == lat and prev_lon == lon:
                        continue

                    # update coordinates if train did move
                    prev_lat, prev_lon = lat, lon

                    # convert each string to a useful value
                    row_data = Coordinate(
                        int(int(tid)/100), # Time id
                        float(int(lat)) / 10**5, # latidute 
                        float(int(lon)) / 10**5, # longitude
                        float(int(speed)) / 10**2, # speed
                        int(course), 
                        float(int(alt)) / 10**2 # altitude
                    )

                    self.data.append(row_data)

                except Exception as exception:
                    print(
                        f'{exception}: Row {csv_reader.line_num} with values {row} could not be converted.'
                    )

            print(self.data.__len__())

            return _header, self.data

    def to_dict(self):
        """ Returns data as a dict """
        pass

    def list_of_coords(self):
        """ generator for list of coordinates """
        for coordinate in self.data:
            yield coordinate



if __name__ == "__main__":
    gpsdata = GPSData()
    file_path = './data/gps_spring.csv'
    header, data = gpsdata.read_csv_data(file_path)
    print(file_path, header, data[:5], '\n')
    file_path = './data/gps_summer.csv'
    header, data = gpsdata.read_csv_data(file_path)
    print(file_path, header, data[:5], '\n')
    file_path = './data/gps_fall.csv'
    header, data = gpsdata.read_csv_data(file_path)
    print(file_path, header, data[:5], '\n')
    file_path = './data/gps_winter.csv'
    header, data = gpsdata.read_csv_data(file_path)
    print(file_path, header, data[:5], '\n')
