import csv

csv_path = "/Users/david/python_Study/Apple_interview/sample.csv"
new_path = "/Users/david/python_Study/Apple_interview/sample11.csv"

csv_list =[]


def get_value(path):
	f = open(path,'r')
	csv_file= csv.reader(f)
	for row in csv_file:
		ss = []
		for ceil in row:
			print(ceil)
			if len(ceil)>8:
				new_ceil = ceil[:8]+'...'
				print(new_ceil)
				ss.append(new_ceil)
			else:
				ss.append(ceil)

		csv_list.append(ss)
	print(csv_list)
	f.close()
def write_csv():
	f = open(new_path,'w')
	csv_f = csv.writer(f)
	for row in csv_list:
		csv_f.writerow(row)

get_value(csv_path)
write_csv()