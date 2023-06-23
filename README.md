# How to run the scrpit

## 1 - Install Jupyter Notebook
https://jupyter.org/install

## 2 - Create a python virtual environment
Inside the data_entry folder run `python -m venv venv` on the commad line to create the virtual environment. Activate the virtual environment by running `source venv/bin/activate` (or `venv/bin/activate` on windows). When inside the venv, run `pip install -r requirements.txt` the install the necessary packages.

## 3 - Run the scrpit
There is a folder called 'reports' and this is where you should put the reports you want to analyse.

The script will output croped images, taken from the report, where the regex expressions matched the text. The names the these images will first have the name of the report, followed by the name of the indicator the expression matched (for example "ghg").

Open the `find_expressions.ipynb` file and just follow the insctructions there.