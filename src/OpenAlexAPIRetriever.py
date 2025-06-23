import ollama
import subprocess
import json
import pandas as pd

"""
Parameters:
allPages: boolean. True to get all pages. False to get first page
(args)
string: to be searched for
boolean: search in whole text if False, just abstract and title if True
(kwargs)
from_year = 2019: searches default from the year 2019 (exclusive) (so will be inclusive 2020-present)

Returns:
tuple (path_to_save_to, api_call_String)
"""
def getCallString(*args, **kwargs):
    fullTextKeys, AbstractAndTitleKeys = parseTupletuple(args)
    from_year = kwargs.get("from_year", 2019)

    full_text_string = ""
    abs_title_string = ""

    #MAKE HTIS NOT PRINT _ FOR THE LAST ITER+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    for i,phrase in enumerate(fullTextKeys):
        full_text_string += phrase + "_"

        if (i != len(fullTextKeys) - 1):
            full_text_string += "_"

    for i,phrase in enumerate(AbstractAndTitleKeys):
        abs_title_string += phrase 

        if (i != len(AbstractAndTitleKeys) - 1):
            abs_title_string += "_"

    #F: words/phrases in full text
    #AT: words/phrases in abstract or title
    name = f"F:{full_text_string}|AT:{abs_title_string}|p1"
    callString = listsToString(AbstractAndTitleKeys, fullTextKeys, from_year)
    path = f"/home/jwagner/Projects/PracticeProjects/data/inputData/{name}.json"

    return (path, callString)
   
    #subprocess.run(["curl", callString, "-o", path])


def parseTupletuple(tuple):
    n = len(tuple)
    i = 0
    lisAbs_Title = []
    lisFull_Text = []
    
    in_abs_title = True
    label = ""

    while(i < n):
        #default values
        in_abs_title = True
        label = "defualt"

        #put label in list depending on next boolean
        if(isinstance(tuple[i], str)):
            label = tuple[i]
        else:
            raise ValueError("expected a string.")

        if(i + 1 < n and isinstance(tuple[i+1], bool)):
            in_abs_title = tuple[i+1]
           
            i += 1

        #must prep names so can be read by subprocessor
        label = label.replace(' ', "%20")
      
        
        if in_abs_title == True:
            lisAbs_Title.append(label)
        else:
            lisFull_Text.append(label)

        i += 1
       

    return (lisFull_Text, lisAbs_Title)
        


    #MAKE OPTION FOR PAGE SELECTION________________________________________________________________________________
def listsToString(abs_title_list, full_text_list, year):

   
    searchString = ""
    for i, phrase in enumerate(full_text_list):
        if i == len(full_text_list) - 1:
            searchString += f"\"{phrase}\""
        else:
            searchString += f"\"{phrase}\"AND"


    filterString = ""
    for i, phrase in enumerate(abs_title_list):
        if i == len(abs_title_list) - 1:
            filterString += f"\"{phrase}\""
        else:
            filterString += f"\"{phrase}\"AND"
    

    string = ""
 
    if not filterString and not searchString:
        raise ValueError("no search parameters given")
    
    if not filterString:
        string = f"https://api.openalex.org/works?search={searchString}&filter=publication_year:>{year}&per_page=200"

    if not searchString:
        string = f"https://api.openalex.org/works?filter=title_and_abstract.search:{filterString},publication_year:>{year}&per_page=200"

    #has a search and filter string
    else:
        string = f"https://api.openalex.org/works?search={searchString}&filter=title_and_abstract.search:{filterString},publication_year:>{year}&per_page=200"
    
    return string


"""
checks if the new page added to inputData is the last one. Adds all to dataframe. stores pandas df in input
Creates pandas dataframe of all pages
"""
def toDataFrame(filePath):

    #create df from file json
    with open(filePath) as dataFile:
        data = json.load(dataFile)

        total_count = data.get("meta")["count"]
        page_num = data.get("meta")["page"]
        per_page = data.get("meta")["per_page"]

        results = data.get("results", [])
        df = pd.DataFrame(results)
    

    #add next page to df if not last page
    if(total_count > page_num * per_page):
        pass

    

    
#/home/jwagner/Projects/PracticeProjects/data/inputData





a = getCallString("digital annealer")

toDataFrame('/home/jwagner/Projects/PracticeProjects/data/inputData/F:|AT:digital%20annealer|p1.json')