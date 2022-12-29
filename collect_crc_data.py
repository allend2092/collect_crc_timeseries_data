# This script takes a file ouputted from anoter script I wrote called get_esxi_vmnics.py
# you can find that script here: https://github.com/allend2092/get_vmnic_data/blob/main/get_esxi_vmnics.py
# Run that script and put the output in the same directory as this script.
#
# This script will poll every ESXi host and each associated vmnic for its crc error data.


import datetime
from netmiko import ConnectHandler
import json
import time
import pandas as pd

# Define a function to retrieve the CRC counter output
def get_crc_errors(hostname, username, password, nic):
    # Define the device details
    device = {
        'device_type': 'generic',
        'ip': hostname,
        'username': username,
        'password': password,
    }

    # Connect to the device using Netmiko
    conn = ConnectHandler(**device)

    # Send the esxcli command to retrieve the CRC counter output
    output = conn.send_command(f"esxcli network nic stats get -n={nic} | grep 'Receive CRC errors'")

    # Parse the output to extract the data
    data = output.strip().split()
    errors = int(data[-1])

    # Disconnect from the device
    conn.disconnect()

    return errors


# Define a function to parse the input JSON file and extract the list of ESXi servers and physical nics.
# Open the input file and read the contents
with open('vmnic_data.json', 'r') as f:
    data = f.read()

# Parse the JSON data
json_data = json.loads(data)

# Create an empty dataframe to store the data
df = pd.DataFrame()

# Iterate over the list of servers
for server in json_data:
    hostname = server['hostname']
    nics = server['vmnic_names']
    print(f'Processing server {hostname} with nics {nics}')


# Define a function to establish an SSH connection to an ESXi server and execute a command to retrieve
# the CRC counter output.
# esxi command is "esxcli network nic stats get -n=vmnicx | grep 'Receive CRC errors'"
# Iterate over the list of servers
for server in json_data:
    hostname = server['hostname']
    username = 'root'  # Replace with your username
    password = 'password'  # Replace with your password
    nics = server['vmnic_names']
    for nic in nics:
        # Try connecting to the host
        try:
            errors = get_crc_errors(hostname, username, password, nic)
        except Exception as e:
            # If there is an exception, handle it here
            print(f'Failed to connect to {hostname}: {e}')
            # You can add a column to the dataframe to indicate that the host was not reachable
            data = pd.DataFrame({'hostname': hostname, 'nic': nic, 'errors': 'NA', 'reachable': False}, index=[0])
        else:
            # If there is no exception, handle the data here
            print(f'There have been {errors} CRC errors on {nic} on server {hostname}')
            data = pd.DataFrame({'hostname': hostname, 'nic': nic, 'errors': errors, 'reachable': True}, index=[0])
        # Append the data to the dataframe
        df = pd.concat([df, data], ignore_index=True)

# Print the dataframe
print(df)

# Convert the dataframe to a list of dictionaries
json_vmnic_errors = df.to_dict('records')

# Get the current timestamp
timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

# Print the JSON object
print(json.dumps(json_vmnic_errors, indent=4, sort_keys=True))

filename = f'vmnic_errors_{timestamp}.json'

# Pretty-print the JSON object
json_vmnic_errors_pretty = json.dumps(json_vmnic_errors, indent=4, sort_keys=True)

# Write the data to a JSON file in a pretty-printed format
with open(filename, "w") as f:
    f.write(json_vmnic_errors_pretty)

# Print a message to confirm that the file has been written
print(f'Data written to file {filename}')
