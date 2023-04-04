from utils import *
import requests

name_dataset = preprocess_data()
# print(type(name_dataset))
# print(name_dataset)

name_list = names_dataset_create(name_dataset)
# print(name_list)

while(True):
    name_to_find = input("Enter a name to Start : ")
    temp = name_to_find
    names_present = {}
    names_present[name_to_find] = ""
    # print(names_present)
    name_to_find = name_to_find.title()
    name_to_find = name_to_find.split()
    name_to_find = "_".join(name_to_find)
    r = requests.get(f'https://en.wikipedia.org/wiki/{name_to_find}', verify=False)
    response_str = str(r)
    if(response_str == "<Response [404]>"):
        print("Invalid name entered / Wikipedia page not found for the entered name.")
    else:
        names_present_new = name_extract(name_list, name_to_find, names_present, temp)
        birthdates = generate_demographics(names_present_new)
        generate_graph(names_present_new, birthdates)
        break
