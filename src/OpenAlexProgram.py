import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

"""
I need to spread the data into different dataframes and merge them since there is a max of 200 papers per API call
"""


string = ""
      
x = 1
with open('/home/jwagner/Projects/PracticeProjects/data/inputData/inputData2_sbm_phrase_abstract.json') as data_file:
    data = json.load(data_file)
    string += "title,id,pub_date,cited_by_count,referenced_works_count\n"

    for paper in data.get("results"):

        string += "\"" + paper.get("title") + "\","
        string += paper.get("id") + ","
        string += paper.get("publication_date") + ","
        string += str(paper.get("cited_by_count")) + ","
        string += str(paper.get("referenced_works_count")) + "\n"
   




with open("/home/jwagner/Projects/PracticeProjects/data/outputData/sbmData2_sbm_phrase_abstract.csv", "w") as f:
     f.write(string)




"""
All output files in form: title, id(link), publication_date, cited_by_count, referenced_work_count



sbmData1 contains all works with the words "simulated", "bifurcate", "machine"


"""


f = "/home/jwagner/Projects/PracticeProjects/data/outputData/sbmData1_sbm_sepWords_abstract.csv"

# papers1 = pd.read_csv(f, parse_dates=["pub_date"])
# papers1.set_index("pub_date", inplace=True)
# plt.plot(papers1.index, papers1["cited_by_count"], "ro", label="Cited by Count")
# plt.plot(papers1.index, papers1["referenced_works_count"], "g^", label="Referenced Works Count")
# plt.legend()
# plt.show()

fig, axes = plt.subplots(1,3,figsize=(12, 4))  # Wide and short figure


x = np.linspace(0,10,20000)

axes[0].plot(x,np.sin(x))
axes[0].set_title('sin')

axes[1].plot(x,np.cos(x))
axes[1].set_title('cos')

axes[2].plot(x,np.tan(x))
axes[2].set_title('tan')
plt.text(.5, 0, 'This is a note on the figure', ha='center', va='center', fontsize=12, color='gray', transform=plt.gcf().transFigure)

plt.show()




"""
from Meta Data
1 simulated bifurcation machine (seperate words in abstract): 63 papers found 
2 simulated bifurcation machine (whole phrase together in abstract): 7 papers found
3 simulated bifurcation machine (whole phrase together in full text): 50 papers found
4 simulated bifurcation machine (seperate words in full text): 2767 papers found
5 digital anealer (whole phrase together in full text): 278 papers found
6 digital anealer (whole phrase together in abstract): 124 papers found
7 d-wave (whole phrase together in abstract): 2376 papers found
8 d-wave (whole phrase together in full text): 7508 papers found
"""



""" NEW (abs = abstract + title //// sep = words can be seperated but all must be there)
simulated bifurcation machine (abs): 72 results, 
simulated bifurcation(abs): 2,234 results
simulated bifurcation (whole text):
digital annealer (abs):
digital annealer (whole text):
digital annealing (abs):
digital annealing (whole text): 149
quantum optimization (abs), fujitsu (full text): 107 Results, x/20 unrelated
toshiba (full text), simulated bifurcation (abs): 7 results, 3/7 unrelated
toshiba (full text), quantum optimization (abs): 44 results
sqbm+ (full text): 12
sqbm+ (abs): 4
Toshiba quantum optimization (abs): 9
toshiba bifurcation (abs): 23   (only 3 seemed relevant)
quantum optimization (phrase) (abs): 675
quantum optimization (sep) (abs): 27583


"""




