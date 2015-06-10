# -*- coding: utf-8 -*-
"""
Created on Tue Jun  9 10:37:10 2015

@author: kirti
"""
import os
import flask, flask.views
import timeit
import sys
app = flask.Flask(__name__)
app.secret_key = 'solong'
usrch = '/home/kirti/Desktop/usearch8'

def validate(read_input):
	if (read_input != ' ' and os.path.exists(read_input) and read_input.endswith('.fasta')):
         return True
	
	else:
         return False
         
def user_input():
    read_input = raw_input('enter path of file in fasta format containing reads:')
    validated = validate(read_input)
    if validated==True:
        print 'input submitted successfully'
        return read_input
    else:
        print 'please check input'
        user_input()

def uparse_pipeline(reads):
    
    derep = usrch + ' -derep_fulllength ' + reads +  ' -fastaout derep.fasta -sizeout'
    ab_sort = usrch + ' -sortbysize derep.fasta -fastaout sorted.fasta -minsize 2'
    clustering_otus = usrch + ' -cluster_otus sorted.fasta -otus otus.fasta -relabel OTU_ -sizeout -uparseout results.fasta'
    mapping_reads = usrch + ' -usearch_global ' + reads + ' -db otus.fasta -strand plus -id 0.97 -uc map.uc'
    
    os.system(derep + ' | '+ ab_sort + ' | '+ clustering_otus + ' | '+ mapping_reads + ' >log.txt')
     
    
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
        else:
            printed = 'Invalid input. Please try again.'
        
        return self.get()
        
        
             
app.add_url_rule('/', view_func=View.as_view('main'), methods = ['GET','POST'])
app.debug = True
app.run()
