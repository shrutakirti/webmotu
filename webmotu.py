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
import shutil

app = flask.Flask(__name__)
app.secret_key = 'solong'


config = ConfigParser.ConfigParser()
readconfig = config.read('/home/kirti/webmotu_config.cfg')#change to location of config file
#app.config.from_envvar('readconfig', silent=True)

bold_url = config.get('Section', 'bold_url')        #edit these bits 
usrch = config.get('Section2','usearch_location')   #in config file
kirti_desktop = tempfile.mkdtemp() 
print kirti_desktop


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def validate(read_input, clustering_percentage):
    if (read_input != ' ' and os.path.exists(read_input) and read_input.endswith('.fasta')):
        
        if (clustering_percentage == '' or is_number(clustering_percentage)== False):
            clustering_percentage = 97.00
        clustering_percentage = float(clustering_percentage)
        if(isinstance(clustering_percentage, float) and 100.00 >= clustering_percentage >= 0.00):
                    print 'percent Fine'+str(clustering_percentage)
                    return clustering_percentage
    else:
        return False

def uparse_pipeline(reads,clustering_percentage):
    clustering_percentage = clustering_percentage/100
    derep = usrch + ' -derep_fulllength ' + reads +  ' -fastaout '+kirti_desktop+'derep.fasta -sizeout'
    ab_sort = usrch + ' -sortbysize '+ kirti_desktop+'derep.fasta -fastaout '+kirti_desktop+'sorted.fasta -minsize 2'
    clustering_otus = usrch + ' -cluster_otus '+kirti_desktop+'sorted.fasta -otus '+kirti_desktop+'otus.fasta -relabel OTU_ -sizeout -uparseout '+kirti_desktop+'results.fasta'
    mapping_reads = usrch + ' -usearch_global ' + reads + ' -db '+kirti_desktop+'otus.fasta -strand plus -id '+str(clustering_percentage)+' -uc '+kirti_desktop+'map.uc'
    
    flask.flash('STARTING DEREPLICATION ...')
    os.system(derep)
    flask.flash('DEREPLICATION COMPLETE')
    flask.flash('TRYING TO SORT...')
    os.system(ab_sort)
    flask.flash('SORTING COMPLETE')
    flask.flash('CLUSTERING...')
    os.system(clustering_otus)
    flask.flash('CLUSTERING COMPLETE')
    flask.flash('MAPPING READS TO OTUS...')
    os.system(mapping_reads)
    flask.flash('MAPPING COMPLETE')

        
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


#boldresults.write('<html><head><title>WEBMOTU</title></head><body>')

def dict_to_html(my_dict):
    boldresults = open('boldresults.html','w')
    boldresults.write( '<table border = '+'"1" name = "boldresults" id = "boldresults">')
    boldresults.write('<thead><th>otu</th><th>Match ID</th><th>Taxonomic Identification</th><th>similarity</th><th>url</th></thead>')
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
    return boldresults

def get_bold_results():
    
    otus = fasta_read(kirti_desktop+'otus.fasta')

    my_dict = {}
    keycount = 0
    parsed_otu_table=[]
    parsed_otu_tables=[]
    for otu in otus:
        otu_xml = call_bold_api(otu)
        parsed_otu_table = xml_parser(otu_xml)
        parsed_otu_tables.append(parsed_otu_table)

        if my_dict.has_key(otu):
            my_dict.pop(otu)
            my_dict[otu] = parsed_otu_tables
        else:
            my_dict[otu] = parsed_otu_table
       
            
    for key in my_dict.items():
        keycount = keycount+1
    return my_dict

#def stream_template(template_name, **context):
#        app.update_template_context(context)
#        t = app.jinja_env.get_template(template_name)
#        rv = t.stream(context)
#        rv.enable_buffering(5)
#        return rv
#    
#def render_large_template():
#    rows = flask.iter_all_rows()
#    return Response(View.stream_template('index.html', rows=rows))

     
class View(flask.views.MethodView):
          
    
    def get(self):
        return flask.render_template('index.html')	
    
    def post(self):
        result = validate(flask.request.form['input_file_path'],flask.request.form['clustering_percentage'])
        
        if result == False:
            flask.flash("INVALID INPUT")
        else:
            os.system('cd '+kirti_desktop)
            path = flask.request.form['input_file_path']
            flask.flash('SUCCESSFULLY SUBMITTED '+path)
            
            flask.flash('CLUSTERING PERCENTAGE ACCEPTED')
            uparse_pipeline(path,result)
            flask.flash('UPARSE PIPELINE SUCCESSFULLY COMPLETED')
            flask.flash('COMMUNICATING WITH BOLD...')
            my_dict = get_bold_results()
            boldresults = dict_to_html(my_dict)
            os.system('cat '+'templates/init.html boldresults.html > templates/finalresults.html')

            return flask.render_template('finalresults.html',boldresults = boldresults)
            
          
        return self.get()

    
        
             
app.add_url_rule('/', view_func=View.as_view('main'), methods = ['GET','POST'])
app.debug = True
app.run()
