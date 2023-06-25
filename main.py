# Run the Main Program
import click 
import datetime
from datetime import date
from datetime import datetime,timedelta
import json
import csv


from recall_package.utils import NTHSA
from recall_package.utils import get_recalls
from recall_package.utils import get_recent_recalls
from recall_package.utils import get_recall_mapping
from recall_package.utils import find_canadian_recalls




## Click

@click.group()
def cli():
    """A tool used to get recall information from NTHSA Database"""
    pass

@click.command(short_help = "Used to update json mapping file")
@click.option('--min',prompt = "Please enter minimum model year: ", help = "Minimum Model Year")
@click.option('--max',prompt = "Please enter maximum model year: ", help = "Maximum Model Year")
def updatejson(min,max):
    print("Updating mapping file")
    master_json = get_recall_mapping(min_year = min, max_year= max)
    


@click.command(short_help = "Gets all recall info between min and max year")
@click.option('--min',prompt = "Please enter minimum model year: ", help = "Minimum Model Year")
@click.option('--max',prompt = "Please enter maximum model year: ", help = "Maximum Model Year")
@click.option('--num_weeks',prompt = "Please number of weeks past to search: ", help = "Number of weeks ago to filter")
def getrecalls(min,max,num_weeks):
    # Open File
    with open('docs/mapping.json') as data_file:
        year_make_model = json.load(data_file)

    # Get Master
    master_nthsa = get_recalls(year_make_model,int(min),int(max),int(num_weeks))

    # Get Recent Recalls
    get_recent_recalls(master_nthsa)


@click.command(short_help = "Gets recall information for a specific NTHSA number")
@click.option("--nthsa", help = "Enter NTHSA for specific data")
def getrecall(nthsa):

    recall = NTHSA(nthsa_num = nthsa)
    print("")
    print(recall)

@click.command(short_help = "Gets all recall info for canada")
@click.option("--week_num", prompt = "Please number of weeks past to search: ",help = "Number of weeks to filter out")
def getrecalls_canadian(week_num):
    find_canadian_recalls(int(week_num))

cli.add_command(updatejson)
cli.add_command(getrecalls)
cli.add_command(getrecall)
cli.add_command(getrecalls_canadian)
if __name__ == "__main__":
    cli()




