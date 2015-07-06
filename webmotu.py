# -*- coding: utf-8 -*-

import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('127.0.1.1', 5000))

import os
import bold_helper
import uparse_helper
import flask, flask.views
from flask import Response, request, stream_with_context
import urllib
import tempfile
import shutil

app = flask.Flask(__name__)
app.secret_key = 'solong'

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

def dict_to_html(my_dict):
    boldresults = open('boldresults.html','w')
    boldresults.write( '<table border = '+'"1" name = "boldresults" id = "boldresults">')
    boldresults.write('<thead><th>otu</th><th>Match Sequence ID</th><th>Taxonomic Identification</th><th>Similarity with Match</th><th>url</th></thead>')
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
    boldresults.write ('</table><form><input type="submit" value="Detailed Taxonomic Information" onClick="this.form.submit();this.disabled=true" /></form></body></html>')
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
            #START UPARSE PIPELINE(add try-except?)
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
            my_dict = bold_helper.get_bold_results(kirti_desktop)
            boldresults = dict_to_html(my_dict)

            os.system('cat '+'templates/init.html boldresults.html > templates/finalresults.html')
            return flask.render_template('finalresults.html',boldresults = boldresults)
            
            #BOLD CALLS FOR SPECIFIC TAXONOMIC INFORMATION
#            specimen_data = specimen_data_retrieval(parsed_otu_table)
#            info = specimen_data_parser(specimen_data)
    

        return self.get()
        
             
app.add_url_rule('/', view_func=View.as_view('main'), methods = ['GET','POST'])
app.debug = True
app.run()
