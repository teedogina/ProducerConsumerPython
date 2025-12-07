import threading
import queue
import time
import socket
import random
from classdef import generate_random_student, wrap_student_to_xml, XML_FILE_COUNT

# Creates XML Files

class Producer(threading.Thread):
   
    def __init__(self, buffer):
        super().__init__()
        self.buffer = buffer
        self.running = True

    def run(self):
        print(f"[PRODUCER] Starting up. Will create {XML_FILE_COUNT} XML files.")
        for i in range(1, XML_FILE_COUNT + 1):
            if not self.running:
                break
                
            # 1. Generate and Wrap Data
            student = generate_random_student()
            file_name = wrap_student_to_xml(student, i)
            
            # 2. Insert File Number into Buffer 
            self.buffer.put(i)
            print(f"[PRODUCER] Produced data for ID {student.student_id}. Inserted file number '{i}' into buffer. ({file_name})")
            
        
            time.sleep(random.uniform(0.5, 1.5)) 

        self.buffer.put(0) 
        print("[PRODUCER] Finished producing all files and sent termination signal (0).")
        
    def stop(self):
        self.running = False


# 2. Client Socket

def client_socket_main(buffer_queue, host='127.0.0.1', port=65432):
 
    
    print("[CLIENT] Waiting for Producer to generate initial files...")
    time.sleep(2) 
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            print(f"[CLIENT] Connected to server at {host}:{port}.")
            
            while True:
                # Get File Number from Queue
                # Use block=True to wait until an item is available
                file_number = buffer_queue.get(block=True) 

                if file_number == 0:
                    
                    message = "EXIT" 
                    s.sendall(message.encode('utf-8'))
                    print("[CLIENT] Sent EXIT signal to Server and shutting down.")
                    buffer_queue.task_done()
                    break

               
                message = str(file_number)
                s.sendall(message.encode('utf-8'))
                print(f"[CLIENT] Sent file number '{file_number}' to Server.")
                
                #  acknowledgement
                data = s.recv(1024)
                if data.decode('utf-8') == "ACK":
                    print(f"[CLIENT] Received ACK for file number {file_number}.")
                
                buffer_queue.task_done()
                
    except ConnectionRefusedError:
        print("\n[ERROR] Connection refused. Ensure consumer_server.py is running first!")
    except Exception as e:
        print(f"[ERROR] Client connection error: {e}")


# Execution

if __name__ == '__main__':
    
    shared_buffer = queue.Queue(maxsize=10) 
    
    #  Producer thread
    producer_thread = Producer(shared_buffer)
    producer_thread.start()
    
    client_socket_main(shared_buffer)

    producer_thread.join()
    
    print("[SYSTEM] Producer and Client finished.")