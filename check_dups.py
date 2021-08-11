#!/usr/bin/python

def checkForDups(log_file):
	lines = log_file.readlines()

	titles = lines[0::11]
	artists = lines[1::11]
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
	# print(set([x for x in titles if titles.count(x) > 1]))
	# print(set([x for x in titles if titles.count(x.lower()) > 1]))


	trackArtistAndTitle = []
	for i in range(len(titles)):
		if titles.count(titles[i]) > 1:
			fullTrack = artists[i].strip() + " - " + titles[i]
			trackArtistAndTitle.append(fullTrack)

	# print(set([x for x in trackArtistAndTitle if trackArtistAndTitle.count(x) > 1]))
	# for i in range(len(dupSet)):
		# print(dupSet[i])

	dupSet = set([x for x in trackArtistAndTitle if trackArtistAndTitle.count(x) > 1])
	print(dupSet)

if __name__ == "__main__":

	metadata_log_file = open("metadata_log_file.txt", "r")
	checkForDups(metadata_log_file)
	print("Done...")