# -*- coding: utf-8 -*-
"""
Created on Sat Jul  4 16:16:13 2015

@author: kirti
"""

import ConfigParser
import flask
import os
import subprocess

config = ConfigParser.ConfigParser()
readconfig = config.read('webmotu_usearch_config.cfg')#change to location of config file

usrch = config.get('Section','usearch_location')   #in config file

def uparse_pipeline(reads,clustering_percentage,kirti_desktop):
    clustering_percentage = clustering_percentage/100
    if "not found" in subprocess.check_output(usrch):
        raise OSError("usearch8 executable is not present in the path specified in the config, please double-check")
    derep = usrch + ' -derep_fulllength ' + reads +  ' -fastaout '+kirti_desktop+'/derep.fasta -sizeout'
    ab_sort = usrch + ' -sortbysize '+ kirti_desktop+'/derep.fasta -fastaout '+kirti_desktop+'/sorted.fasta -minsize 2'
    clustering_otus = usrch + ' -cluster_otus '+kirti_desktop+'/sorted.fasta -otus '+kirti_desktop+'/otus.fasta -relabel OTU_ -sizeout -uparseout '+kirti_desktop+'/results.fasta'
    mapping_reads = usrch + ' -usearch_global ' + reads + ' -db '+kirti_desktop+'/otus.fasta -strand plus -id '+str(clustering_percentage)+' -uc '+kirti_desktop+'/map.uc'

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
