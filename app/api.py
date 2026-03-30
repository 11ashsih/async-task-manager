import asyncio
from app.service import create_task, list_task, mark_complete, delete_task
from app.models import TaskCreate

async def menu():
    while True:
        print("\n1. Create Task \n2. List Tasks \n 3. Complete Task \n4. Delete Task \n5. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            title = input(" Enter task title")
            task = await create_task(TaskCreate(title=title))
            print(f"Task created:{task}")

        elif choice == "2":
            task = await list_task() 
            for t in task:
                print(t)

        elif choice == "3":
            task_id = input("Enter task ID: ")
            task = await mark_complete(task_id)
            print(f"Updated Task: {task}")

        elif choice == "4":
            task_id = input("Enter task ID")
            task = await delete_task(task_id)
            print(f"Deleted Task: {task}")

        elif choice == "5":
            break

        else:
            print("Invalid choice")

async def run():
    await menu()
