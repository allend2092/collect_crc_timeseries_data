# collect_crc_timeseries_data
connect to each esxi host and get crc statistics

This script takes a file ouputted from anoter script I wrote called get_esxi_vmnics.py
you can find that script here: https://github.com/allend2092/get_vmnic_data/blob/main/get_esxi_vmnics.py
Run that script and put the output in the same directory as this script.
This script will poll every ESXi host and each associated vmnic for its crc error data.
