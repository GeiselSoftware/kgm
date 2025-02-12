#
# docker install on ubuntu jellyfish: https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-22-04
#
# --- from https://hub.docker.com/r/clickhouse/clickhouse-server/
# run clickhouse in docker: 
# docker run -d -p 18123:8123 -p19000:9000 --name local-clickhouse-server --ulimit nofile=262144:262144 clickhouse/clickhouse-server
# docker exec -it local-clickhouse-server clickhouse-client
# > create table a (a String) engine = Log
# > select * from a
#
# pip install posix-ipc
# pip install clickhouse-connect
#

import posix_ipc
import time
import clickhouse_connect

# Define a unique name for the message queue
QUEUE_NAME = "/my_ipc_queue"

# Create a message queue
mq = posix_ipc.MessageQueue(QUEUE_NAME, posix_ipc.O_CREAT)

print("connecting to clickhouse server...")
client = clickhouse_connect.get_client(host='localhost', port=18123, username='default', password='')

print("Server is listening for messages...")

try:
    while True:
        # Receive a message from the queue
        message, priority = mq.receive()
        print(f"Received: {message.decode()} with priority {priority}")
        
        # Simulate processing
        #time.sleep(1)
        
        # Optionally send a response
        response = f"Processed: {message.decode()}"

        client.command(f"insert into a(a) values ('{message.decode()}')")
        
        mq.send(response, priority=priority)
        print(f"Sent response: {response}")
except KeyboardInterrupt:
    print("\nShutting down server...")
finally:
    # Close and unlink the queue
    mq.close()
    mq.unlink()
