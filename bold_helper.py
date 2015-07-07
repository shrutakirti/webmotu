# -*- coding: utf-8 -*-
"""
Created on Sat Jul  4 15:35:24 2015

@author: kirti
"""

import ConfigParser
import flask
from itertools import groupby
import urllib
import xml.etree.ElementTree as ET


config = ConfigParser.ConfigParser()
readconfig = config.read('webmotu_bold_config.cfg')#change to location of config file
#app.config.from_envvar('readconfig', silent=True)

bold_url = config.get('Section', 'bold_url')
bold_species_url = config.get('Section', 'bold_species_url')        #edit these bits 

def get_bold_results(kirti_desktop):
    
    otus = fasta_read(kirti_desktop+'otus.fasta')

    my_dict = {}
    
    parsed_otu_table=[]
    parsed_otu_tables=[]
    
    for otu in otus:
        otu_xml = call_bold_api(otu)#first call to BOLD
        parsed_otu_table = xml_parser(otu_xml)
        parsed_otu_tables.append(parsed_otu_table)
#        specimen_data = specimen_data_retrieval(parsed_otu_table)#second call to BOLD
#        info = specimen_data_parser(specimen_data)

        if my_dict.has_key(otu):
            my_dict.pop(otu)
            my_dict[otu] = parsed_otu_tables
        else:
            my_dict[otu] = parsed_otu_table

    return my_dict
    
def xml_parser(otu_xml):
    try:
        tree = ET.parse(otu_xml)
    except(tree.ElementTree.ParseError):
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
       
    print "processed "+ str(count) +" matches"
           
    return table
    
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
        #drop '>'
        header = header.next()[1:].strip()
        #join all sequence lines
        seq = "".join(s.strip() for s in fasta_iter.next())
        otu_list.append(seq)
    return otu_list
