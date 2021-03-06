# This script shows how to connect to a JIRA instance with a
# username and password over HTTP BASIC authentication.
from collections import Counter
from jira import JIRA
from cStringIO import StringIO
import time
import sys 

#Codification system.
'''WATCH OUT THIS LINES ~ THESE COULD BROKE THE ENTIRE CODE; FIND SOME OTHER WAY TO ENCONDE THE STRINGS.'''
reload(sys)
sys.setdefaultencoding('utf-8')

#Constants
if (len(sys.argv)<2):
    __PROJECT__='BSTI'
else:
    __PROJECT__=sys.argv[1]

#Common functions

def getCustomFieldID(name):
    '''Getting all the current custom fields ID's and dump it to a CSV file for revision.'''
    # Fetch all fields
    allfields=jira.fields()
    # Make a map from field name -> field id
    nameMap = {field['name']:field['id'] for field in allfields}

    stringBuffer = StringIO()
    stringBuffer.write("Field Name;Code\n")

    for field in allfields:
        stringBuffer.write(field['name'] + ";" + field['id'] + "\n")

    getSendToCSVFile(stringBuffer.getvalue())
       
    if (name!=None):
        try:
            result=nameMap[name]
        except:
            return None
        #Well known codes:
            #customfield_11602 <- Story Points code for the custom field.
            #customfield_11606 <- Epic Link.
            #customfield_11607 <- Epic Name

        return result
    else:
        return None

def getSendToCSVFile(fileStr):
    '''Sends the String to a file'''
    f = open(".\\xls-export\\" + time.strftime("%Y%m%d") + "-" + time.strftime("%H%M%S") + "-jira-export.csv","wb")
    f.write(fileStr)
    f.close()

# By default, the client will connect to a JIRA instance started from the Atlassian Plugin SDK.
# See https://developer.atlassian.com/display/DOCS/Installing+the+Atlassian+Plugin+SDK
# for details.

options = {'server': 'http://issues.mercap.net:8080'}
jira = JIRA(options, basic_auth=('emartinez', 'itT85278952'))# a username/password tuple

# Get the mutable application properties for this server (requires
# jira-system-administrators permission)
#props = jira.application_properties()
# Find all issues reported by the admin


#Check how many files are required:
issues = jira.search_issues("project=" + __PROJECT__,startAt=0, maxResults=0)
issues = jira.search_issues("project=" + __PROJECT__,startAt=0, maxResults=issues.total)

completedDevelopmentSPs = 0
completedAnalysisSPs = 0
totalDevelopmentSPs = 0 
totalAnalysisSPs = 0
totalSPs = 0
totalIssues = 0
errorCount = 0
csvString=""
storyPoints = ""

#getCustomFieldID(None)
#time.sleep(1)

print ("Total amount issues available: " + str(issues.total))

#Searching for the issues and preparing the excel file for processing.
stringBuffer = StringIO()
stringBuffer.write("Issue;Type;Summary; Status; SPs\n")

for i in issues:

    totalIssues = totalIssues + 1

    #print(getCustomFieldID("Story Point"))
    #print(getCustomFieldID("Story Points"))
    
    try:
        
        if ((str(i.fields.issuetype) == "Testing") or (str(i.fields.issuetype) == "Analysis") or (str(i.fields.issuetype) == "Development")):
            
            storyPoints = str(i.fields.customfield_11602)
            
            if (str(i.fields.customfield_11602) != "None"):
             
                print("Issue: " + i.key.decode() + " Type: " + str(i.fields.issuetype) + " Summary: " + i.fields.summary.strip() + " Status: \'" + str(i.fields.status) + "\' SPs: " + storyPoints)
                
                stringBuffer.write(str(i.key).strip() + ";" + str(i.fields.issuetype) +  ";" + i.fields.summary.strip() + ";" + str(i.fields.status).strip() + ";" + str(int(i.fields.customfield_11602)) +"\n")
                
                totalSPs = totalSPs + float(storyPoints)

                #Summing the analysis and development story points by each side. #TODO:Needed refactoring.
                if ((str(i.fields.issuetype) == "Testing") or (str(i.fields.issuetype) == "Analysis")):
                    totalAnalysisSPs += float(storyPoints)
                elif (str(i.fields.issuetype) == "Development"):
                    totalDevelopmentSPs = totalDevelopmentSPs + float(storyPoints)
                
                if ((str(i.fields.status)=='Approved') or (str(i.fields.status)=='Closed') or (str(i.fields.status)=="Ready To Merge")  or (str(i.fields.status)=="Ready To Test")):
                    
                    if (str(i.fields.issuetype) == "Development"):
                        completedDevelopmentSPs = completedDevelopmentSPs + float(storyPoints)
                    else:
                        completedAnalysisSPs = completedAnalysisSPs + float(storyPoints)
        else:
            print("Issue: " + i.key.decode() + " Type: " + str(i.fields.issuetype) + " Summary: " + i.fields.summary.strip() + " Status: \'" + str(i.fields.status) + "\' SPs: " + storyPoints)
            if (i.fields.timespent!=None):
                print(" Time Spent:" + str(i.fields.timespent/3600))

                    
    except Exception as e:

        print("Error in Issue: " + str(i.key) + " -> " + i.fields.summary + " Error: " + str(e))

        stringBuffer.write(str(i.key) + ";" + str(i.fields.issuetype) +  ";" +  i.fields.summary.strip() +";" + str(i.fields.status) + ";0" + "\n")

        errorCount = errorCount + 1
        pass

print("\n"*3)
print("-"*80)
print("\n")
print("Total issues: " + str(totalIssues))
print("Completed Development SPs: " + str(completedDevelopmentSPs) + "/" + str(totalDevelopmentSPs))
print("Completed Analysis SPs: " + str(completedAnalysisSPs) + "/" + str(totalAnalysisSPs))
print("Total SPs: " + str(totalSPs))
print("Error records: " + str(errorCount))

getSendToCSVFile(stringBuffer.getvalue())
stringBuffer.close()

# Find the top three projects containing issues reported by admin
'''top_three = Counter(
[issue.fields.project.key for issue in issues]).most_common(3)

print(top_three)

boardBST = jira.boards(name='BST - Scrum')

print(boardBST)'''
