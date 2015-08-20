Webmotu performs Barcode Clustering and Taxonomic Identification.
-----------------------------------------------------------------------
**If you want to access webmotu online, goto www.webmotu.bio.ed.ac.uk**
-----------------------------------------------------------------------
This folder contains 2 config files and 4 python scripts:

*Config files*
webmotu_usearch_config.cfg - contains the location of installed USEARCH.

webmotu_bold_config.cfg - contains URLs of two BOLD APIs. First section contains URL for the PUblic Records Barcode Database, second section contains the URL for Species Level Barcode Records database.

*Python Scripts*
webmotu.py - the main script. responsible for temp file creation, scheduling execution of other scripts in the folder, displaying results to user

uparse_helper.py - performs USEARCH Pipeline

bold_helper.py - contacts BOLD to get preliminary taxonomic information and parses response

detail_getter.pt - contacts BOLD to get detailed taxonomic information, parses response, calculates abundance

-----------------------------------------------------------------------------


If you want to download and run webmotu on your machine, follow these steps:

step 1: ssh username@servername

step 2: Install Flask(0.10 or above) and USEARCH(8 or above). USEARCH may require an academic license.
Step 2.5: Make sure your machine contains Python 2.7 or above

step 3: clone webmotu from github: https://github.com/shrutakirti/webmotu.git

step 4: Go into the webmotu folder and modify the webmotu_usearch_config.cfg file as follows. 

       [Section]
       usearch_location = /path/to/usearch8/on/your/machine

step 5: Go into to the webmotu folder ["cd webmotu"], and run webmotu:
 python webmotu.py

step 6: Webmotu is up and running!
--------------------------------------------------------------------------------

Contact: s1460720@sms.ed.ac.uk
