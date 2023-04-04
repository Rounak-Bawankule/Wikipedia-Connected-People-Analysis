import pandas as pd
import requests
from bs4 import *
from py2neo import Graph, Node, Relationship
import os
# from ethnicolr import pred_census_name

def preprocess_data():
    dataset = pd.read_csv("./dataset/people_wiki.csv")
    # print(dataset.head)   
    name_df = dataset['name']
    name_df = name_df.to_frame()
    
    return name_df

def names_dataset_create(name_dataset):
    name_list = name_dataset['name'].tolist()
    name_data = []
    for i in name_list:
        name_data.append(i.lower())    
    return name_data 

def name_extract(name_list, find_name, names_present, temp_name):
    # print(len(name_list))
    # print("in function")
    try:
        url = f'https://en.wikipedia.org/wiki/{find_name}'
        r = requests.get(url, verify=False)
        soup = BeautifulSoup(r.text,'html.parser').select('body')[0]
        text = []
        for tag in soup.find_all():
             if tag.name=="p":
                text.append(tag.text)
                # print(text)
        wiki_data = " ".join(text)
        wiki_data = wiki_data.lower()
        temp_list = []
        for i in name_list:
            if i in wiki_data:
                # print(count)
                if(i in names_present):
                    pass
                else:
                    print(i)
                    t = i.title()
                    t = t.split()
                    t = "_".join(t)
                    url = f'https://en.wikipedia.org/wiki/{t}'
                    r1 = requests.get(url, verify=False)
                    response_str = str(r1)
                    if(response_str == "<Response [404]>"):
                        print("delete")
                        pass
                    else:
                        print("listlist")
                        temp_list.append(i)

                names_present[temp_name] = temp_list


    except:
        print("Can't fetch data from web due to SSL certifiate error. Fetching Data from local database...")
        path =f"./wiki_data/{find_name}.txt"
        file_names =  os.listdir("./wiki_data/")
        # print(file_names)
        if f'{find_name}.txt' in file_names:
            with open (path, "r", encoding="utf8") as f:
                print("file opened")
                txt = f.read()
                txt = txt.lower()
                # print(txt)   
                count = 0
                temp_list = []
                for i in name_list:
                    # print("in for loop")
                    # count = count + 1   
                    # print(i)
                    if i in txt:
                        # print(count)
                        if(i in names_present):
                            pass
                        else:
                            print(i)
                            temp_list.append(i)
                        # print(temp_list)
                        names_present[temp_name] = temp_list

    print(names_present)
    return names_present


def generate_demographics(names_present):
    birthdates = {}
    for k,v in names_present.items():
        try:
            url = f'https://en.wikipedia.org/wiki/{k}'
            r = requests.get(url, verify=False)
            soup = BeautifulSoup(r.text,'html.parser').select('body')[0] 
            bdate = soup.find(class_ = "bday")
            print(bdate.text)
            # birthdates[k] = ""
            birthdates[k] = f"{bdate.text}"
        except:
            print("Birthdate not found.")
            # birthdates[k] = ""
            birthdates[k] = "Birth Date not found."
        for item in v:
            try:
                url = f'https://en.wikipedia.org/wiki/{item}'
                r = requests.get(url, verify=False)
                soup = BeautifulSoup(r.text,'html.parser').select('body')[0] 
                bdate = soup.find(class_ = "bday")
                print(bdate.text)
                # birthdates[item] = ""
                birthdates[item] = f"{bdate.text}"
            except:
                print("Birthdate not found.")
                # birthdates[item] = ""
                birthdates[item] = "Birth Date not found."
        
        print(birthdates)
        return birthdates



def generate_graph(names_present, birthdates):
    # Connect to the Neo4j database
    graph = Graph("neo4j://localhost:7687", auth=("neo4j", "123123123"))
    graph.run("MATCH (n) DETACH DELETE n")
    # other_person_node = []
    rel = "Related To"
    for key, values in names_present.items():
    # Create a node for a person
        person_node = Node("Person", name=key)
        person_node["Birth Date"] = birthdates[key]
        path = key.title()
        path = path.split()
        path = "_".join(path)
        person_node["More About Them"] = f"https://en.wikipedia.org/wiki/{path}"
        # person_node["Nationality"] = f"{key.pre}"
        for i in values:
            other_person_node = Node("Person", name=i)
            other_person_node["Birth Date"] = birthdates[i]
            path1 = i.title()
            path1 = path1.split()
            path1 = "_".join(path1)
            other_person_node["More About Them"] = f"https://en.wikipedia.org/wiki/{path1}"
    # Create a relationship between two people
            relationship = Relationship(person_node, f"{rel}", other_person_node)
            graph.create(relationship)

    # Add the nodes and relationship to the graph
    graph.create(person_node)

    