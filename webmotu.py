# -*- coding: utf-8 -*-
"""
Created on Tue Jun  9 10:37:10 2015

@author: kirti
"""
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('127.0.1.1', 5000))

import os
import flask, flask.views
import timeit
import subprocess
import urllib
import urllib2
from itertools import groupby
import xml.etree.ElementTree as ET
import tabulate
import time




app = flask.Flask(__name__)
app.secret_key = 'solong'
usrch = '/home/kirti/Desktop/usearch8'

def validate(read_input):
	if (read_input != ' ' and os.path.exists(read_input) and read_input.endswith('.fasta')):
         return True
	
	else:
         return False
#         
#def user_input():
#    read_input = raw_input('enter path of file in fasta format containing reads:')
#    validated = validate(read_input)
#    if validated==True:
#        print 'input submitted successfully'
#        return read_input
#    else:
#        print 'please check input'
#        user_input()

def uparse_pipeline(reads):
    
    derep = usrch + ' -derep_fulllength ' + reads +  ' -fastaout derep.fasta -sizeout'
    ab_sort = usrch + ' -sortbysize derep.fasta -fastaout sorted.fasta -minsize 2'
    clustering_otus = usrch + ' -cluster_otus sorted.fasta -otus otus.fasta -relabel OTU_ -sizeout -uparseout results.fasta'
    mapping_reads = usrch + ' -usearch_global ' + reads + ' -db otus.fasta -strand plus -id 0.97 -uc map.uc'
    
    #os.system(derep + ' | '+ ab_sort + ' | '+ clustering_otus + ' | '+ mapping_reads)
    os.system(derep)
    os.system(ab_sort)
    os.system(clustering_otus)
    os.system(mapping_reads)
#    flask.flash(subprocess.check_output(derep,shell=True))
#    
    flask.flash('DEREPLICATION IN PROGRESS...' + '\n\nDEREPLICATION COMPLETE'+'\n\nCREATED DEREP.FASTA')
    
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

def get_bold_results():
    otus = fasta_read('/home/kirti/otus.fasta')
    list_of_tables = list()
    logfile = open('log.txt','w')
    for otu in otus:
        otu_xml = call_bold_api(otu)
        logfile.write(otu.xml)
        parsed_otu_table = xml_parser(otu_xml)
        list_of_tables.append(parsed_otu_table)
        
    print list_of_tables

def call_bold_api(otu):
    print otu
    url_values = otu
    url = 'http://boldsystems.org/index.php/Ids_xml?db=COX1_SPECIES_PUBLIC&sequence='
    full_url = url+url_values
    data = urllib2.urlopen(full_url)
    return data

def xml_parser(otu_xml):
    tree = ET.parse(otu_xml)
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
        newcount = count
        if (count%10==0):
            print "processed "+ str(count) +" sequences"
        count = newcount   
    return table
    




class View(flask.views.MethodView):
      
    
    def get(self):
        return flask.render_template('index.html')	
    def post(self):
        result = validate(flask.request.form['input_file_path'])
        if result == True:
            printed = flask.request.form['input_file_path']
            flask.flash('SUCCESSFULLY SUBMITTED '+printed)
            uparse_pipeline(printed)
            flask.flash('uparse done')
            flask.flash(get_bold_results())
        else:
            printed = 'Invalid input. Please try again.'
        
        return self.get()
        
        
             
app.add_url_rule('/', view_func=View.as_view('main'), methods = ['GET','POST'])
app.debug = True
app.run()
