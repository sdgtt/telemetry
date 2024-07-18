BOOT_PARTITION_BN_MAP = {
    "zynq-adrv9364-z7020-bob-cmos" : "zynq-adrv9364-z7020-bob-vcmos",
    "zynq-adrv9364-z7020-bob" : "zynq-adrv9364-z7020-bob-vlvds",
    "zynqmp-zcu102-rev10-ad9081-204b-txmode9-rxmode4" : "zynqmp-zcu102-rev10-ad9081-v204b-txmode9-rxmode4",
    "zynqmp-zcu102-rev10-ad9081-204c-txmode0-rxmode1" : "zynqmp-zcu102-rev10-ad9081-v204c-txmode0-rxmode1",
    "zynqmp-zcu102-rev10-ad9081" : "zynqmp-zcu102-rev10-ad9081-vm4-l8",
    "zynqmp-zcu102-rev10-ad9081-m8-l4" : "zynqmp-zcu102-rev10-ad9081-vm8-l4",
    "zynq-zed-adv7511-adrv9002-rx2tx2" : "zynq-zed-adv7511-adrv9002-rx2tx2-vcmos",
    "zynq-zed-adv7511-adrv9002" : "zynq-zed-adv7511-adrv9002-vcmos",
    "zynqmp-zcu102-rev10-adrv9002-rx2tx2" : ["zynqmp-zcu102-rev10-adrv9002-rx2tx2-vcmos","zynqmp-zcu102-rev10-adrv9002-rx2tx2-vlvds"],
    "zynqmp-zcu102-rev10-adrv9002" : ["zynqmp-zcu102-rev10-adrv9002-vcmos","zynqmp-zcu102-rev10-adrv9002-vlvds"],
    "zynqmp-adrv9009-zu11eg-revb-adrv2crr-fmc-revb-jesd204-fsm":"zynqmp-adrv9009-zu11eg-revb-adrv2crr-fmc-revb",
    "zynqmp-adrv9009-zu11eg-revb-adrv2crr-fmc-revb-sync-fmcomms8-jesd204-fsm":"zynqmp-adrv9009-zu11eg-revb-adrv2crr-fmc-revb-sync-fmcomms8",
}

def map_bp_to_th(bp_bn_name):
    '''Maps boot partition board name with the test harness board name'''
    match = None
    if bp_bn_name in BOOT_PARTITION_BN_MAP.keys():
        match = BOOT_PARTITION_BN_MAP[bp_bn_name]
    return match

def map_th_to_bp(th_bn_name):
    '''Maps test harness board name board name with the boot partition board name'''
    boot_partition_bn_th_map = dict()
    for bn, thbn in BOOT_PARTITION_BN_MAP.items():
        if type(thbn) == list:
            for thbnv in thbn:
                boot_partition_bn_th_map.update({thbnv:bn})
        else:
            boot_partition_bn_th_map.update({thbn:bn})

    match = None
    if th_bn_name in boot_partition_bn_th_map.keys():
        match = boot_partition_bn_th_map[th_bn_name]
    return match

