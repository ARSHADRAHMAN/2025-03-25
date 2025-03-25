from flask import Flask, jsonify, request
import datetime
import asyncio

app = Flask(__name__)

tasks = [
    {'id': 1, 'title': 'Green', 'completed': False, 'due_date': '2024-03-20'},
    {'id': 2, 'title': 'Blue', 'completed': False, 'due_date': '2024-03-21'}
]

next_task_id = 3  # Initialize this globally to avoid reference errors

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    return jsonify(tasks)

@app.route('/api/tasks', methods=['POST'])
def create_task():
    global next_task_id  # Declare next_task_id as global

    data = request.get_json()
    
    new_task = {
        'id': next_task_id,  # Assign a unique ID
        'title': data['title'],
        'completed': False,
        'due_date': data.get('due_date') or datetime.date.today().strftime("%Y-%m-%d")
    }

    next_task_id += 1  # Increment for the next task
    tasks.append(new_task)
    
    return jsonify(new_task), 201

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json()
    
    for task in tasks:
        if task['id'] == task_id:
            task.update(data)  # Update task attributes
            asyncio.create_task(send_notification(task_id))  # Run asynchronously
            return jsonify(task), 200

    return jsonify({'error': 'Task not found'}), 404

async def send_notification(task_id):
    """
    send notification when task status is updated.
    """
    await asyncio.sleep(2)  # Simulate some work (e.g., sending email)
    print(f"Notification sent for task {task_id}")

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    global tasks
    tasks = [task for task in tasks if task['id'] != task_id]
    
    if any(task['id'] == task_id for task in tasks):
        return jsonify({'message': 'Task deleted'}), 204
    
    return jsonify({'error': 'Task not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)  # Set the port correctly

# RxJS Integration (Conceptual): Imagine that the frontend of this application uses RxJS to handle updates. Describe how you would design the backend API to provide updates to the frontend using a stream of events (e.g., using Server-Sent Events or WebSockets). Explain the key concepts and technologies you would use. (You don't need to implement the frontend part for this exercise).
# Solution 1:
# 1. For bidirectional or full duplex communication i will go with web socket 
# 2. If the application requires only server-to-client updates (e.g., live notifications, status updates), SSE is a simpler and more lightweight choice.

# Design: 
# 1. Usign FastAPI + Uvicorn, i will create /event endpoint
# 2. I will create event generator function and it will return streaming json response
# 3. for pub/sub, i will use azure service bus topic to publish the events
# 4. using /event endpoint, i will get streaming response and using observable i will update it on UI.

#  +-----------+        +---------------------+        +---------------------------+  
#  | Frontend  | -----> | Backend SSE Server  | -----> | Azure Service Bus Topic   |
#  | (RxJS)    |        | (FastAPI + Uvicorn) |        | (Pub/Sub for event relay) |
#  +-----------+        +---------------------+        +---------------------------+  

# Simple Design: considering SSE 
# I will create a backend endpoint, i.e  Get to get the task status. Response will be in json format.
# Using RxJS, axion or fetch i will hit the get api and display the necesary information 