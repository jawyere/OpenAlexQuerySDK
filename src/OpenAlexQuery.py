import pandas as pd
import requests
import ollama
import pickle
import os



class OpenAlexQuery:

    def __init__(self, tuple, **kwargs):
        #get API call string from input keywords
        self.fullTextKeys, self.AbstractAndTitleKeys = self.parseTupletuple(tuple)
        self.dataFilePath = kwargs.get("data_path", "./data/queries")
        self.from_year = kwargs.get("from_year", 2019)
        self.callString = self.listsToCallString(self.AbstractAndTitleKeys, self.fullTextKeys, self.from_year)
        self.df = None
        self.percentRelated = None

        #Quantitative Metadata



    def getMyMetaData(self):
        if(self.df.empty):
            print("dataFrame was not created yet")
            return (None, None, None, None)
#         print(f"""\nNumber of papers: {len(self.df)}
# Average Relevance Score: {round(float(self.df["relevance_score"].describe()["mean"]),2)}
# STD of Relevance Score: {round(float(self.df["relevance_score"].describe()["std"]),2)}
# Percent Related: {round(self.percentRelated,2)}""")
        return (len(self.df), float(self.df["relevance_score"].describe()["mean"]), float(self.df["relevance_score"].describe()["std"]) ,self.percentRelated)

    def getAPIQueryString(self):
        return self.callString

    def createDataFrame(self):
        
        dataFrames = []

        #initial variables before loop
        total_count = 1
        page_num = 0
        per_page = 200
        tempCallString = self.callString

        #add next page to df if not last page
        while(total_count > page_num * per_page):
            page_num += 1
            
            #get api data
            response = requests.get(tempCallString)
            data = response.json()

            #create df from file json and get needed metadata
            total_count = data.get("meta")["count"]
            page_num = data.get("meta")["page"]
            per_page = data.get("meta")["per_page"]
            results = data.get("results", [])
            
            
            temp_df = pd.DataFrame(results)
            dataFrames.append(temp_df)


            #update call string to point to next page and update page_num for while loop condition
            tempCallString = tempCallString.replace(f"&page={page_num}", f"&page={page_num+1}")

        allPageDataFrame = pd.concat(dataFrames, ignore_index=True)

        self.df = allPageDataFrame

    #add backup check with llm to make sure falses are actually false
    def addRelatedTitlesBool(self, LLM_prompt, n=None):

        if(self.df.empty):
            print("dataFrame was not created yet")
            return
        
        print(f"Adding key for first {min(n,len(self.df))} papers in dataframe")
        
        lis = []
        titles = self.df["title"]
        x = 0
        titleString = ""


        for i, title in enumerate(titles):

            if(n != None and i >= n):
                break
            response = ollama.chat(model='mistral', messages=[
            {
                'role': 'user',
                'content': f"""{LLM_prompt}

                {title}
                """,
            },])
           
            #if start with yes, true. otherwise false
            related = response['message']['content'].strip().lower()[:3] == "yes"
            print(f"Related to prompt ({title}): {related}")
            lis.append(related)

            x+=1
            print(f"{x} of {min(len(self.df), n)} complete")
        

        num_true = sum(1 for x in lis if x is True)
        self.percentRelated = num_true / len(lis) * 100
        self.df["is_title_related"] = pd.Series(lis)
                
    #update this for other popular keys
    def cleanDataFrame(self):
        #remove none or empty titles for llm prep
        if(self.df.empty):
            print("dataFrame was not created yet")
            return
                
     
        self.df = self.df[self.df["title"].notna() & (self.df["title"] != "")]


    def describeQuantitativeData(self):

        if "is_title_related" not in self.df.keys():
            raise ValueError("Need to create is_titel_related key before getting data")
        

        #gets description for boolean keys
        keys = ["is_retracted", "has_fulltext", "is_paratext", "is_title_related"]

        descriptionDF = self.df.describe()
        #has_fulltext seems to have innacurate data
        for key in keys:
            descriptionDF[key] = self.df.get(key).astype(int).describe()

        print(f"Percent of titles related to prompt: {self.percentRelated}", "\n")
        print(descriptionDF)

        return descriptionDF

    def describeMissingData(self):
        missingData = self.df.isnull().sum()
        totalMissing = sum(missingData)
        totalPercentMissing = totalMissing / (self.df.shape[0] * self.df.shape[1])
        percentMissing = missingData / len(self.df) * 100

        print("Total data missing: ", totalMissing, "\nPercent of total data missing: ", totalPercentMissing, "\n")

        items = [(missingData[key], percentMissing[key], key) for key in self.df.keys() if percentMissing[key] > 0]
        sortedItems = sorted(items, reverse=True)

        itemStrings = [f"{pair[2]} = {pair[0]}({round(pair[1],2)}%)" for pair in sortedItems]
        for i in range(0, len(items), 5):
            group = itemStrings[i:i+5]
            print(",  ".join(group))

        print("All other keys have no missing data")
        return missingData

    def getCorrelationMatrix(self):
        correlationMatrix = self.df.corr(numeric_only=True)
        print(correlationMatrix)
        return correlationMatrix

    def PlotQuantitativeInfo(self):
        pass

    def saveQuery(self, saveName = None):

        if saveName is None:
            saveName = self.fileName
        
        
        dir_path = "/home/jwagner/Projects/OpenAlexQuerySDK/data/queries/"
        filePath = os.path.join(dir_path, saveName) 
        
        with open(filePath, "wb") as f:
            pickle.dump(self, f)

    def process(self, prompt):
        self.createDataFrame()
        self.cleanDataFrame()
        self.addRelatedTitlesBool(prompt)
        return self

    def setupDisplay(self, displayWidth = 150):
        pd.set_option("display.width", displayWidth)
        pd.set_option("display.max_rows", None)
        pd.set_option("display.max_columns", None)
    
    def parseTupletuple(self, tuple):
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
            
       
        self.storeFileName(lisAbs_Title,lisFull_Text)

        return (lisFull_Text, lisAbs_Title)
    
    def storeFileName(self, abs_title_list, full_text_list):
        full_text_string = ""
        abs_title_string = ""

        for i,phrase in enumerate(full_text_list):
            full_text_string += phrase + "_"

            if (i != len(full_text_list) - 1):
                full_text_string += "_"

        for i,phrase in enumerate(abs_title_list):
            abs_title_string += phrase 

            if (i != len(abs_title_list) - 1):
                abs_title_string += "_"

        self.fileName = "q-" + abs_title_string + "-"  + full_text_string + ".pkl"

    def listsToCallString(self, abs_title_list, full_text_list, year):
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
    
    def toOutputFile(self, fileName):
        
        output_path = f"/home/jwagner/Projects/OpenAlexQuerySDK/data/outputData/{fileName}"
        with open(output_path, "a") as file:

            file.write(f"Query File Name: {self.fileName}\nRelevant Data: {self.getMyMetaData()}\n\n")
                    
    @staticmethod
    def loadQuery(fileName):
        
        filePath = "/home/jwagner/Projects/OpenAlexQuerySDK/data/queries/" + fileName
        with open(filePath, "rb") as f:
            return pickle.load(f)





