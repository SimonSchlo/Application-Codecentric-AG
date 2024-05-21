###########################################################################################################################################
# Description:
#
# This script works this way:
# 0.) Entered your github username + token into the following variables.
# 1.) Extract the data (names, repos and programming languages) of the members of Codecentric AG via a request-method. 
# --> Function: get_memberData(...)
# 2.) Create tkinter-Window as a tool for searching the member data for specific search words (names, repos and programming languages) and outputting results of the search runs.
# --> Function: create_tkWindow(...)
#     2.1) Search algorithm/function implemented behind search button of tkinter-window: search_StringInData()
# 3.) Enter one search word in at least one entry widget of the tkinter-window. If a search word was entered in multiple entry field, then the Codecentric members' data will be looked through a match, that fulfills all search word criteria.
#     3.1) In case a search word was entered in multiple fields: Function for getting the intersection of the searches with eaches search word: get_commonElementsOfLists
#     3.2) Visual preparing algorithm/function of the matches: convert_ListIntoStringEnumeration()
# 4.) Match(es) get printed out to the result text widget in the tkinter-window.
###########################################################################################################################################


##########################################################################################
# Variables to be modified according to the user
github_username = 'SimonSchlo' # Enter user name of github account
github_token = 'fbgf6_nh_blablabla' # Enter github token
##########################################################################################


import numpy as np
import requests
import json
import tkinter as tk


'''
Description: Get data of the members of codecentric AG.

Output: a list where each element is a dict for one member. The dict contains info about the member's name, repos and programming languages.
--> member name = 'login' of member (from github-link: https://api.github.com/orgs/codecentric/members)
--> member repo = repos listed in 'repos_url' of member (e.g. from github-link https://api.github.com/users/danielbayerlein/repos)
--> member programming language = extract info (keys) from 'languages_url' of each repo of each member. (e.g. from github-link https://api.github.com/repos/danielbayerlein/alfred-workflows/languages)
    Sort the programming languages and avoid duplicates (same languages used for tools of different repos).

Params:
- link: url of the origin of the data
- user_name: github user name of the member executing this script
- user_token: github user token of the member executing this script
'''
def get_memberData(link, user_name, user_token):
    # Get codecentric member data
    responseObject_members = requests.get(link, auth=(user_name,user_token))

    members = responseObject_members.json() # convert response from JSON object into python object (in this case: since data structure of JSON object is a list, a list is returned)

    codecentric_membersData = [] # a list of lists containing all member names, their repos and their programming languages

    for i, member in enumerate(members):
        
        '''if i == 1: # to be deleted
           break'''

        member_data = {} # member-specific dict containing current member name, his/her repos and his/her programming languages
    
        # Name of member (according to login identification)
        member_name = [] # List containing the name of the member
        member_name.append(members[i]['login'])

        # Get repos
        member_repos_url = members[i]['repos_url']
        member_repos_response = requests.get(member_repos_url, auth=(user_name,user_token))
        member_repos_list_raw = member_repos_response.json() # convert response from JSON object into python object (in this case: since data structure of JSON object is a list, a list is returned)
        
        member_repos = [] # List containing all repos of the current member
        member_languages = [] # List containing all used programming languages (according to the repos) of the member
        
        # Iterate through every repo to get the name of the repo and the programming languages used for the tool at the repo
        for repo in member_repos_list_raw:
            # Add repo name
            member_repos.append(repo['name']) 
            
            # Get programming language used for the tool of the repo
            member_repo_languages_url = repo['languages_url']
            member_repo_languages_response = requests.get(member_repo_languages_url, auth=(user_name,user_token))
            member_repo_languages_dicts = member_repo_languages_response.json() # returns programming languages as a dict (where keys = programming language)
            member_repo_languages_list = list(member_repo_languages_dicts.keys()) # get only the programming languages (keys) of the dict + convert to list
            if len(member_repo_languages_list) != 0:
                member_languages.extend(member_repo_languages_list)


        # Delete duplicate values of programming languages in members' languages list
        member_languages_clean = []
        for language in member_languages:
            if language not in member_languages_clean:
                member_languages_clean.append(language)
        # Sort the clean programming language list
        member_languages_clean.sort() 

        # Add current member name, his/her repos and his/her programming languages to one member-specific dict
        member_data['Member name'] = member_name
        member_data['Repos'] = member_repos
        member_data['Programming languages'] = member_languages_clean

        # Add data of current member to an overall list containing data of all members
        codecentric_membersData.append(member_data)

    codecentric_membersData = np.array(codecentric_membersData, dtype=object) # convert list to numpy-array for easier accessability (via indexing)

    return codecentric_membersData


