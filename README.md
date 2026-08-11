# Overview
MTD Dump of Nokia G-240W-F GPON ONT

>[!NOTE]
>You can find the dump within [Releases Tab](https://github.com/ButterWatt/G240WF-Dump/releases), also dump tool [here](https://github.com/ButterWatt/G240WF-Dump/blob/main/UART-Dump-Tool.py)
>
>UART Dump tool's cons: requires 3rd-party python plugin `pyserial` (painful to setup if you are not familiar with terminal), dumping process takes too much time (can take up to 10 hours), less reliable than programmers like CH341A.
# License
This repository is licensed under GNU General Public License version 3 (GNU GPLv3), take a look at [GNU Website](https://www.gnu.org/licenses/gpl-3.0.html) or this [repo's license](https://github.com/ButterWatt/G240WF-Dump/blob/main/LICENSE). *Meh, you didn't read the license*
>[!Warning]
>This repository is created for EDUCATION PURPOSES only, using this repo for "unethical activities" is considered as *war crime* (that's on you). *Read twice before you do anything stupid enough to summon hell beneath your basement*
# Partition Table
    PARTITION |   SIZE   | ERASESIZE | DEFINITION     |                                            PARTITION INFO

      mtd0      00040000   00020000    bootloader       LZMA, P: 0x5D, D: 8388608, U: 185792, H: 0x10000

      mtd1      00040000   00020000    romfile          N/A
  
      mtd2      00300000   00020000    kernel           LZMA, P: 0x5D, D: 8388608, U: 6624768, H: 0x100
      
      mtd3      001f0000   00020000    rootfs           Squashfs LZMA, LE, version 4.0, S: 15788044, I: 1798, B: 131072, T: 2017-08-11 09:32:58

      mtd4      00300000   00020000    kernel_slave     LZMA, P: 0x5D, D: 8388608, U: 6624768, H: 0x100

      mtd5      001f0000   00020000    rootfs_slave     Squashfs LZMA, LE, version 4.0, S: 15788044, I: 1798, B: 131072, T: 2017-08-11 09:32:58
      
      mtd6      00300000   00020000    kernel_oflt      LZMA, P: 0x5D, D: 8388608, U: 6624768, H: 0x100
    
      mtd7      00c00000   00020000    rootfs_oflt      Squashfs LZMA, LE, version 4.0, S: 7344015, I: 851, B: 131072, T: 2017-08-11 09:19:01
      
      mtd8      00800000   00020000    config           UBI erase count header, version: 1, EC: 0x46D, VID header offset: 0x800, data offset: 0x1000
    
      mtd9      00c00000   00020000    log              UBI erase count header, version: 1, EC: 0x1, VID header offset: 0x800, data offset: 0x1000, H: 0x0 /
                                                        UBIFS filesystem master node, Highest I: 27523, commit number: 148241 to 148274, start H: 0x21000
                                                        
      mtd10     00600000   00020000    extfs            N/A
    
      mtd11     00040000   00020000    bosa             N/A
    
      mtd12     00040000   00020000    flag             N/A
    
      mtd13     00040000   00020000    flagback         N/A

      mtd14     00040000   00020000    ri               N/A

      mtd15     00040000   00020000    riback           N/A
    
    P: PROPERTIES | D: DICTIONARY SIZE (byte) | U: UNCOMPRESSED (byte) | S: SIZE (byte) | B: BLOCKSIZE (byte) | I: INODE
    
    H: HEXDECIMAL | A: IMAGE ID | T: TIMESTAMP | C: CHECKSUM | LE: LITTLE ENDIAN | BE: BIG ENDIAN
# NAND Table
    START ADDRESS    |     END ADDRESS   |    PARTITION NAME
    0x000000000000       0x000000040000        bootloader
    0x000000040000       0x000000080000        romfile
    0x000000080000       0x000000380000        kernel
    0x000000380000       0x000002280000        rootfs
    0x000002280000       0x000002580000        kernel_slave
    0x000002580000       0x000004480000        rootfs_slave
    0x000004480000       0x000004780000        kernel_oflt
    0x000004780000       0x000005380000        rootfs_oflt
    0x000005380000       0x000005b80000        config
    0x000005b80000       0x000006780000        log
    0x000006780000       0x000006d80000        extfs
    0x000006d80000       0x000006dc0000        bosa
    0x000006dc0000       0x000006e00000        flag
    0x000006e00000       0x000006e40000        flagback
    0x000006e40000       0x000006e80000        ri
    0x000006e80000       0x000006ec0000        riback
# Device Information
Model: `G-240W-F`

Storage: `Macronix MXIC MX35LF1GE4AB-Z4I SPI NAND 128MB 1Gbit`

Memory: `Winbond W632GG6MB-12 256MB 128M*16-bit DDR3 2Gbit`

WiFi: `Mediatek MT7592N`

SoC: `EcoNet EN7526GT` (Note: *evolution of EN751221 family, same toolchain*)

Landline: `Microchip LE9652PQC`

Default telnet/UART credentials: `ONTUSER:SUGAR2A041`

(*Nevermind why NAND Table so weird, that's classic Symbian mind applied to GPON ONT systems*)
# UART log
You can find device's bootlog [here](https://github.com/ButterWatt/G240WF-Dump/blob/main/UART-log) and UART shell log [here](https://github.com/ButterWatt/G240WF-Dump/blob/main/UART-shell-log)
# Dive In U-boot - Instruction
 - Find device's SPI NAND
 - Short Pin 4 (GND) to Pin 6 (SCLK) of the SPI NAND when `BMT & BBT Init Success` shows up
 - Press a key if terminal shows `Press any key in 3 secs to enter boot command mode.`
 - If the terminal shows `bldr> `, you're in. Restart the process in case something else appears.
# Enable shell - Instruction
 - Find device's SPI NAND
 - Short Pin 4 (GND) to Pin 6 (SCLK) of the SPI NAND for a brief moment when `BMT & BBT Init Success` shows up
 - Wait for boot command prompt to timeout (*Please, do not press any keys at this point or it will enter u-boot*)
 - If you see `OperatorID` is blank, you're in, you should be able to see device's operation logs. Retry in case `OperatorID` shows your ISP's or your region.
# Device's U-boot Available Commands
    ?                                   Print out help messages.
    help                                Print out help messages.
    ritool                              Print or edit device parameters (get/set/dump)
    reset                               Perform CPU reset
    serial disable                      Disable serial
    go                                  Booting the linux kernel.
    memrl <addr>                        Read a word from addr.<addr, hex remove 0x>
    memwl <addr> <value>                Write a word to addr.<addr, hex remove 0x>
    dump <addr> <len>                   Dump memory content.<addr, hex remove 0x>
    jump <addr>                         Jump to addr.
    flash <dst> <src> <len> <oob>       Write to flash from src to dst(oob: write nand oob if 1).
    imginfo                             Show images info.
    nandit <addr>                       Write to flash from src to dst.
    nandrd <src> <len>                  Read flash from src.
    nander <dst> <len> <oob>            Erase flash from dst(oob: force erase oob if 1).
    chkmem <nand> <ddr> <len>           Check data between nand and ddr.
    innand <dst> <src> <len>            Move data from spi to nand.
    bdstore <flash dst> <bin src>       Do backdoor config store
    bdshow                              Show backdoor config
    bdswitch[1|0]                       Enable or disable backdoor function
    ddrcalswitch[1|0]                   Enable or disable ddr calibration funciton
    drambistswitch[0|1|2]               disable or enable, and quick or normal test
    xmdm <addr> <len>                   Xmodem receive to addr.
    miir <phyaddr> <reg>                Read ethernet phy reg.
    miiw <phyaddr> <reg> <value>        Write ethernet phy reg.
    cpufreq <freq num> / <m> <n>        Set CPU Freq <156~450>(freq has to be multiple of 6)
    ipaddr <ip addr>                    Change modem's IP.
    httpd                               Start Web Server
    ddrdrv <..>                         Change DDR driving length
    mtd                                 Print NAND partition start/end addresses
>[!IMPORTANT]
>`nandrd` buffer is 0x1000 = 4096 bytes, going above will crash U-boot
>
>`xmdm` *only* receive file, not send.
>
>Do not touch any critical commands like `cpufreq`, `nandit` or `flash` if you are **NOT CERTAIN** what you're about to do.
> (*Make sure you have a programmer to reflash if something goes wrong while using critical commands*)

>[!CAUTION]
>`ritool` is the **MOST CRITICAL** command, I'd like to warn you that **PRINT IT AND BACK IT UP** before writing anything, avoid irreversable damages

# SHA-512 Checksum
G240WF-Dump-Untested.bin `ae43281e2a15c9fe1bdba1e18d9bdce7e13ee3bc013ace752a3032193a51834f5779a1bda3ca47d74c8f7a4b7a0998002519d5e4068053076096516b0c7a85a3`

G240WF-MTD-Dump.zip `fcb31746ba48c88b4dec419b0d5336eb78c20c4fce80c1ac1a7a4b06cc016d1ea8f467fab907b4719ae4d8b19bfae708a79004fe768e73e8f17cb66fd258beca`
