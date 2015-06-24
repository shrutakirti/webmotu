# -*- coding: utf-8 -*-

import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('127.0.1.1', 5000))

import os
import flask, flask.views
from flask import Response, request, stream_with_context
import urllib
import urllib2
from itertools import groupby
import xml.etree.ElementTree as ET
import ConfigParser
import tempfile

app = flask.Flask(__name__)
app.secret_key = 'solong'


config = ConfigParser.ConfigParser()
readconfig = config.read('/home/kirti/webmotu_config.cfg')#change to location of config file
#app.config.from_envvar('readconfig', silent=True)

bold_url = config.get('Section', 'bold_url')        #edit these bits 
usrch = config.get('Section2','usearch_location')   #in config file
kirti_desktop = config.get('Section2','my_desktop') 


def validate(read_input):
	if (read_input != ' ' and os.path.exists(read_input) and read_input.endswith('.fasta')):
         return True
	else:
         return False

def uparse_pipeline(reads):
    
    derep = usrch + ' -derep_fulllength ' + reads +  ' -fastaout '+kirti_desktop+'derep.fasta -sizeout'
    ab_sort = usrch + ' -sortbysize '+ kirti_desktop+'derep.fasta -fastaout '+kirti_desktop+'sorted.fasta -minsize 2'
    clustering_otus = usrch + ' -cluster_otus '+kirti_desktop+'sorted.fasta -otus '+kirti_desktop+'otus.fasta -relabel OTU_ -sizeout -uparseout '+kirti_desktop+'results.fasta'
    mapping_reads = usrch + ' -usearch_global ' + reads + ' -db '+kirti_desktop+'otus.fasta -strand plus -id 0.97 -uc '+kirti_desktop+'map.uc'
    
    #os.system(derep + ' | '+ ab_sort + ' | '+ clustering_otus + ' | '+ mapping_reads)
    
    os.system(derep)
    flask.flash('DEREPLICATION IN PROGRESS...' + '\n\nDEREPLICATION COMPLETE'+'\n\nCREATED DEREP.FASTA')
    os.system(ab_sort)
    flask.flash('SORTING...' + '\n\nSORTING COMPLETE'+'\n\nCREATED SORTED.FASTA')
    os.system(clustering_otus)
    flask.flash('CLUSTERING...' + '\n\nFINDING OTUS...'+'\n\nCREATED OTUS.FASTA' + '\n\nCREATED RESULTS.FASTA')
    os.system(mapping_reads)
    flask.flash('MAPPING READS TO OTUS...' +'\n\nCREATED MAP.UC')

        
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


def call_bold_api(otu):
    print otu
    url_values = otu
    full_url = bold_url+url_values
    data = urllib.urlopen(full_url)
    
    return data

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
       
        if (count%10==0):
            print "processed "+ str(count) +" sequences"
           
    return table
    
boldresults = open('templates/boldresults.html','w')
def dict_to_html(my_dict):
    boldresults.write( '<html><head><title>WEBMOTU</title></head><body><table border = '+'"1" id = "boldresults">')
    boldresults.write('<thead><th>otu</th><th>ID</th><th>Taxonomic Identification</th><th>similarity</th><th>url</th></thead>')
    for key in my_dict.keys():
        for value in my_dict[key]:
            
            boldresults.write( '<tr>' + '<td>' + key + '</td>')
            if (value==''):
                boldresults.write('<td>'+'no match found'+'</td>'+'</tr>')
            else:
                for v in value:
                    if v.startswith('http://'):
                        boldresults.write ('<td>'+'<a href = "'+str(v)+'" onclick=window.open(this.href) target=”_blank”>Click here for full record</a></td>')
                    else:
                        boldresults.write ('<td>'+str(v)+'</td>')
                boldresults.write('</tr>')
    boldresults.write ('</table></body></html>')
    print boldresults
    return boldresults

def get_bold_results():
    otus = fasta_read(kirti_desktop+'otus.fasta')
#    list_of_tables = list()
    my_dict = {}
    keycount = 0
    parsed_otu_table=[]
    parsed_otu_tables=[]
    for otu in otus:
        otu_xml = call_bold_api(otu)
        parsed_otu_table = xml_parser(otu_xml)
        parsed_otu_tables.append(parsed_otu_table)
#        parsed_otu_table.append(otu)
#        list_of_tables.append(parsed_otu_table)
        if my_dict.has_key(otu):
            my_dict.pop(otu)
            my_dict[otu] = parsed_otu_tables
        else:
            my_dict[otu] = parsed_otu_table
       
            
    for key in my_dict.items():
        keycount = keycount+1
    return my_dict


     
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
            my_dict = get_bold_results()
            boldresults = dict_to_html(my_dict)
           
#            for row in zip([key] + value for key, value in sorted(my_dict.items())):
#                flask.flash(row)
            return flask.render_template('boldresults.html',boldresults = boldresults)
            
        else:
            flask.flash('Invalid input. Please try again.')
        
        return self.get()

#    def stream_template(template_name, **context):
#        app.update_template_context(context)
#        t = app.jinja_env.get_template(template_name)
#        rv = t.stream(context)
#        rv.enable_buffering(5)
#        return rv
#    
#    def render_large_template():
#        rows = flask.iter_all_rows()
#        return Response(View.stream_template('index.html', rows=rows))
        
             
app.add_url_rule('/', view_func=View.as_view('main'), methods = ['GET','POST'])
app.debug = True
app.run()
