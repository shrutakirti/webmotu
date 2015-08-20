#This script hits the
#Public Record Barcode Database (808,526 Sequences/80,719 Species/18,248 Interim Species)
#The said database contains
#All published COI records from BOLD and GenBank with a minimum sequence length of 500bp.
#This library is a collection of records from the published projects section of BOLD.


import ConfigParser
import flask
from itertools import groupby
import urllib
import xml.etree.ElementTree as ET


config = ConfigParser.ConfigParser()
readconfig = config.read('webmotu_bold_config.cfg')#change to location of config file

bold_url = config.get('Section', 'bold_url')
#get data, parse data, write to file
def get_bold_results(kirti_desktop):
    otus = fasta_read(kirti_desktop+'/otus.fasta')
    headers = header_read(kirti_desktop+'/otus.fasta')
    my_dict = {}
    output_dict = {}
    parsed_otu_table=[]
    parsed_otu_tables=[]
    similarity_list = []
    abundance_list = []
    curr_index = 0;
    for otu in otus:
        full_size_string = (headers[curr_index].split(';'))[1]
        size = str((full_size_string.split('='))[1])
        size_array = [size]
        curr_index += 1
        otu_xml = call_bold_api(otu)#first call to BOLD
        parsed_otu_table = xml_parser(otu_xml)

        #if otu not in output_dict.keys():
        if not parsed_otu_table:
            output_dict[otu] = size_array + ['No hit','--','--','--']
        else:
            for element in parsed_otu_table:
                similarity_list.append(float(element[2]))
                abundance_list.append(parsed_otu_table.count(element[1]))
            max_similarity = max(similarity_list)
            max_abundance = max(abundance_list)
            for element in parsed_otu_table:
                if (float(element[2]) == max_similarity):
                    if (parsed_otu_table.count(element[1]) == max_abundance):
                        output_dict[otu] = size_array + element
        parsed_otu_tables.append(parsed_otu_table)
    return output_dict
#parse data
def xml_parser(otu_xml):
    try:
        tree = ET.parse(otu_xml)
    except(ElementTree.ParseError):
        flask.flash('BOLD API down.')

    root = tree.getroot()
    table = []
    count = 0

    for match in root.findall('match'):

        ID = match.find('ID').text
        taxonomic_id=match.find('taxonomicidentification').text
        similarity=match.find('similarity').text
        url = match.find('specimen').find('url').text
        table = table + [[ID,taxonomic_id,similarity,url]]
        count = count + 1

    return table
#get data
def call_bold_api(otu):
    print otu
    url_values = otu
    full_url = bold_url+url_values
    data = urllib.urlopen(full_url)

    return data

def fasta_read(otus_file):
    otus = open(otus_file)
    fasta_iter = (x[1] for x in groupby(otus, lambda line: line[0] == ">"))
    otu_list = list()
    for header in fasta_iter:
        #join all sequence lines
        seq = "".join(s.strip() for s in fasta_iter.next())
        otu_list.append(seq)
    return otu_list

def header_read(otus_file):
    otus = open(otus_file)
    fasta_iter = (x[1] for x in groupby(otus, lambda line: line[0] == ">"))
    header_list = list()
    index = 0
    for header in fasta_iter:
        #drop '>'
        header = header.next()[1:].strip()
        #join all sequence lines
        if (index % 2 == 0) :
            header_list.append(header)
        index += 1
    return header_list
