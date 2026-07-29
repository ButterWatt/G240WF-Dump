# Overview
MTD Dump of Nokia G-240W-F GPON ONT
# License
This repository is licensed under GNU General Public License version 3 (GNU GPLv3), take a look at [GNU Website](https://www.gnu.org/licenses/gpl-3.0.html) or this [repo's license](https://github.com/ButterWatt/G240WF-Dump/blob/main/LICENSE). *Meh, you didn't read the license*
# Partition Table
*Not Available*
# NAND Table
    START ADDRESS    |     END ADDRESS   |    PARTITION NAME
      0x00000000           0x00040000         bootloader
      0x00040000           0x00080000         romfile
      0x00080000           0x002a85f4         kernel
      0x002a85f4           0x011b85f4         rootfs
      0x00080000           0x01080000         tclinux
      0x01080000           0x1af46dfa         kernel_slave
      0x1af46dfa           0xd0746dfa         rootfs_slave
      0x01080000           0x02080000         tclinux_slave
      0x05480000           0x054a0000         yaffs
      0x06e40000           0x07000000         reservearea
# Device Information
Model: `G-240W-F`

Storage: `Macronix MXIC MX35LF1GE4AB-Z4I SPI NAND 128MB 1Gbit`

Memory: `Winbond W632GG6MB-12 256MB 128M*16-bit DDR3 2Gbit`

WiFi: `Mediatek MT7592N`

SoC: `EcoNet EN7526GT` (Note: *evolution of EN751221 family, same toolchain*)

Landline: `Microchip LE9652PQC`
# UART log
You can find device's bootlog [here](https://github.com/ButterWatt/G240WF-Dump/blob/main/UART-log)
# Dive In U-boot - Instruction
 - Find device's SPI NAND
 - Short Pin 4 (GND) to Pin 6 (SCLK) of the SPI NAND when `BMT & BBT Init Success` shows up
 - Press a key if terminal shows `Press any key in 3 secs to enter boot command mode.`
 - If the terminal shows `bldr> `, you're in. Restart the process in case something else appears.
# Device's U-boot Available Commands
    ?                                   Print out help messages.
    help                                Print out help messages.
    ritool                              ritool.
    reset                               board reset
    serial disable                      serial disable
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
>[!NOTE]
>`nandrd` buffer is 0x1000 = 4096 bytes, going above will crash U-boot
>
>`xmdm` *only* receive file, not send.
