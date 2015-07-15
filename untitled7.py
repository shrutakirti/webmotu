# -*- coding: utf-8 -*-
"""
Created on Mon Jun 22 12:21:01 2015

@author: kirti
"""
import urllib
import xml.etree.ElementTree as ET
import ConfigParser

config = ConfigParser.ConfigParser()
readconfig = config.read('webmotu_bold_config.cfg')#change to location of config file
request_url = config.get('Section', 'bold_species_url')
#for sanity check
#my_dict = {'ACTCTATATTTTATTTTCGGAGCTTGAGCAGGTATAGTAGGAACTTCTCTAAGAATTCTTATTCGAGCAGAATTAGGTCATCCTGGTGCATTAATTGGTGATGATCAGATTTATAACGTAATTGTTACA':['LSAFR2136-12','Bastilla torrida','1','someurl'], 
#'ACATTATATTTNATTTTNGGAATTTGAGCAGGAATAGTAGGAACATCCTTAAGACTATTAATTCGAGCAGAATTGGAAATCCTNGGATCTTTAATTGGAGATGACCAAATTTATAACACTATTGTTACA':['GWORL383-09','Deltote deceptoria','1','someurl'],'ACCTTATACTTCATTTTNGGAGCTTGATCAGGAATAGTAGGAACTTCACTTAGTATACTTATTCGAGCAGAACTTAATCAACCCGGATCTCTTATTGGAGATGATCAAATTTATAATGTTATTGTAACA':['No hit','--','--','--'],}
specimen_datas=[]
specimen_data_parsed=[]

def specimen_data_retrieval(my_dict):
    
   # request_url = 'http://www.boldsystems.org/index.php/API_Public/specimen?ids='
    for key in my_dict.iterkeys():
        
        value = my_dict[key]
        seq_id = value[0]
        print request_url+str(seq_id)
        if (not seq_id == 'No hit'):
            specimen_data = urllib.urlopen(request_url+str(seq_id))
        else:
            specimen_data = ''
        specimen_datas.append([key,specimen_data])

    return specimen_datas


def specimen_data_parser(specimen_datas):
    
    phylums = [] #list all phylums in result
    class_names = []# list all classes in result
    orders = []#list all orders in result
    genuss = []#list all genuses in result
    speciess = []#list all species in result
    
    phylum_set = set()#set of all phylums
    classname_set = set()#set of all classes
    order_set = set()#set of all orders
    genus_set = set()#set of all genuses
    species_set = set() #set of all species
        
    for specimen_data in specimen_datas:
        if (not specimen_data[1]==''):
            
            tree = ET.parse(specimen_data[1])
            root = tree.getroot()
            
        #parse data from second call to BOLD: detailed taxonomic information
            for record in root.findall('record'):
                
                phylum = record.find('taxonomy').find('phylum').find('taxon').find('name').text
                class_name = record.find('taxonomy').find('class').find('taxon').find('name').text
                order = record.find('taxonomy').find('order').find('taxon').find('name').text
                genus = record.find('taxonomy').find('genus').find('taxon').find('name').text
                species = record.find('taxonomy').find('species').find('taxon').find('name').text
                
                phylums.append(phylum) #populate phylums[]
                class_names.append(class_name)#populate classnames[]
                orders.append(order) #populate orders[]
                genuss.append(genus) #populate genuss[]
                speciess.append(species) #populate speciess[]
                specimen_data_parsed.append([specimen_data[0],phylum,class_name,order,genus,species])
                
                phylum_set.add(phylum) #populate phylum_set
                classname_set.add(class_name) #populate classname_set
                order_set.add(order) #populate order_set
                genus_set.add(genus) #populate genus_set
                species_set.add(species) #populate species_set

                total_phylum_count = len(phylums) #total number of phylums in phylums[]
                total_classname_count = len(class_names)#total number of classnames in class_names[]
                total_order_count = len(orders)
                total_genus_count = len(genuss)
                total_species_count = len(speciess)
                
                

                
                for phylum in phylum_set:
                    phylum_count = phylums.count(phylum)#no of instances of a genus in genuss[]
                    phylum_percentage = float((phylum_count*100)/total_phylum_count)#percentage of a genus in genuss[]
                    print "no of "+phylum +" in list of phylums is "+ str(phylum_count)
                    print "% of "+phylum+ "is "+str(phylum_percentage)     
                
                for classname in classname_set:
                    classname_count = class_names.count(classname)#no of instances of a classname in class_names[]
                    classname_percentage = float((classname_count*100)/total_classname_count)#percentage of a classname in class_names[]
                    print "no of "+classname +" in list of classnames is "+ str(classname_count)
                    print "% of "+classname+ "is "+str(classname_percentage)
            
                for order in order_set:
                    order_count = orders.count(order)#no of instances of a order in orders[]
                    order_percentage = float((order_count*100)/total_order_count)#percentage of a order in orders[]
                    print "no of "+order +" in list of orders is "+ str(order_count)
                    print "% of "+order+ "is "+str(order_percentage) 
                
                for genus in genus_set:
                    genus_count = genuss.count(genus)#no of instances of a genus in genuss[]
                    genus_percentage = float((genus_count*100)/total_genus_count)#percentage of a genus in genuss[]
                    print "no of "+genus +" in list of genuss is "+ str(genus_count)
                    print "% of "+genus+ "is "+str(genus_percentage) 
                
                for species in species_set:
                    species_count = speciess.count(species)#no of instances of a genus in genuss[]
                    species_percentage = float((species_count*100)/total_species_count)#percentage of a genus in genuss[]
                    print "no of "+species +" in list of speciess is "+ str(species_count)
                    print "% of "+species+ "is "+str(species_percentage) 
    return specimen_data_parsed
def init_data():
    outfile = open('templates/outfile.html','w')
    outfile.write('<table name = "final" id = "final"><thead><th>OTU</th><th>Phylum</th><th>Class</th><th>Order</th><th>Genus</th><th>Species</th></thead><tbody>')
    return outfile
    
def write_to_file(specimen_data_parsed):
    outfile = init_data()
    for data in specimen_data_parsed:
        outfile.write("<tr><td>"+str(data[0])+"</td><td>"+str(data[1])+"</td><td>"+str(data[2])+"</td><td>"+str(data[3])+"</td><td>"+str(data[4])+"</td><td>"+str(data[5])+"</td></tr>")
    outfile.write("</tbody></table></body></html>")

