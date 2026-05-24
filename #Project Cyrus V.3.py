#Cyrus Project V.3
import math
import json
import pandas as pd
import collections
from collections import Counter
#Set weigh
urg_weigh = 1
imp_weigh = 1
eff_weigh = 1
additional_plan = []
'''************************************************************************'''
#CYRUS V.1 Part
#FUNCTION PART
''' |
    |
    |
    V'''
#preventing error for memory part
def load_memory():
    try:
        with open("Cyrus_memory.json", "r") as f:
            data = json.load(f)
    except:
        # file missing / empty / corrupted
        data = {
    "tasks": [],
    "plans": []
        }  
    return data
memory = load_memory()
tasks = memory["tasks"]
plans = memory["plans"]

#Pattern recognition via Count collections
def countingpatterns():
    with open("Cyrus_memory.json", "r") as f:
        data = json.load(f)
    tasks = data["tasks"]
    urgencycounter = [task["urgency"] for task in tasks]
    importancecounter = [task["importance"] for task in tasks]
    effortcounter = [task["effort"] for task in tasks]
    timecounter = [task["time"] for task in tasks]
    urgencypattern = Counter(urgencycounter)
    importancepattern = Counter(importancecounter)
    effortpattern = Counter(effortcounter)
    timepattern = Counter(timecounter)
    return (
        Counter(urgencycounter),
        Counter(importancecounter),
        Counter(effortcounter),
        Counter(timecounter)
    )

#task ID counter
def get_next_task_id(tasks):
    if not tasks:
        return 1
    return max(task["id"] for task in tasks) + 1

#time conversion --> user input hours, minutes respectively; 1 hour = 60 minutes; hour conversion to minutes + minutes
def convert_time(hour, minutes):
    return hour * 60 + minutes

#safe integer --> functioning a correct form of input. it works as an infinite loop asking a user for input. if input isn't integer, it would ask until it's valid. it converts string number to integer number
def safe_int(prompt):
    while True:
        value = input(prompt)
        if value.isdigit():
            return int(value)
        else:
            print("Please enter a valid number")

#setting the pattern recognition
def pattern(tasks):
    u = 0
    e = 0
    i = 0

    for x in tasks:
        # soft condition (not binary)
        if x["urgency"] > 6:
            u += (x["urgency"] - 6) / 4

        if x["effort"] > 6:
            e += (x["effort"] - 6) / 4

        if x["importance"] > 6:
            i += (x["importance"] - 6) / 4

    urg_boost = math.log(u + 1)
    eff_boost = math.log(e + 1)
    imp_boost = math.log(i + 1)

    return urg_boost, eff_boost, imp_boost

#setting weighs for each criteria
def calculate_weigh():
    global urg_weigh, eff_weigh, imp_weigh
    urg_weigh = 1
    eff_weigh = 1
    imp_weigh = 1
    urg_pattern, imp_pattern, eff_pattern, time_pattern = countingpatterns()
    # extract most common values (signal strength idea)
    urg_signal = sum([k * v for k, v in urg_pattern.items()])
    imp_signal = sum([k * v for k, v in imp_pattern.items()])
    eff_signal = sum([k * v for k, v in eff_pattern.items()])
    # apply learning effect
    urg_weigh += urg_signal * 0.01
    imp_weigh += imp_signal * 0.01
    eff_weigh += eff_signal * 0.01
    
#Saving additional plans (if have) into JSON file memory
def savememoryforplans(plans):
    data = load_memory()
    data["plans"] = plans   # ← replace, NOT append
    with open("Cyrus_memory.json", "w") as f:
        json.dump(data, f)

# additional plans --> weekly/monthly/yearly
def handle_plans(additional_plan):
    global urg_weigh, imp_weigh, eff_weigh  # FIX: allow global update
    additional_plan.clear()

    choice = input('Which plan? weekly/monthly/yearly: ').lower()
    while True:
        plan = input("Enter priority (type done to stop): ").lower()

        if plan == "done":
            break
        plans.append(plan)
        additional_plan.append(plan)
    savememoryforplans(plans)

    for x in additional_plan:

        if "exam" in x:
            urg_weigh += 2
            imp_weigh += 2
            eff_weigh -= 1

        elif "project" in x:
            urg_weigh += 2
            imp_weigh += 3
            eff_weigh += 1

        elif "homework" in x:
            urg_weigh += 1
            imp_weigh += 2
            eff_weigh += 1

        elif "study" in x:
            urg_weigh += 1
            imp_weigh += 1
            eff_weigh += 0.5

    if choice == "weekly":
        urg_weigh *= 1.6
        imp_weigh *= 1.2

    elif choice == "monthly":
        urg_weigh *= 1.2
        imp_weigh *= 1.1

    elif choice == "yearly":
        urg_weigh *= 0.7

    return urg_weigh, imp_weigh, eff_weigh

#Saving tasks info into JSON memory file
def savememoryfortasks(tasks):
    data = load_memory()
    data["tasks"] = tasks
    with open("Cyrus_memory.json", "w") as f:
        json.dump(data, f)
             
