import pandas as pd
import bcrypt
import os
import hashlib
import hmac

userId = None
salt = "t1123"

#read users data from csv and create dataframe instance
def read_user_df():
    try:
        if os.path.exists("users.csv"):
            return pd.read_csv("users.csv")
        else:
            return pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()


#read task data from csv and create dataframe instance
def read_task_df():
    try:
        if os.path.exists("tasks.csv"):
            return pd.read_csv("tasks.csv")
        else:
            return pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()


user_df = read_user_df()
task_df = read_task_df()

#encrypt password using sha256
def hash_password(password: str) -> bytes:
    return hashlib.sha256((password + salt).encode()).digest()

#encrypt password using sha256
def encrypt_passw(passw:str):
    hashed = hashlib.sha256((passw + salt).encode()).digest()
    return hashed

#decrypt password and compare with store password
def decypt_passw(passw:str,hashed_passw:str):
    passw_enc = hash_password(passw)
    hashed_passw = eval(hashed_passw)
    return hmac.compare_digest(passw_enc, hashed_passw)

#get incremented user id from user dataframe (count number of users)
def get_user_id():
    if len(user_df)>0:
        user_id = user_df["id"].max()+1
        return user_id
    else:
        return 1

#get incremented task id from task dataframe (count number of tasks)
def get_task_id():
    if len(task_df)>0:
        task_id = task_df["id"].max()+1
        return task_id
    else:
        return 1


#check for in dataframe from username whether username is already exists
def check_user_exists(username:str):
    if len(user_df)>0:
        user = user_df[user_df["username"]==username]
        return len(user)>0
    else:
        return False

#add new user in dataframe in export as csv
def add_update_user(username:str,passw:str,user_id:int):
    global user_df
    user = pd.Series({"id":user_id,"username":username,"passw":passw})
    user_df = pd.concat([user_df,user.to_frame().T],ignore_index=True)
    user_df.to_csv("users.csv")
    print("User registered.")

#compare credentials and log-in user
def check_for_cred(username:str,passw:str):
    global user_df, userId
    if len(user_df)>0:
        user = user_df[user_df["username"]==username]
        if len(user)>0:
            user = user.iloc[0].to_dict()
            passw_hash = user.get("passw")
            if decypt_passw(passw,passw_hash):
                print("check_for_cred",user.get("id"))
                print("User logged in.")
                userId = user.get("id")
                return True
            else:
                return False
    else:
        print("User not found.")
        return False

#create input prompt for username and password compare whether password is matched from stored password
def login_user():
    global loggedIn
    try:
        username = input("\nEnter user name : ")
        passw = input("\nEnter password : ")
        loggedIn = check_for_cred(username,passw)
        if loggedIn:
            show_task_menu()
        else:
            print("\nInvalid usename or password\n")
            show_auth_menu()
    except Exception as e:
        print("error",e)

#logout user
def logout_user():
    global userId
    try:
        userId = None
        print("\nUser Logged out!\n")
        show_auth_menu()
    except Exception as e:
        print("error",e)
        show_auth_menu()
    
#create input prompt for username and password and add in user dataframe
def register_user():
    while True:
        try:
            username = input("\nEnter user name : ")
            passw = input("\nEnter password : ")
            if not check_user_exists(username):
                hashed_passw = str(encrypt_passw(passw))
                user_id = get_user_id()
                add_update_user(username, hashed_passw, user_id)
            else:
                print("username already exists. try another user name")
            break
        except Exception as e:
            print("Invalid option.",e)

#create input prompt for task description and insert in dataframe
def add_task():
    global userId, task_df
    try:
        if userId is not None:
            desc = input("\nEnter task description : ")
            if not desc:
                print("description is empty. try again.")
            else:
                task_id = get_task_id()
                task = pd.Series({"id":task_id,"user_id":userId,"desc":desc,"status":"Pending"})
                task_df = pd.concat([task_df,task.to_frame().T],ignore_index=True)
                task_df.to_csv("tasks.csv")
                print("Task added")
                show_task_menu()
        else:
            print("User not logged in.")
            show_auth_menu()
    except Exception as e:
        print("Error : ",e)
        show_task_menu()

#list task with task id and description
def list_task():
    global userId, task_df
    try:
        tasks = []
        if(len(task_df)>0):
            tasks = task_df[task_df["user_id"]==userId]
            print("\n")
            for i in range(len(tasks)):
                task = tasks.iloc[i].to_dict()
                print(f"Tasks : {i+1}")
                print(f"Task Id : {task.get('id')}")
                print(f"Description : {task.get('desc')}")
                print(f"Status : {task.get('status','Pending')}")
                print("\n-------------------\n")
        else:
            print("\nNo task found.")
        show_task_menu()
    except Exception as e:
        print("Error : ",e)
        show_task_menu()

#update task status (Pending to Completed)
def update_task_status():
    global task_df
    try:
        task_id = input("\nEnter the task id :")
        task_id = int(task_id)
        if type(task_id)==int:
            task = task_df[task_df["id"]==task_id]
            if len(task)>0:
                task_df.loc[task_df["id"]==task_id, "status"] = "Completed"
                task_df.to_csv("tasks.csv")
                print(f"\nTask updated!")
            else:
                print("\nNo task found!")
            show_task_menu()
        else:
            print("\ninvalid task id\n")
            update_task_status()
    except Exception as e:
        print("Error : ",e)
        show_task_menu()

#delete task from dataframe and update in csv 
def delete_task():
    global task_df
    try:
        task_id = input("\nEnter the task id :")
        task_id = int(task_id)
        if type(task_id)==int:
            task = task_df[task_df["id"]==task_id]
            if len(task)>0:
                index_to_drop = task_df.loc[task_df["id"]==task_id].index
                task_df.drop(index=index_to_drop, inplace=True)
                task_df.to_csv("tasks.csv")
                print(f"\nTask deleted!")
            else:
                print("\nNo task found!")
            show_task_menu()
        else:
            print("invalid task id\n")
            delete_task()
    except Exception as e:
        print("Error : ",e)
        show_task_menu()
    

#show task menu and take input as prompt and invoke function according to choise entered
def show_task_menu():
    while True:
        try:
            choise = input("\nChoose the options :\n1.Add Task\n2.View Tasks\n3.Mark Task as Completed\n4.Delete Task\n5.Logout\n\nEnter a number : ")
            if choise in ["1","2","3","4","5"]:
                if choise=="1":
                    add_task()
                elif choise=="2":
                    list_task()
                elif choise=="3":
                    update_task_status()
                elif choise=="4":
                    delete_task()
                elif choise=="5":
                    logout_user()
                break
            else:
                print("Invalid option. Please try again")
        except Exception as e:
            print("Error",e)

#show auth menu and take input as prompt and invoke function according to choise entered (Login --> 1, Register --> 2)
def show_auth_menu():
    while True:
        try:
            choise = input("\nChoose the options :\n1.Login\n2.Register\n\nEnter a number : ")
            if choise in ["1","2"]:
                if choise=="1":
                    login_user()
                else:
                    register_user()
                    show_auth_menu()
                break
            else:
                print("Invalid option. Please try again")
        except Exception as e:
            print("Invalid option.")

#invoke auth menu function
show_auth_menu()