'''
Description: Function for creating a window with labels, entry fields and a result output.

Output: a tkinter-window with different widgets/fields

Params:
- title: title of the window
- data_list: data to be searched through (in shape of a list) (here: Codecentric member data)
-
'''
def create_tkWindow(title, data_list):
    tkWindow = tk.Tk()
    tkWindow.title(title)
    tkWindow.geometry('1000x600')

    tkWindow_fieldNames= ['Member:','Repos:','Programming languages:']
    num_fields = len(tkWindow_fieldNames)

    fields = [] # list containing all entry fields
    
    for i in range(0, num_fields):
        
        # Label (of the entry field) on the left side of the window
        field_label = tk.Label(master=tkWindow, text=tkWindow_fieldNames[i])
        field_label.grid(row=i+1, column=0, pady=5, sticky=tk.W)
        # Entry field on the right side of the window
        field_entry = tk.Entry(master=tkWindow, width = 50, bg='white')
        field_entry.grid(row=i+1, column=1, pady=5, sticky=tk.W)

        fields.append(field_entry)
    
    # Button for searching
    searchButton = tk.Button(master=tkWindow, width = 40, bg='#FBD975', text='Search', command=lambda: search_StringInData(data_list, fields, results_field))
    searchButton.grid(row=num_fields+1, column=1, pady=(20, 20), sticky=tk.W)

    # Label for presenting the results
    results_Label = tk.Label(master=tkWindow, bg = '#b0ffab', text='Results:')
    results_Label.grid(row=num_fields+2, column=0, sticky=tk.NW, pady=2)

    # Field for the results of the search + scrollbar (for large result lists)
    results_field_frame = tk.Frame(master=tkWindow) # Create a results field frame for the scrollbar and the text field
    results_field_frame.grid(row=num_fields+2, column=1)
    results_field_scrollbar = tk.Scrollbar(results_field_frame, orient="vertical") # add a scrollbar to the results field frame
    results_field = tk.Text(results_field_frame, bg = '#f2f2f2', width = 100, yscrollcommand=results_field_scrollbar.set) # add a text field to the results field frame
    results_field.pack(side='left', fill='both', expand=True)
    results_field_scrollbar.config(command=results_field.yview)
    results_field_scrollbar.pack(side='right', fill='y')

    return tkWindow


