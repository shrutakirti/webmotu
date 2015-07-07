# -*- coding: utf-8 -*-

import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('127.0.1.1', 5000))

import os
import bold_helper
import uparse_helper
#import untitled7
import file_merge
import flask, flask.views
from flask import Response, request, stream_with_context
import urllib
import tempfile
import shutil

kirti_desktop = tempfile.mkdtemp() 
print kirti_desktop

app = flask.Flask(__name__)
app.secret_key = 'solong'


my_dict = {}
output_dict ={}

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

def dict_to_html(output_dict):
    boldresult_html = kirti_desktop +'/boldresults.html'
    boldresults = open(boldresult_html,'w')
    boldresults.write( '<table border = '+'"1" name = "boldresults" id = "boldresults">')
    boldresults.write('<thead><th><center>otu</center></th><th>Match Sequence ID</th><th>Taxonomic Identification</th><th>Similarity with Match</th><th>Match URL</th></thead>')
    for key in output_dict.keys():
        
        boldresults.write( '<tr>' + '<td>' + key + '</td>')
        for v in output_dict[key]:
                   
            if v.startswith('http://'):
                boldresults.write ('<td>'+'<a href = "'+str(v)+'" onclick=window.open(this.href) target=”_blank”>Click here for full record</a></td>')
            else:
                boldresults.write ('<td>'+str(v)+'</td>')
        boldresults.write('</tr>')
    boldresults.write ('</table></body></html>')
    return boldresults


class View(flask.views.MethodView):
          
            
    def get(self):
        
        return flask.render_template('index.html')	
    
    def post(self):
        
        result = validate(flask.request.form['input_file_path'],flask.request.form['clustering_percentage'])
        
        if result == False:
            #TERMINATE
            flask.flash("INVALID INPUT")
            return flask.render_template('index.html')
        else:
            #START UPARSE PIPELINE
            os.system('cd '+kirti_desktop)
            path = flask.request.form['input_file_path']
            flask.flash('SUCCESSFULLY SUBMITTED '+path)
            
            flask.flash('CLUSTERING PERCENTAGE ACCEPTED')
            try:
                uparse_helper.uparse_pipeline(path,result,kirti_desktop)
            except OSError:
                flask.flash("USEARCH NOT INSTALLED CORRECTLY")
                return flask.render_template('index.html')                
            flask.flash('UPARSE PIPELINE SUCCESSFULLY COMPLETED')
            flask.flash('COMMUNICATING WITH BOLD...')
            
            #UPARSE PIPELINE COMPLETE, START BOLD CALLS FOR GENERAL INFORMATION 
            output_dict = bold_helper.get_bold_results(kirti_desktop)
            boldresults = dict_to_html(output_dict[0])
            file_merge.file_merge(kirti_desktop)

            
            return flask.render_template('finalresults.html',boldresults = boldresults)
        return self.get()

    def post2(self):
        #BOLD CALLS FOR SPECIFIC TAXONOMIC INFORMATION
        my_dict = output_dict[1]
        #specimen_data = untitled7.specimen_data_retrieval(my_dict)
          
        #info = untitled7.specimen_data_parser(specimen_data)
        return flask.render_template('index.html')
             
app.add_url_rule('/', view_func=View.as_view('main'), methods = ['GET','POST','POST2'])
app.debug = True
app.run()
