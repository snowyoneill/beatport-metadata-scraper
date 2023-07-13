#!/usr/bin/python

from collections import Counter

def checkForDups(log_file):
	lines = log_file.readlines()

	## Capture titles and artists
	titles = lines[0::11]
	artists = lines[1::11]
	dividers = lines[10::11]

	# print(len(titles), len(artists), len(dividers))

	## If you dont see '#-----#\n' then the file is corrupted 
	# print(dividers)
	dividersCount = Counter(dividers)
	print(dividersCount)
	if len(titles) != dividersCount['#-----#\n']:
		print("CORRUPT")
		return
	
	## Output artist and title together
	# for t, a in zip(titles, artists):
	# 	print a.rstrip(), "-", t.rstrip()

	set_of_titles = list(set(titles))

	## Check lens of titles vs set of titles
	if len(titles) != len(set_of_titles):
		# print(list(set(titles) - set(no_dups)))
		# print(set([x for x in titles if titles.count(x.lower()) > 1]))
		total_non_unique = len(set([x for x in titles if titles.count(x) > 1]))

		print("Dup titles exist: " + str(len(titles)) + " vs " + str(len(set_of_titles)) + " -> #Non unique titles: " + str(total_non_unique))
		print

		# temp = list(titles)
		# for x in set_of_titles:
		# 	if x in titles:
		# 		temp.remove(x)
		# print(len(temp))
		# print(temp)

	## Print out list of duplicate Titles with their Artists
	trackArtistAndTitle = []
	for i in range(len(titles)):
		if titles.count(titles[i]) > 1:
			# fullTrack = artists[i].strip() + " - " + titles[i]
			# fullTrackR = fullTrack[::-1]
			fullTrack = titles[i].rstrip() + " - " + artists[i].rstrip()
			trackArtistAndTitle.append(fullTrack)

	## Sort for easier grouping
	print("Dup titles total: ", len(trackArtistAndTitle))
	for i in sorted(trackArtistAndTitle):
		print(i.rstrip())

	## Check if i have downloaded the metadata more than once
	dupSet = set([x for x in trackArtistAndTitle if trackArtistAndTitle.count(x) > 1])
	if dupSet:
		print
		print("---------------------")
		print("DUP METADATA!!!")
		# print("".join(dupSet))
		for x in dupSet:
			print(x)

if __name__ == "__main__":

	metadata_log_file = open("metadata_log_file.txt", "r")
	checkForDups(metadata_log_file)
	print("Done...")