'''
Description: Function for searching data for a given string

Output: -

Params:
- data_list: data to be searched through (in shape of a list) (here: Codecentric member data)
- fields: fields ("widgets") of the tkinter-window
- resultField: field ("widget"), in which the output/matches shall be outputted
'''
def search_StringInData(data_list, fields, resultField):
    
    ## Lists
    ## 1. element: entry field 1 = member name
    ## 2. element: entry field 2 = repo
    ## 3. element: entry field 3 = programming languages
    matches = [None, None, None] # (initialization) Matches of the search word in the entry field with the data
    searchWord = [None] * len(fields)  # (initialization) Entered search words of "name"-entry field, "repo"-entry field and "programming language"-entry field

    for i, field in enumerate(fields):
        matches_field = [] # Matches in the data corresponding to the field (e.g. matches in data for "name" by input in "name"-entry field)
        if len(fields[i].get()) != 0: # Check if entry field is empty
            searchWord[i] = str(fields[i].get())
            if searchWord[i] == '': # Convert empty entry fields into None
                searchWord[i] = None
            for j, list_element in enumerate(data_list):
                data_toBeInspected = list(list_element.values())[i]
                if searchWord[i] != None: # Search for matches only if search word was entered in corresponding entry field
                    for value in data_toBeInspected:
                        #if str.lower(value) == str.lower(searchWord[i]):  # Neglect upper-case letters
                        if str.lower(searchWord[i]) in str.lower(value):  # Neglect upper-case letters
                            if list_element not in matches_field: # make sure an element gets not added multiple times to the matches
                                matches_field.append(list_element) # in case of a match, add the name + repos + programming skills of the member to the matches
            matches[i] = matches_field 
    
    # Until now, only the matches for the entry of one field were found. Now find the common matches of all fields
    matches_overAllFields = get_commonElementsOfLists(matches, searchWord)
    
    matches_overAllFields_string = convert_ListIntoStringEnumeration(matches_overAllFields)
    resultField.delete(1.0,tk.END) # clear the result field (from results of previous searches)
    resultField.insert(tk.INSERT, matches_overAllFields_string) # add the matches to the result text field in the tkinter-window
 

'''
Description: Function for filtering multiple lists for common matches. Here 

Output: a list, in which an element is a dict for each member containing his/her name, repos and programming languages

Params:
- list_of_lists: a list (e.g. A) containing multiple lists (e.g. 1,2,3). In each list (1,2,3,) it's looked for matches with the "search word". E.g.: list_of_lists = [list1, list2, list3]
- searchWord: list with the same number of lists (containing only 1 element) as in "list_of_lists" For 3 lists in "list_of_lists" there are 3 search words for each list. E.g. searchWord = [search word for list1, search word for list2, search word for list3]
'''    
def get_commonElementsOfLists(list_of_lists, searchWord):

  result_matches = []
  
  matches_previousIteration = []
  for i, list in enumerate(list_of_lists):
    matches_currentIteration = []

    # First iteration (with non-empty list)
    if (searchWord[i] != None):
      
      if (i == 0) or ((len(matches_previousIteration) == 0) and (searchWord[i-1] == None)):
        matches_currentIteration.extend(list)
      # Other iterations
      else:
        for element in matches_previousIteration:
          if element in list:
            matches_currentIteration.append(element)

      matches_previousIteration = matches_currentIteration

    # Last iteration (last list): save result in case last list is empty but other are not
    if i == (len(list_of_lists)-1):
      result_matches = matches_previousIteration

  return result_matches                  


