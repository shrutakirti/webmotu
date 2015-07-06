import fileinput
def file_merge(kirti_desktop):
	output_file = 'templates/finalresults.html'
        bold_op = kirti_desktop + '/boldresults.html'
	with open(output_file,'w') as fout:
		for line in fileinput.input(files=('templates/init.html',bold_op)):
			fout.write(line)
