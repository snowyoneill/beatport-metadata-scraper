#!/usr/bin/python

def checkForDups(log_file):
	lines = log_file.readlines()

	titles = lines[0::11]
	# print(titles)
	# for line in lines:
	# 	title_to_check = line
	# 	print(title_to_check)
	# 	break

	# for t in titles:
	# 	print t

	if len(titles) != len(list(set(titles))):
		print("Dups exist")

	# print(list(set(titles) - set(no_dups)))
	print(set([x for x in titles if titles.count(x) > 1]))
	# print(set([x for x in titles if titles.count(x.lower()) > 1]))

if __name__ == "__main__":

	metadata_log_file = open("metadata_log_file.txt", "r")
	checkForDups(metadata_log_file)
	print("Done...")