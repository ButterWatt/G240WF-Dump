# !/usr/bin/env python3

# UART DUMP TOOL BY BUTTERWATT
# RELEASE UNDER GNU GENERAL PUBLIC LICENSE VERSION 3

import time, re, os, platform
try: 
    import serial
except ModuleNotFoundError as e:
    print("[!] PySerial is not installed or this Instance is in restricted mode.")
    exit()
# === GENERAL CONFIGURATION ===
PORT = 'COM3'         # Replace your COM port (eg: /dev/ttyUSB0) | Thay cổng COM tương ứng
OUTPUT_FILE = 'dump.bin'

# === DUMP ADDR (0x PREFIX IS NOT REQUIRED) | ĐỊA CHỈ DUMP (KHÔNG CẦN TIỀN TỐ 0x) ===
# Example/Ví dụ          Dump 1MB       : START = "0", END = "100000"
#                        Dump 128MB     : START = "0", END = "8000000"
START_ADDR_HEX = "0"
END_ADDR_HEX   = "8000000"

# === U-BOOT CONFIGURATION ===
BAUD = 115200
PROMPT = "bldr>"           # U-Boot Standard Promp, Replace If Needed | Promp U-boot tiêu chuẩn, thay thế nếu cần
BLOCK_SIZE = 0x1000        # 4096 bytes (1k hex), going above threshold will crash U-boot | vượt quá ngưỡng sẽ gây sập U-boot

def governor_intercept():
    if platform.system() != "Linux":
        return
    host = platform.machine().lower()
    if host not in ("armv7l", "armhf"):
        return
    governor_path = "/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor"
    try:
        with open(governor_path) as path:
            governor = path.read().strip()
    except OSError:
        return
    if governor != "performance":
        print(f"\r[!] CPU Governor is set to {governor}. On {host}, it is a bottleneck and causes timing issue.")
        print("""[!] Please change your device governor to "performane" in order to continue.""")
        exit(0)
    print(f"\n[*] No issue detected with governor. Continue (Device's governor: {governor})")

def hex_str_to_int(hex_str):
    clean_hex = hex_str.strip().lower().replace("0x", "")
    return int(clean_hex, 16)

def send_and_receive(ser, cmd):
    ser.reset_input_buffer()
    # ONLY SEND \r (Carriage Return) | CHỈ GỬI \r
    ser.write((cmd + '\r').encode('utf-8'))
    
    output = ""
    start_time = time.time()
    
    while True:
        if ser.in_waiting > 0:
            data = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
            output += data
            if PROMPT in output:
                break
        
        if time.time() - start_time > 3: # TIMEOUT
            break
            
        time.sleep(0.01)
        
    return output

def read_block_with_retry(ser, offset_str, max_retries=3):
    cmd = f"nandrd {offset_str} 1000"
    
    for attempt in range(1, max_retries + 1):
        raw_response = send_and_receive(ser, cmd)
        
        # SPLIT HEX DATA | TÁCH DỮ LIỆU THẬP LỤC PHÂN
        lines = raw_response.splitlines()
        payload_lines = [l for l in lines if not l.startswith("nandrd") and PROMPT not in l]
        clean_text = " ".join(payload_lines)
        
        hex_bytes = re.findall(r'\b[0-9a-fA-F]{2}\b', clean_text)
        binary_data = bytes([int(b, 16) for b in hex_bytes])
        
        if len(binary_data) > 0:
            return binary_data
        
        time.sleep(0.1)
        ser.reset_input_buffer()
        
    raise RuntimeError(f"Offset 0x{offset_str} Did not return any data after {max_retries} attempts")

def main():
    STIME = time.asctime()
    estop = 0
    start_addr = hex_str_to_int(START_ADDR_HEX)
    end_addr = hex_str_to_int(END_ADDR_HEX)
    
    if start_addr >= end_addr:
        print("[!] ERROR: START ADDR MUST SMALLER THAN END ADDR!")
        return

    # CALCULATE BLOCK | TÍNH TOÁN KHỐI
    total_bytes = end_addr - start_addr
    total_blocks = (total_bytes + BLOCK_SIZE - 1) // BLOCK_SIZE

    print(f"[*] CONNECTING TO : {PORT} AT {BAUD}", end='')
    time.sleep(1)
    ser = serial.Serial(PORT, BAUD, timeout=1)
    print(f"\r[*] CONNECTED TO  : {PORT} AT {BAUD}")
    print("=" * 60)
    print(f"[*] DUMP ADDRESSES  : 0x{start_addr:X} -> 0x{end_addr:X}")
    print(f"[*] TOTAL CAP.      : {total_bytes} bytes (~{total_bytes/1024/1024:.2f} MB)")
    print(f"[*] TOTAL BLOCK     : {total_blocks} (0x1000 bytes each)")
    print(f"[*] START TIME      : {STIME}")
    print(f"[*] ESTIMATED TIME  : {total_blocks*1.5:.1f} s | {total_blocks*(1.5/60):.1f} m | {total_blocks*(1.5/60/60):.1f} h")
    print(f"[!] Keep both PC and GPON powered until the process completes.")
    print(f"[!] Unplugging UART cable mid-dump is a great way to corrupt your dump.")
    print("=" * 60)
    
    # WARM-UP BEFORE DUMP | LÀM NÓNG TRƯỚC KHI TIẾN HÀNH DUMP
    ser.write(b'\r')
    time.sleep(0.3)
    send_and_receive(ser, "nandrd 0 1000")
    try:
        with open(OUTPUT_FILE, 'wb') as f_out:
            for i in range(total_blocks):
                current_offset = start_addr + (i * BLOCK_SIZE)
                offset_str = f"{current_offset:X}"
                binary_data = read_block_with_retry(ser, offset_str)
                f_out.write(binary_data)
            
                # PRINT PROGRESS | IN TIẾN TRÌNH
                progress = ((i + 1) / total_blocks) * 100
                print(f"\r[*] P: {progress:.2f}% | B: {i+1}/{total_blocks} | O: 0x{offset_str}" + " "*5, end='')
        print(f"\n\n[+] COMPLETED! SAVED TO {OUTPUT_FILE} | ENDED AT {time.asctime()}")
    finally:
        ser.close()

if __name__ == "__main__":
    try:
        governor_intercept()
        main()
    except KeyboardInterrupt as e:
        print(f"\r[!] Keyboard Interupted. Abort." + " "*15)
    except serial.SerialException as e:
        print(f"\r[!] Serial Device Error. Abort. ({e})")
    except TypeError as e:
        print(f"\r[!] Unexpected Error Occurred. Abort. ({e})")
    except OSError as e:
        print(f"\r[!] UART Cable Unplugged. Abort. ({e})")
    except RuntimeError as e:
        print(f"\r[!] Error: {e}. Abort,")
