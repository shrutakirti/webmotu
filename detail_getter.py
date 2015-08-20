# -*- coding: utf-8 -*-
"""
Created on Mon Jun 22 12:21:01 2015
This script accesses the Species Level Barcode Records database belonging to BOLD.
@author: kirti
"""
import urllib
import xml.etree.ElementTree as ET
import ConfigParser
from decimal import *

config = ConfigParser.ConfigParser()
readconfig = config.read('webmotu_bold_config.cfg')#location of config file
request_url = config.get('Section', 'bold_species_url')#read config
specimen_datas=[]
specimen_data_parsed=[]
specimen_dict = {}
#get data
def specimen_data_retrieval(my_dict):
    # request_url = 'http://www.boldsystems.org/index.php/API_Public/specimen?ids='
    for key in my_dict.iterkeys():

        value = my_dict[key]
        seq_id = value[1]

        if (not seq_id == 'No hit'):
            specimen_data = urllib.urlopen(request_url+str(seq_id))
            specimen_dict[key] = specimen_data
        else:
            specimen_data = 'Unknown'
            specimen_dict[key]=specimen_data

    return specimen_dict
#parse data and get abundance scores, write to output file
def specimen_data_parser(specimen_dict,output_dict,filename_suffix):
    outfile = open('templates/outfile' + filename_suffix + '.html','w')

    phylum_dict={}
    phylum_size_dict={}
    phylum_count_dict={}
    classname_dict={}
    classname_size_dict={}
    classname_count_dict={}
    order_dict={}
    order_size_dict={}
    order_count_dict={}
    genus_dict={}
    genus_size_dict={}
    genus_count_dict={}
    species_dict={}
    species_size_dict={}
    species_count_dict={}

    no_hits_size = 0
    no_hits_count = 0

    total_cluster_size = 0
    total_records = 0

    for otu in specimen_dict.iterkeys():
        specimen_data = specimen_dict[otu]
        if(otu in output_dict):
            size = int((output_dict[otu])[0])
        else:
            continue
        total_cluster_size += size
        if (not specimen_data=='Unknown'):

            tree = ET.parse(specimen_data)
            root = tree.getroot()

        #parse data from second call to BOLD: detailed taxonomic information
            for record in root.findall('record'):
                total_records+=1

                phylum = record.find('taxonomy').find('phylum').find('taxon').find('name').text
                class_name = record.find('taxonomy').find('class').find('taxon').find('name').text
                order = record.find('taxonomy').find('order').find('taxon').find('name').text
                genus = record.find('taxonomy').find('genus').find('taxon').find('name').text
                species = record.find('taxonomy').find('species').find('taxon').find('name').text

                specimen_data_parsed.append([otu,phylum,class_name,order,genus,species])

                dict_array = update_dicts(phylum, phylum_size_dict, phylum_count_dict, size)
                phylum_size_dict = dict_array[0]
                phylum_count_dict = dict_array[1]

                dict_array = update_dicts(class_name, classname_size_dict, classname_count_dict, size)
                classname_size_dict = dict_array[0]
                classname_count_dict = dict_array[1]

                dict_array = update_dicts(order, order_size_dict, order_count_dict, size)
                order_size_dict = dict_array[0]
                order_count_dict = dict_array[1]

                dict_array = update_dicts(genus, genus_size_dict, genus_count_dict, size)
                genus_size_dict = dict_array[0]
                genus_count_dict = dict_array[1]

                dict_array = update_dicts(species, species_size_dict, species_count_dict, size)
                species_size_dict  = dict_array[0]
                species_count_dict = dict_array[1]
        else:
            no_hits_count+=1
            no_hits_size+=int(size)

    getcontext().prec = 4
