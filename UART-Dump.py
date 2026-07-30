import serial
import time
import re

# === SERIAL PORT CONFIG ===
PORT = 'COM3'         # Replace your COM port (eg: /dev/ttyUSB0)
BAUD = 115200
OUTPUT_FILE = 'mtd2.bin'
PROMPT = "bldr>"     # U-Boot Standard Promp

# === DUMP ADDR (0x PREFIX IS NOT REQUIRED) ===
# Example   Dump 1MB       : START = "0", END = "100000"
#           Dump All 128MB : START = "0", END = "8000000"
START_ADDR_HEX = "80000"
END_ADDR_HEX   = "2a85f4"

BLOCK_SIZE = 0x1000        # 4096 bytes (1k hex)

def hex_str_to_int(hex_str):
    clean_hex = hex_str.strip().lower().replace("0x", "")
    return int(clean_hex, 16)

def send_and_receive(ser, cmd):
    ser.reset_input_buffer()
    # ONLY SEND \r (Carriage Return)
    ser.write((cmd + '\r').encode('utf-8'))
    
    output = ""
    start_time = time.time()
    
    while True:
        if ser.in_waiting > 0:
            data = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
            output += data
            if PROMPT in output:
                break
        
        if time.time() - start_time > 4: # TIMEOUT 4S
            break
            
        time.sleep(0.01)
        
    return output

def read_block_with_retry(ser, offset_str, max_retries=3):
    cmd = f"nandrd {offset_str} 1000"
    
    for attempt in range(1, max_retries + 1):
        raw_response = send_and_receive(ser, cmd)
        
        # SPLIT HEX DATA
        lines = raw_response.splitlines()
        payload_lines = [l for l in lines if not l.startswith("nandrd") and PROMPT not in l]
        clean_text = " ".join(payload_lines)
        
        hex_bytes = re.findall(r'\b[0-9a-fA-F]{2}\b', clean_text)
        binary_data = bytes([int(b, 16) for b in hex_bytes])
        
        if len(binary_data) > 0:
            return binary_data
        
        time.sleep(0.1)
        ser.reset_input_buffer()
        
    return b''

def main():
    start_addr = hex_str_to_int(START_ADDR_HEX)
    end_addr = hex_str_to_int(END_ADDR_HEX)
    
    if start_addr >= end_addr:
        print("[!] ERROR: START ADDR MUST SMALLER THAN END ADDR!")
        return

    # CALCULATE BLOCK
    total_bytes = end_addr - start_addr
    total_blocks = (total_bytes + BLOCK_SIZE - 1) // BLOCK_SIZE

    print(f"[*] CONNECTING TO {PORT} ({BAUD})...")
    ser = serial.Serial(PORT, BAUD, timeout=1)
    
    print("=" * 60)
    print(f"[*] DUMP ADDRESSES  : 0x{start_addr:X} -> 0x{end_addr:X}")
    print(f"[*] TOTAL CAP.      : {total_bytes} bytes (~{total_bytes/1024/1024:.2f} MB)")
    print(f"[*] TOTAL BLOCK     : {total_blocks} (0x1000 bytes each)")
    print("=" * 60)
    
    # WARM-UP
    ser.write(b'\r')
    time.sleep(0.3)
    send_and_receive(ser, "nandrd 0 1000")
    
    with open(OUTPUT_FILE, 'wb') as f_out:
        for i in range(total_blocks):
            current_offset = start_addr + (i * BLOCK_SIZE)
            offset_str = f"{current_offset:X}"
            
            binary_data = read_block_with_retry(ser, offset_str)
            
            if len(binary_data) == 0:
                print(f"\n[!] SKIPPED BLOCK AT OFFSET {offset_str}")
            
            f_out.write(binary_data)
            
            # PRINT PROGRESS
            progress = ((i + 1) / total_blocks) * 100
            print(f"\r[*] Progress: {progress:.2f}% | Block: {i+1}/{total_blocks} | Current Offset: 0x{offset_str} | Recv: {len(binary_data)}B", end='')

    print(f"\n\n[+] COMPLETED! SAVED TO {OUTPUT_FILE}")
    ser.close()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as e:
        print(f"\n[!] Keyboard Interupted, Abort")