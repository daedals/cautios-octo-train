"""GPSData class definition"""
import csv

class GPSData:
    """Data container for GPS data from specific csv format"""
    data = []
    
    def read_csv_data(self, _file_path):
        """Reads data from specific gps csv files and converts them to a list of tuples"""

        with open(_file_path, 'r', encoding=str) as file:
            csv_reader = csv.reader(file)
            _header = next(csv_reader)  # skip the header line

            for row in csv_reader:
                try:
                    # catch all header values as strings
                    tid, lat, lon, speed, course, alt = row

                    # convert each string to a useful value
                    row_data = tuple([
                        int(tid), # Time id
                        float(int(lat)) / 10**5, # latidute 
                        float(int(lon)) / 10**5, # longitude
                        float(int(speed)) / 10**2, # speed
                        int(course), 
                        float(int(alt)) / 10**2]) # altitude

                    self.data.append(row_data)
                except Exception as exception:
                    print(f'{exception}: Row {csv_reader.line_num} with values {row} could not be converted.')


            return header, self.data

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