#abundance data calculation
    unknown_percentage = (Decimal(no_hits_count)/Decimal(total_records+no_hits_count))*100
    unknown_cluster_percentage = (Decimal(no_hits_size)/Decimal(total_cluster_size))*100

    phylum_dict = get_dict_from_data(phylum_count_dict, phylum_size_dict, total_records, no_hits_count,no_hits_size, total_cluster_size, unknown_percentage, unknown_cluster_percentage)
    classname_dict = get_dict_from_data(classname_count_dict, classname_size_dict, total_records, no_hits_count,no_hits_size, total_cluster_size, unknown_percentage, unknown_cluster_percentage)
    order_dict = get_dict_from_data(order_count_dict, order_size_dict, total_records, no_hits_count,no_hits_size, total_cluster_size, unknown_percentage, unknown_cluster_percentage)
    genus_dict = get_dict_from_data(genus_count_dict, genus_size_dict, total_records, no_hits_count, no_hits_size,total_cluster_size, unknown_percentage, unknown_cluster_percentage)
    species_dict = get_dict_from_data(species_count_dict, species_size_dict, total_records, no_hits_count, no_hits_size,total_cluster_size, unknown_percentage, unknown_cluster_percentage)

    write(phylum_dict,"Phylum",outfile)
    write(classname_dict,"Class",outfile)
    write(order_dict,"Order",outfile)
    write(genus_dict,"Genus",outfile)
    write(species_dict,"Species",outfile)

    return specimen_data_parsed

def update_dicts(key, size_dict, count_dict, size):
    if key in size_dict:
        new_size = size_dict[key]+size
        size_dict[key] = new_size
        new_count = count_dict[key] + 1
        count_dict[key] = new_count
    else:
        size_dict[key] = size
        count_dict[key] = 1
    return [size_dict, count_dict]

def get_dict_from_data(count_dict, size_dict, total_records, no_hits_count, no_hits_size,total_cluster_size, unknown_percentage, unknown_cluster_percentage):
    data_dict={}
    for data_key in count_dict.keys():
        count = count_dict[data_key]
        percentage = (Decimal(count)/Decimal(total_records + no_hits_count))*100
        cluster_percentage = (Decimal(size_dict[data_key])/Decimal(total_cluster_size))*100
        data_dict[data_key] = [percentage,count,cluster_percentage,size_dict[data_key]]
    data_dict['Unknown']=[unknown_percentage,no_hits_count,unknown_cluster_percentage,no_hits_size]
    return data_dict
#initialize output file
def init_data(filename_suffix):
    outfile = open('templates/outfile' + filename_suffix + '.html','a')
    outfile.write('<center><p><b><h4>Detailed Taxonomic Information</h4></b></p></center>')
    outfile.write('<table name = "final" id = "final"><thead><th>OTU</th><th>Phylum</th><th>Class</th><th>Order</th><th>Genus</th><th>Species</th></thead><tbody>')
    return outfile
#write to file
def write_to_file(specimen_data_parsed,filename_suffix):
    outfile = init_data(filename_suffix)
    for data in specimen_data_parsed:
        outfile.write("<tr><td>"+str(data[0])+"</td><td>"+str(data[1])+"</td><td>"+str(data[2])+"</td><td>"+str(data[3])+"</td><td>"+str(data[4])+"</td><td>"+str(data[5])+"</td></tr>")
    outfile.write("</tbody></table></body></html>")
    outfile.close()

def write(my_dict,category,outfile):
    outfile.write('<center><p><b><h4>'+category+' Abundance Information</h4></b></p></center>')
    outfile.write('<table name = "'+category+'" id = "'+category+'"><thead><th>'+category+'</th><th>% of Clusters</th><th>Number of Clusters</th><th>% of Sequences</th><th>Number of Sequences</th></thead><tbody>')
    for key in my_dict.iterkeys():
        outfile.write('<tr><td>'+key+'</td><td>'+str((my_dict[key])[0])+'</td><td>'+str((my_dict[key])[1])+'</td><td>'+str((my_dict[key])[2])+'</td><td>'+str((my_dict[key])[3])+ '</td></tr>')
    outfile.write('</tbody></table>')