#add tasks --> users add tasks and control when to stop by input "done"; task creation: create structured object (dictionary) and adds to the database (list); task ID + 1
def add_tasks(tasks):
    global task_id_counter
    while True:
        print("\n--- Add Task ---")
        name = input("Enter your task (or type 'done' to stop): ")

        if name.lower() == "done":
            break
        importance = safe_int("How important it is? Rank 1-10: ")
        effort = safe_int("How much effort does it take? Rank 1-10: ")
        urgency = safe_int("How urgent it is? Rank 1-10: ")
        hour = safe_int("How many hours would it take? ")
        minutes = safe_int("How many minutes would it take? ")
        time = convert_time(hour, minutes)
        task = {
            "id": task_id_counter,
            "name": name,
            "importance": importance,
            "effort": effort,
            "urgency": urgency,
            "time": time
        }
        tasks.append(task)
        task_id_counter += 1
        savememoryfortasks(tasks)
        print("Task added successfully!")

#show tasks --> loop through the "tasks" list and y represents each dictionary in the task. y["key"] is used to access the value associated with that key.
def show_tasks(tasks):
    for y in tasks:
        print(
            "ID:", y["id"],
            "| Name:", y["name"],
            "| Importance:", y["importance"],
            "| Effort:", y["effort"],
            "| Urgency:", y["urgency"],
            "| Time:", y["time"]
        )

#delete tasks --> loop through the task and find the correct task (task_id ) based on input and remove that exact task
def delete_tasks(tasks, task_id):
    for task in tasks:
        if task["id"] == task_id:
            tasks.remove(task)
            savememoryfortasks(tasks)            
            return
    print("Task ID not found")

#edit tasks --> locates the task (if input not in fields, still continue) --> enter the field's number that you want to change --> type the new thing you want to change --> 
def edit_tasks(tasks, task_id):
    for task in tasks:
        if task["id"] == task_id:
            while True:
                print("\nWhat do you want to edit?")
                print("1. name")
                print("2. importance")
                print("3. effort")
                print("4. urgency")
                print("5. time")
                print("6. done")
                choice = input("Choose field: ")
                fields = {
                    "1": "name",
                    "2": "importance",
                    "3": "effort",
                    "4": "urgency",
                    "5": "time"
                }
                if choice == "6":
                    break
                if choice not in fields:
                    print("Invalid choice")
                    continue
                field = fields[choice]
                if field == "name":
                    task[field] = input("New value: ")
                elif field == "time":
                    hour = safe_int("Hours: ")
                    minutes = safe_int("Minutes: ")
                    task[field] = convert_time(hour, minutes)
                else:
                    task[field] = safe_int("New value: ")
                savememoryfortasks(tasks)
            return
    print("Task ID not found")

#CYRUS V.2 Part
#Functions
#X --> Overall score
def scoringsystem():
    for x in tasks:
        x["score"] = (
            x["importance"] * imp_weigh +
            x["urgency"] * urg_weigh -
            x["effort"] * eff_weigh -
            (x["time"] / 60)
        )

#Sort total scorings in descending order to find the greatest score
def sorting():
    tasks.sort(key=lambda x: x["score"], reverse=True)

#finish tasks
def finish(ranked_tasks):
    num = safe_int('Type task number to finish: ')
    if num < 1 or num > len(ranked_tasks):
        print("Invalid number")
        return
    task = ranked_tasks[num - 1]
    tasks.remove(task)
    savememoryfortasks(tasks)

#Pandas for structuring the data
def structuring():
    df = pd.DataFrame(tasks)
    

#ID Generator --> starts at 1 and increases every time the task was added

task_id_counter = get_next_task_id(tasks)


'''**************************************************************'''

#EXECUTION PART
''' |
    |
    |
    V'''
    
while True:
    menu = input('add/show/delete/edit/next:  \nif you have additional plans or any speicifc change in your schedule, type  "plans" , we will figure out the best choice for you: \nview history/delete history: ')
    menu = menu.strip().lower()
    if menu == "add":
        add_tasks(tasks)

    elif menu == "show":
        show_tasks(tasks)

    elif menu == "delete":
        task_id = safe_int("Enter task ID: ")
        delete_tasks(tasks, task_id)
        
    elif menu == "edit":
        task_id = safe_int("Task ID: ")
        edit_tasks(tasks, task_id)

    elif menu == "plans":
        weights = handle_plans(additional_plan)
        urg_weigh = weights[0]
        imp_weigh = weights[1]
        eff_weigh = weights[2]

    elif menu == "next":
        if not tasks:
            print("No tasks found. Try adding tasks using 'add'.")
        else:
            structuring()
            calculate_weigh()      # uses patterns INSIDE
            scoringsystem()
            ranked_tasks = sorted(tasks, key=lambda x: x["score"], reverse=True)

            rank = 1
            for i in ranked_tasks:
                print(rank, i["name"])
                rank += 1

    elif menu == "finished":
        if not tasks:
            print("No tasks found.")
        else:
            pattern(tasks)
            calculate_weigh()
            scoringsystem()
            sorting()
            ranked_tasks = tasks.copy()
            rank = 1
            for i in ranked_tasks:
                print(rank, i["name"])
                rank += 1

            finish(ranked_tasks)
        
    elif menu == "exit":
        break

    else:
        print("Error")

