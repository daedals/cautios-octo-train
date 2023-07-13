import csv


def read_csv_data(file_path):
	data = []

	with open(file_path, 'r') as file:
		csv_reader = csv.reader(file)
		header = next(csv_reader)  # skip the header line

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
				
				data.append(row_data)
			except:
				print(f'Row {csv_reader.line_num} with values {row} could not be converted.')


	return header, data

if __name__ == "__main__":
    path = './data/gps_spring.csv'
    header, data = read_csv_data(path)
    print(path, header, data[:5], '\n')
    path = './data/gps_summer.csv'
    header, data = read_csv_data(path)
    print(path, header, data[:5], '\n')
    path = './data/gps_fall.csv'
    header, data = read_csv_data(path)
    print(path, header, data[:5], '\n')
    path = './data/gps_winter.csv'
    header, data = read_csv_data(path)
    print(path, header, data[:5], '\n')