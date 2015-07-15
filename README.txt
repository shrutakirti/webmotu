Webmotu is ready to be deployed with some basic functionality! It can also be downloaded to run locally on a machine.

If you want to download and run webmotu on your machine, follow these steps:

step 1: ssh username@servername

step 2: Install Flask and usearch(8 or above!). Usearch may require an academic license.
Step 2.5: Make sure your machine contains Python 2.7 or above

step 3: clone webmotu from github: https://github.com/shrutakirti/webmotu.git

step 4: Go into the webmotu folder and modify the webmotu_uparse_config.cfg file as follows. This will help Webmotu understand where usearch is located on your machine.
	[Section]
        usearch_location = /path/to/usearch8/on/your/machine
step 5: Go into to the webmotu folder ["cd webmotu"], and run webmotu.py:
        python webmotu.py

step 6: Webmotu is up and running! Celebrate with a cupcake and a cuppa joe.
