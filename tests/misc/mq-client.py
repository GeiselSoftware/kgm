import posix_ipc

# Define the same queue name as the server
QUEUE_NAME = "/my_ipc_queue"

# Open the existing message queue
mq = posix_ipc.MessageQueue(QUEUE_NAME)

try:
    for i in range(5):
        # Send a message to the server
        message = f"Message {i + 1}"
        mq.send(message, priority=1)  # Set priority as needed
        print(f"Sent: {message}")
        
        # Wait for a response
        response, priority = mq.receive()
        print(f"Received response: {response.decode()} with priority {priority}")
finally:
    # Close the queue
    mq.close()
