# !/usr/bin/env python3

# UART Dump Tool by Butter Watt
# Revision 1.0 - Release under GNU General Public License v3.0 (GPLv3)
# Github: ButterWatt/G240WF-Dump

import time, re, platform
try:
    import serial
except ModuleNotFoundError:
    print("\r[!] Module not found, please install \"Pyserial\" or exit restricted Instance before running this program.")
    exit()

# GLOBAL CONFIGURATION
devport = "COM3"       # SERIAL PORT (CHANGE IF NEEDED)
outputbin = "dump.bin" # OUTPUT FILE NAME
start = "0"            # START ADDRESS
end = "8000000"        # END ADDRESS

# WARNING: THE TWO ADDRESSES ABOVE MUST BE MULTIPLES OF 1000, OTHERWISE THE SCRIPT WILL NOT WORK PROPERLY. (e.g., 0x1000, 0x2000, 0x3000, etc.)

# U-BOOT DEVICE CONFIGURATION / MODIFY ONLY WHEN ABSOLUTELY NECESSARY (just adjust in case of hand cramps, ensure no dump if prompt or baudrate is off)
prompt = "bldr>"
baudrate = 115200

def governorCheck():
    if platform.system() not in ("Linux"):
        return
    host = platform.machine().lower()
    governorPath = "/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor"
    if host not in ("armv7l", "armhf"):
        return
    try:
        with open(governorPath) as path:
            governor = path.read().strip()
    except OSError:
        return
    raise RuntimeError(f"\n[!] CPU Governor of this ARM device is {governor}, please switch to 'performance' mode before running the script.") if governor != "performance" else print(f"\n[~] CPU Governor of this ARM device is {governor}, continuing.")

def hextoint(string):
    return int(string.strip().lower().replace("0x", ""), 16)

def communicate(dserial, cmd):
    dserial.reset_input_buffer()
    dserial.write((cmd + '\r').encode('utf-8'))

    output = ""
    startTime = time.time()

    while True:
        if dserial.in_waiting > 0:
            output += dserial.read(dserial.in_waiting).decode('utf-8', errors="ignore")
            if prompt in output: break
        if time.time() - startTime > 3: break
        time.sleep(0.01)
    return output

def serialRead(dserial, offset, attempts=3):
    cmd = f"nandrd {offset} 1000"
    for run in range(1, attempts + 1):
        rawResp = communicate(dserial, cmd)
        lines = rawResp.splitlines()
        payload = [line for line in lines if not line.startswith("nandrd") and prompt not in line]
        cleanPayload = " ".join(payload)
        hexdecimal = re.findall(r'\b[0-9a-fA-F]{2}\b', cleanPayload)
        binary = bytes(int(b, 16) for b in hexdecimal)
        if len(binary) == 4096:
            return binary
        time.sleep(0.1)
        dserial.reset_input_buffer()
    raise RuntimeError(f"Offset 0x{offset} does not return data after {attempts} attempts")

def main():
    governorCheck()
    startTime = time.asctime()
    startAddr = hextoint(start)
    endAddr = hextoint(end)
    if startAddr >= endAddr:
        print("\r[!] Start address cannot be greater than or equal to end address. Stopping.")
        return
    totalBytes = endAddr - startAddr
    totalBlocks = (totalBytes + 0x1000 - 1) // 0x1000

    print(f"[~] Connecting to {devport} at {baudrate}", end="")
    time.sleep(1)
    dserial = serial.Serial(devport, baudrate, timeout=1)
    try:
        print(f"\r[~] Connected to {devport} at {baudrate}\n")
        print(f"[~] Dump Address: 0x{startAddr:X} -> 0x{endAddr:X}")
        print(f"[~] Predicted Size: {totalBytes} bytes (~{totalBytes/1024/1024:.2f} MB), {totalBlocks} Blocks (4096 bytes/block)")
        print(f"[~] Estimated Time: {totalBlocks*(1.5/3600):.1f} hours")
        print(f"[~] Make sure both devices connected properly.\n[!] Script does not guarantee correct file structure.\n")
        print("[~] Warming up", end="")
        dserial.write(b'\r')
        time.sleep(1)
        communicate(dserial, "nandrd 0 1000")
        print("\r[-] Waiting for device responses", end="")
        with open(outputbin, 'wb') as out:
            for i in range(totalBlocks):
                curOffset = startAddr + (i * 0x1000)
                offString = f"{curOffset:X}"
                binary = serialRead(dserial, offset=offString)
                out.write(binary)
                progress = ((i + 1) / totalBlocks) * 100
                print(f"\r[>] Progress: {progress:.2f}% | Block: {i + 1}/{totalBlocks} | Offset: 0x{offString}" + " " * 5, end="")
            print(f"\r[~] Dump process completed. Please check the file to ensure it contains {totalBytes/1024/1024:.1f} MB.")
    finally:
        dserial.close()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\r[!] Ctrl-C pressed. Stopping program." + " " * 10)
    except Exception as exc:
        print(f"\r[!] An error occurred. Stopping. ({exc})" + " " * 5)
