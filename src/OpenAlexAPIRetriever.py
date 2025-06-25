import ollama
import subprocess
import json
import pandas as pd
import requests
prompt = "Is this title directly related to optimization, especially algorithmic. Respond with \"yes\" or \"no\" after explanation"

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

    
    callString = listsToString(AbstractAndTitleKeys, fullTextKeys, from_year)

    return callString
   

def getFileName(fullTextKeys, AbstractAndTitleKeys):
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
    path = f"/home/jwagner/Projects/OpenAlexQuerySDK/data/inputData/{name}.json"

    return path

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
        string = f"https://api.openalex.org/works?search={searchString}&filter=publication_year:>{year}&per_page=200&page=1"

    if not searchString:
        string = f"https://api.openalex.org/works?filter=title_and_abstract.search:{filterString},publication_year:>{year}&per_page=200&page=1"

    #has a search and filter string
    else:
        string = f"https://api.openalex.org/works?search={searchString}&filter=title_and_abstract.search:{filterString},publication_year:>{year}&per_page=200&page=1"
    
    return string


"""
checks if the new page added to inputData is the last one. Adds all to dataframe. stores pandas df in input
Creates pandas dataframe of all pages

I need to choose to have this take an apicallstirng or json file. I htink i will od api call stirng
"""
def getDataFrame(callString):

    dataFrames = []

    #initial variables before loop
    total_count = 1
    page_num = 0
    per_page = 200

    #add next page to df if not last page
    while(total_count > page_num * per_page):
        page_num += 1
        
        #get api data
        response = requests.get(callString)
        data = response.json()

        #create df from file json and get needed metadata
        total_count = data.get("meta")["count"]
        page_num = data.get("meta")["page"]
        per_page = data.get("meta")["per_page"]
        results = data.get("results", [])
        
        
        temp_df = pd.DataFrame(results)
        dataFrames.append(temp_df)


        #update call string to point to next page and update page_num for while loop condition
        callString = callString.replace(f"&page={page_num}", f"&page={page_num+1}")
        
    


    allPageDataFrame = pd.concat(dataFrames, ignore_index=True)

    return allPageDataFrame

#uses ollama LLM to create new hasRelatedTitle key to the dataFrame    
def addRelatedTitleKey(df):

    titleSeries = df.get("title")
    print(titleSeries)

    

#removes papers without titles
def cleanTitleData(df):

    #remove none or empty titles for llm prep
    df = df[df["title"].notna() & (df["title"] != "")]

   
def add_has_related_titles(df, prompt):
    lis = []
    
    total_titles = df.shape[0]
    print(total_titles)
    
    titles = df["title"]
    x = 0
    titleString = ""
    for title in titles:
        
        response = ollama.chat(model='mistral', messages=[
        {
            'role': 'user',
            'content': f"""{prompt}

            {title}
            """,
    },
    ])
        print(title, "\n", response['message']['content'], "\n\n")
        #if start with yes, true. otherwise false
        if(response['message']['content'].strip().lower()[:3] == "yes"):
            lis.append(True)
        else:
            lis.append(False)
        x+=1
        print(x)
      
        num_true = sum(1 for x in lis if x is True)

        related_ratio = num_true / total_titles

        print(related_ratio)




    df.insert(3, "has_related_title", lis)
    return






def saveDataFrame(df, saveName):

    saveName = "/home/jwagner/Projects/OpenAlexQuerySDK/data/dataFrame/" + saveName + ".pkl.gz"
    df.to_pickle(saveName, compression = "gzip")


#/home/jwagner/Projects/OpenAlexQuerySDK/data/inputData

#'/home/jwagner/Projects/OpenAlexQuerySDK/data/inputData/F:|AT:simulated_bifurcation|p1.json'


prompt = "Is this title directly related to optimization, especially algorithmic. Respond with \"yes\" or \"no\" after explanation"

pd.set_option("display.max_rows", None)
a = getCallString("digital annealer")

b = getDataFrame(a)


cleanTitleData(b)



add_has_related_titles(b, prompt)

saveDataFrame(b, "df3:\"digital annealer\"")

# hi = pd.read_pickle('df2:"simulated bifurcation".pkl.gz')
# print(hi.iloc[:,3])