if __name__ == "__main__":
    
    pd.set_option("display.width", 150)
    pd.set_option("display.max_rows", None)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_colwidth", None)  
 
    
    prompt = "Is this title directly related to optimization, especially algorithmic or combinatorial. Respond with \"yes\" or \"no\" after explanation"


    # query1 = OpenAlexQuery("simulated bifurcation machine")
    # query1.createDataFrame()
    # query1.cleanDataFrame()
    # query1.addRelatedTitlesBool(prompt, 13)
    # query1.saveQuery("q2:'simulated bifurcation machine'.pkl")

    # query1 = OpenAlexQuery.loadQuery("q2:'simulated bifurcation machine'.pkl")
    # q1.describeMissingData()
    # query1.describeQuantitativeData()
    # print(q1.df)


    #list of tuples to input and get data from


   

    inputList = [("digital annealer",),
     ("quantum annealer",),
     ("simulated bifurcation",),
     ("simulated bifurcation machine",),
     ("simulated quantum annealing",),
     ("toshiba", "simulated bifurcation",),
     ("toshiba", "sbm",),
     ("toshiba", "sqbm",),
     ("fujitsu", "digital annealer",),
     ("fujitsu",),
     ("toshiba",),
     ("d-wave",),
     ("d-wave", "quantum annealer")]  

    

    for name in inputList:
         q1 = OpenAlexQuery(name)
         q1.createDataFrame()
         q1.cleanDataFrame()
         q1.addRelatedTitlesBool(prompt, 30)
         q1.saveQuery()
         q1.getMyMetaData()
         q1.toOutputFile("output1.txt")

   



    