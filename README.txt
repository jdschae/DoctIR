doctIR
John Schaefer, Alex Li, Michael Lee, Akash Ramanujam

======= Prerequisites =======

Python 3.6+

Python packages:
    Beautiful Soup 4
    Requests
    Natural Language Toolkit
    Natural Language Toolkit's Porter stemmer

======= Instructions =======

=== Data collection / Web scraping ===

Before our program can be run, you must have the illness dataset used to build the
vector space model. The dataset is included with our submission, but if you need
to obtain it again, then you can run our web scraper:

$ python scraper.py

This script will create JSON files containing data from www.wikipedia.org,
www.cdc.gov, and www.mayoclinic.org. These files are named wikipedia.json,
cdc.json, and mayoclinic.json.

=== Main program ===

When run, our program will build a vector space model using all of the scraped
data. Because of the size of the dataset, this process may take a while. We have
provided a serialized version of the vector space model that will allow you to
avoid building the vector space model when running our program. Extract the file
model.tar.gz and place it in the same directory as doctir.py.

$ tar -xzvf model.tar.gz

Running the above command should produce a file called model.pkl, which doctir.py
will read into a VectorSpaceModel object during execution.

Run the main program by entering:

$ python doctir.py

You will be shown a disclaimer and asked whether you understand it. Enter 'y' to
proceed, or any other input to cancel.

If you do not have the serialized vector space models saved, then the program
will build the vector space models and save them locally.

After the vector space models are built/loaded, you will be asked to enter some
symptoms. The total number of relevant illnesses that exhibit your entered
symptoms and the top 10 relevant results will be displayed on the screen.
If there are more than 10 illnesses, then you will be asked whether you want
to see more. Press 'y' to display more results, or any other key to cancel.