'''
Description: Function for converting a list into an enumeration of type string, where each element gets one bullet point.
-------------------------------------------------------------------------------------------------------------------------
Example: 
Converting the list

--> [{'Member name': ['danielschleindlsperger'], 'Repos': ['adventofcode2020', 'adventofcode2021', 'adventofcode2022', 'adventofcode2023', 'adventofjs2021', 'atobtoa', 'Auth', 'aws-learninger', 'clj-shorty', 'crockpot', 'daniel.schleindlsperger.de', 'dav-hut-planner', 'eccspense-manager-clojure', 'eli5-scraper', 'lebenslauf', 'liftoff', 'mini-react-ssr', 'ov-movies', 'patch-day', 'react-selective-hydration', 'react-ssr-css-modules', 'rebass-styled-components-ts', 'renderless-component-test', 'RepeatAfterMe', 'sbahn-notifier', 'SingForSomeOne', 'speed-series', 'speedseries', 'spotify-playlist-organizr', 'storybook-component-library'], 'Programming languages': ['CSS', 'Clojure', 'Dockerfile', 'Emacs Lisp', 'HTML', 'Java', 'JavaScript', 'PHP', 'PLpgSQL', 'Python', 'Scheme', 'Shell', 'TypeScript', 'Vue']}]

to

--> - Name: ['danielschleindlsperger']
      Repos: ['adventofcode2020', 'adventofcode2021', 'adventofcode2022', 'adventofcode2023', 'adve
              ntofjs2021', 'atobtoa', 'Auth', 'aws-learninger', 'clj-shorty', 'crockpot', 'daniel.sc
              hleindlsperger.de', 'dav-hut-planner', 'eccspense-manager-clojure', 'eli5-scraper', 'l
              ebenslauf', 'liftoff', 'mini-react-ssr', 'ov-movies', 'patch-day', 'react-selective-hy
              dration', 'react-ssr-css-modules', 'rebass-styled-components-ts', 'renderless-componen
              t-test', 'RepeatAfterMe', 'sbahn-notifier', 'SingForSomeOne', 'speed-series', 'speedse
              ries', 'spotify-playlist-organizr', 'storybook-component-library']
      Programming languages: ['CSS', 'Clojure', 'Dockerfile', 'Emacs Lisp', 'HTML', 'Java', 'JavaSc
                              ript', 'PHP', 'PLpgSQL', 'Python', 'Scheme', 'Shell', 'TypeScript', 'V
                              ue']
.
-------------------------------------------------------------------------------------------------------------------------
Output: a string with separate new lines for the name, the repos and the programming languages of the member

Params:
- list: list to be converted
'''    
def convert_ListIntoStringEnumeration(list):
    linewidth_limit_languages = 70
    linewidth_limit_repos = linewidth_limit_languages + (len('Programming languages') - len('Repos'))
    string = ''
    for element in list:
        # Name
        string = string + '- Name: ' + str(element['Member name']) + '\n' 
      
        # Repos
        if len(str(element['Repos'])) < linewidth_limit_repos:
            string = string + ' Repos: ' + str(element['Repos']) + '\n' 
        else: # create linebreaks
            string_repo_len = len(str(element['Repos']))
            string = string + '  Repos: ' + str(element['Repos'])[0:linewidth_limit_repos] + '\n'
            num_loops = int(np.ceil(string_repo_len / linewidth_limit_repos))
            for i in range(1, num_loops):
                if i < num_loops-1:
                    string = string + '          ' + str(element['Repos'])[(i*linewidth_limit_repos):((i+1)*linewidth_limit_repos)] + '\n'
                elif i == num_loops-1:
                    string = string + '          ' + str(element['Repos'])[(i*linewidth_limit_repos):] + '\n'
            
        # Programming languages
        if len(str(element['Programming languages'])) < linewidth_limit_languages:
             string = string + '  Programming languages: ' + str(element['Programming languages']) + '\n'*2 
        else: # create linebreaks
            string_repo_len = len(str(element['Programming languages']))
            string = string + '  Programming languages: ' + str(element['Programming languages'])[0:linewidth_limit_languages] + '\n'
            num_loops = int(np.ceil(string_repo_len / linewidth_limit_languages))
            for i in range(1, num_loops):
                if i < num_loops-1:
                    string = string + '                          ' + str(element['Programming languages'])[(i*linewidth_limit_languages):((i+1)*linewidth_limit_languages)] + '\n'
                elif i == num_loops-1:
                    string = string + '                          ' + str(element['Programming languages'])[(i*linewidth_limit_languages):] + '\n'*2
        
    return string






if __name__ == "__main__":
    print('\n')
    print('-'*20)
    print('*** NEW RUN ***')
    print('-'*20)

    codecentric_membersData = get_memberData('https://api.github.com/orgs/codecentric/members', github_username, github_token)
    print(codecentric_membersData) # For understandibility and plausibility-check: show the whole collected member data of Codecentric AG

    tkWindow = create_tkWindow('Developer Search', codecentric_membersData)
    tkWindow.mainloop()
