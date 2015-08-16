# -*- coding: utf-8 -*-

import os
import bold_helper
import uparse_helper
import detail_getter
import flask, flask.views
import tempfile
import shutil
from flask import Flask, render_template, request, Response
import time
from werkzeug import secure_filename

ALLOWED_EXTENSIONS = set(['fasta', 'fa','fas','fsa'])

app = flask.Flask(__name__)
app.secret_key = 'solong'

my_dict = {}
output_dict ={}
initial_fasta = ''

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def validate(read_input, clustering_percentage):
    if flask.request.method == 'POST':
        file = flask.request.files['browse']
        if file and allowed_file(file.filename):
            flask.flash("Uploading file")
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            read_input = app.config['UPLOAD_FOLDER'] + '/' + filename
            initial_fasta = read_input
        else:
            flask.flash("INVALID INPUT FILE, EITHER NOT PROVIDED OR UNSUPPORTED EXTENSION")
            return False
    if (read_input != ' ' and os.path.exists(read_input)):

        if (clustering_percentage == '' or is_number(clustering_percentage)== False):
            clustering_percentage = 97.00
        clustering_percentage = float(clustering_percentage)
        if(isinstance(clustering_percentage, float) and 100.00 >= clustering_percentage >= 0.00):
                    print 'percent Fine'+str(clustering_percentage)
                    return clustering_percentage
    else:
        return False

def dict_to_html(output_dict,filename_suffix):#writes the first output html file
    boldresult_html = 'templates/finalresults' + filename_suffix + '.html'
    open(boldresult_html, "w").writelines(open("templates/init.html").readlines())
    boldresults = open(boldresult_html,'a')
    boldresults.write('<center><h3>PRELIMINARY TAXONOMIC INFORMATION: TOP HIT FOR EACH OTU</h3><p>Top hit = highest similarity + highest count</p></center>\n')
    boldresults.write('<center><form action"/result" method="View.post2"></h4>\n')
    boldresults.write('<h4><a href="/result" class="mynewbutton">Click to view Abundance & Detailed Taxonomic Information </a></h4>\n')
    boldresults.write('<center></form>\n')
    boldresults.write( '<table border = '+'"1" name = "boldresults" id = "boldresults" style="table-layout: fixed; width: 100%;text-overflow:ellipsis;overflow:hidden;white-space:nowrap;">\n')
    boldresults.write('<thead><th><center>otu</center></th><th>Cluster Size</th><th>Match Sequence ID</th><th>Taxonomic Identification</th><th>Similarity with Match</th><th>Match URL</th></thead>')
    for key in output_dict.keys():
        boldresults.write( '<tr>' + '<td>' + key + '</td>')
        for v in output_dict[key]:

            if v.startswith('http://'):
                boldresults.write ('<td>'+'<a href = "'+str(v)+'" onclick=window.open(this.href) target=”_blank”>Click here for full record</a></td>')
            else:
                boldresults.write ('<td>'+str(v)+'</td>')
        boldresults.write('</tr>\n')
    boldresults.write ('</table></body></html>')
    boldresults.close()
    return boldresults

class View(flask.views.MethodView):


    def get(self):

        return flask.render_template('index.html')

    @app.route('/taxonomy-info')
    def post(self):
        tempdirectory = tempfile.mkdtemp()
        app.config['UPLOAD_FOLDER'] = tempdirectory
        result = validate(flask.request.form['input_file_path'],flask.request.form['clustering_percentage'])

        if result == False:
            #TERMINATE
            flask.flash("INVALID INPUT")
            return flask.render_template('index.html')
        else:
            #START UPARSE PIPELINE
            os.system('cd '+tempdirectory)
            file = flask.request.files['browse']
            filename = secure_filename(file.filename)
            path = app.config['UPLOAD_FOLDER'] + '/' + filename
            flask.flash('SUCCESSFULLY SUBMITTED FILE')

            flask.flash('CLUSTERING PERCENTAGE ACCEPTED')
            filename_suffix = str(int(round(time.time() * 1000)))

            try:
                uparse_helper.uparse_pipeline(path,result,tempdirectory)
            except OSError:
                flask.flash("USEARCH NOT INSTALLED CORRECTLY")
                return flask.render_template('index.html')

            flask.flash('UPARSE PIPELINE SUCCESSFULLY COMPLETED')
            flask.flash('COMMUNICATING WITH BOLD...')

            #UPARSE PIPELINE COMPLETE, START BOLD CALLS FOR GENERAL INFORMATION
            output_dict = bold_helper.get_bold_results(tempdirectory)
            boldresults = dict_to_html(output_dict,filename_suffix)
            specimen_data = detail_getter.specimen_data_retrieval(output_dict)
            specimen_data_parsed = detail_getter.specimen_data_parser(specimen_data,output_dict,filename_suffix)
            final = detail_getter.write_to_file(specimen_data_parsed,filename_suffix)
            open("templates/finaltable.html", "w").writelines(open("templates/init.html").readlines())
            open("templates/finaltable.html", "a").writelines(open("templates/outfile" + filename_suffix + ".html").readlines())
            return flask.render_template('finalresults' + filename_suffix + '.html')
        return self.get()

    @app.route('/result')
    def post2():
        return flask.render_template('finaltable.html')




app.add_url_rule('/', view_func=View.as_view('main'), methods = ['GET','POST','POST2'])
app.debug = True
app.run(host= '0.0.0.0',threaded = True)
