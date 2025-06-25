import pandas as pd
import requests
import ollama



class OpenAlexQuery:

    def __init__(self, *args, **kwargs):
        self.fullTextKeys, self.AbstractAndTitleKeys = self.parseTupletuple(args)
        self.from_year = kwargs.get("from_year", 2019)
        self.callString = self.listsToString(self.AbstractAndTitleKeys, self.fullTextKeys, self.from_year)
        self.df = None
        self.percentRelated = None



    def getAPIQueryString(self):
        return self.callString

    def createDataFrame(self):
        
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

        self.dataFrame = allPageDataFrame


    def addRelatedTitlesBool(self, LLM_prompt):

        if(self.dataFrame == None):
            raise ValueError("dataFrame was not created yet")
        
        lis = []
        total_titles = self.df.shape[0]
        titles = self.df["title"]
        x = 0
        titleString = ""

        for title in titles:
            response = ollama.chat(model='mistral', messages=[
            {
                'role': 'user',
                'content': f"""{LLM_prompt}

                {title}
                """,
            },])
           
            #if start with yes, true. otherwise false
            if(response['message']['content'].strip().lower()[:3] == "yes"):
                lis.append(True)
            else:
                lis.append(False)

            x+=1
            print(f"{x} of {total_titles} complete")
        

        num_true = sum(1 for x in lis if x is True)
        self.percentRelated = num_true / total_titles
        self.df["is_title_related"] = pd.Series(lis)
                
    #update this for other popular keys
    def cleanDataFrame(self):
        #remove none or empty titles for llm prep
        self.df = self.df[self.df["title"].notna() & (self.df["title"] != "")]


    def previewQuery(self,):
        pass

    def showImportantInfo(self):
        pass

    def saveQuery():
        pass

    def loadQuery():
        pass

    def _internal_methods():
        pass

    #should just output basic desc of first n papers
    @staticmethod
    def previewQuery(callString, n):
        pass
        

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
    



if __name__ == "__main__":
    print("deez")





    