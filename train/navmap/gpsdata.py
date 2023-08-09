""" GPSData class definition """

import csv
from datetime import time
from COTdataclasses import GPSDatum


class GPSData:
    """Data container for GPS data from specific csv format"""

    def __init__(self) -> None:
        self.data = []
        self._file_path :str = None

    def __getitem__(self, index: int) -> GPSDatum:
        return self.data[index]

    def read_csv_data(self, _file_path):
        """ Reads data from specific gps csv files and converts them to a list of tuples """

        # Return if function is called with the same argument
        if self._file_path is not None and _file_path.lower() == self._file_path.lower():
            return

        with open(_file_path, 'r', encoding='ascii') as file:

            # Discard data if a new file_path is provided
            if self.data is not None:
                del self.data
                self.data = []

            # Set file path
            self._file_path = _file_path

            # Read with csv module
            csv_reader = csv.reader(file)
            _ = next(csv_reader)  # skip the header line

            first_timestamp: int = None

            for row in csv_reader:
                try:
                    # catch all header values as strings
                    tid, lat, lon, speed, course, alt = row

                    # time id is given as a clock time in milliseconds, so 12:34 is 12340000
                    # gps coordinates seem to have been created only every second
                    # so it is converted to total amount of seconds
                    s = int(int(tid)/100)%100
                    m = int(int(tid)/10000)%100
                    h = int(int(tid)/1000000)

                    timestamp = 3600 * h + 60 * m + s

                    # remember first t
                    if first_timestamp is None:
                        first_timestamp = timestamp

                    row_data = GPSDatum(
                        time(hour=h, minute=m, second=s),
                        timestamp - first_timestamp,
                        # latitude and longitude are given in decimal geographical degrees multiplied by 100000
                        float(int(lat)) / 10**5,
                        float(int(lon)) / 10**5,
                        # speed is given in 10m/h, converted to km/h
                        float(int(speed)) / 10**2,
                        # course is not used
                        int(course),
                        # altitude is given in cm, converted to m
                        float(int(alt)) / 10**2

                    )

                    self.data.append(row_data)

                except Exception as exception:
                    print(
                        f'{exception}: Row {csv_reader.line_num} with values {row} could not be converted.'
                    )

    def list_data(self):
        """ generator for list of coordinates """
        gpsdatum: GPSDatum
        for gpsdatum in self.data:
            yield gpsdatum

    def list_of_coords_filtered(self):
        """ generator for list of coordinates with unique geographical coordinates"""
        gpsdatum: GPSDatum
        previous_lat: float = 0
        previous_lon: float = 0

        for gpsdatum in self.data:
            if previous_lat == gpsdatum.latitude and previous_lon == gpsdatum.longitude:
                continue

            previous_lat = gpsdatum.latitude
            previous_lon = gpsdatum.longitude

            yield gpsdatum

    def list_of_timestamps(self) -> list:
        """ provides list of timestamps"""
        return [gpsdatum.timestamp for gpsdatum in self.data]


    @property
    def file_path(self):
        """ getter for file path """
        return self._file_path

