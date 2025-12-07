import threading
import queue
import time
import socket
import random
from classdef import unwrap_xml_to_student, student_to_html  


# Consumer Thread

class Consumer(threading.Thread):
    
    def __init__(self, buffer):
        super().__init__()
        self.buffer = buffer
        self.running = True
        self.processed_count = 0
        self.processed_data = []

    def run(self):
        print("[CONSUMER] Setting up.")
        while self.running:
            try:
                file_number = self.buffer.get(timeout=1)
            except queue.Empty:
                continue

            
            if file_number == 0:
                print("[CONSUMER] Received termination signal. Stopping.")
                self.running = False
                self.buffer.task_done()
                break

            # unwrapping
            student_obj = unwrap_xml_to_student(file_number)

            if student_obj:
                self.processed_data.append(student_obj)
                self.processed_count += 1

                
                print(f"[CONSUMER] Processed file '{file_number}':")
                print(student_obj)

                student_to_html(student_obj)

            else:
                print(f"[CONSUMER] Warning: File '{file_number}' was empty or corrupted.")

            self.buffer.task_done()
            time.sleep(random.uniform(0.7, 1.8))  

        print(f"[CONSUMER] Finished. Total processed: {self.processed_count}")

# Server Socket 


def server_socket_main(buffer_queue, host='127.0.0.1', port=65432):
    
    print(f"[SERVER] Starting up on {host}:{port}...")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print("[SERVER] Waiting for a connection...")

        conn, addr = s.accept()
        with conn:
            print(f"[SERVER] Connected by {addr}")

            while True:
                data = conn.recv(1024)
                if not data:
                    print("[SERVER] Client disconnected.")
                    break

                message = data.decode('utf-8').strip()

                if message == "EXIT":
                    print("[SERVER] Received EXIT signal. Inserting termination signal (0).")
                    buffer_queue.put(0)
                    conn.sendall("ACK".encode('utf-8'))
                    break

                try:
                    file_number = int(message)
                    buffer_queue.put(file_number)
                    print(f"[SERVER] Received file number '{file_number}'. Added to buffer.")
                    conn.sendall("ACK".encode('utf-8'))
                except ValueError:
                    print(f"[SERVER] Invalid message: '{message}'")
                    conn.sendall("NACK".encode('utf-8'))

    print("[SERVER] Socket closed. Exiting server thread.")

if __name__ == '__main__':

    shared_buffer = queue.Queue(maxsize=5)

    consumer_thread = Consumer(shared_buffer)
    consumer_thread.start()

    server_socket_main(buffer_queue=shared_buffer)

    shared_buffer.join()
    consumer_thread.join()
    
    print("\n[SYSTEM] Server and Consumer finished. Final processed students:")
    for student in consumer_thread.processed_data:
        print(student)
