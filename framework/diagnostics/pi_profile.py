import os
import platform
import psutil
import pygame

def get_pi_profile():
    # Detect Hardware/OS
    os_info = platform.platform()
    cpu_info = platform.processor()
    
    # Memory
    mem = psutil.virtual_memory()
    total_mem_gb = mem.total / (1024**3)
    
    # Framebuffer (stubbed check)
    fb_exists = os.path.exists("/dev/fb0")
    
    print(f"--- Pi Profile Diagnostic Report ---")
    print(f"OS: {os_info}")
    print(f"CPU: {cpu_info}")
    print(f"Total RAM: {total_mem_gb:.2f} GB")
    print(f"Framebuffer (/dev/fb0): {'Detected' if fb_exists else 'Not Detected'}")
    
    return {
        "os": os_info,
        "ram_gb": total_mem_gb,
        "fb_available": fb_exists
    }

if __name__ == "__main__":
    get_pi_profile()
