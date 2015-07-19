import fileinput
def file_merge(output_file,join_file):

        with open(output_file,'w') as fout:
                for line in fileinput.input(files=('templates/init.html',join_file)):
                        fout.write(line)
