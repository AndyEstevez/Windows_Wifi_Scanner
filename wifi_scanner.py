import subprocess
import re
from colorama import Fore, Style, init
from tabulate import tabulate
from IPython.display import display

import matplotlib.pyplot as plt

output = subprocess.check_output(['netsh', 'wlan', 'show', 'networks', 'mode=bssid'])

# decode
data = output.decode('utf-8').split('\n')

# regex for the netsh output
ssid_pattern = re.compile(r'\ASSID\s+\d+\s+:\s+(.*)')
authentication_pattern = re.compile(r'Authentication\s+:\s+(.+)')

bssid_pattern = re.compile(r'BSSID\s+\d+\s+:\s+([0-9a-fA-F:]{17})')
signal_pattern = re.compile(r"Signal +: (\d+)%")
wifi_standard_pattern = re.compile(r'Radio type\s*:\s*(.+)')
band_pattern = re.compile(r'Band\s*:\s*(.+)')
channel_pattern = re.compile(r'Channel\s*:\s*(\d+)')

wifi_networks = []
current_network = {}
total_bssids, total_signal_strengths, total_standards, total_bands, total_channels = []

for line in data: # extract data from output into list
    ssid_match = ssid_pattern.match(line)
    authentication_match = authentication_pattern.search(line)

    bssid_match = bssid_pattern.search(line)
    signal_match = signal_pattern.search(line)
    wifi_standard_match = wifi_standard_pattern.search(line)
    band_match = band_pattern.search(line)
    channel_match = channel_pattern.search(line)

    if ssid_match and (ssid_match.group(1).strip()) != '':
        # add network to list after new SSID appears before creating new network item
        if current_network:
            current_network['BSSID'] = total_bssids
            current_network['Signal Strength'] = total_signal_strengths
            current_network['Wi-Fi Standard'] = total_standards
            current_network['Band'] = total_bands
            current_network['Channel'] = total_channels
            total_bssids, total_signal_strengths, total_standards, total_bands, total_channels = []

            wifi_networks.append(current_network)
        # create current network with SSID
        current_network = {"SSID": ssid_match.group(1).strip(), "Authentication": "", "BSSID": "", "Signal Strength": "", "Wi-Fi Standard": "", "Band": "", "Channel": ""}
    elif authentication_match:
        current_network['Authentication'] = authentication_match.group(1).strip()
    elif bssid_match:
        total_bssids.append(bssid_match.group(1).strip()) 
    elif signal_match: 
        total_signal_strengths.append(signal_match.group(1).strip() + '%')
    elif wifi_standard_match:
        total_standards.append(wifi_standard_match.group(1).strip())
    elif band_match:
        total_bands.append(band_match.group(1).strip())
    elif channel_match:
        total_channels.append(channel_match.group(1).strip())

if current_network:
    current_network['BSSID'] = total_bssids
    current_network['Signal Strength'] = total_signal_strengths
    current_network['Wi-Fi Standard'] = total_standards
    current_network['Band'] = total_bands
    current_network['Channel'] = total_channels
    wifi_networks.append(current_network)


init(autoreset=True)
wifi_data = []
headers = "SSID Authentication BSSID Signal Wi-Fi_Strength Wi-Fi_Standard Band Channel".split()
color = Fore.GREEN
signal_color = Fore.GREEN

for w in wifi_networks: # create new data from list to have visual for wifi & new rows for each BSSID
    if w['Authentication'] == 'WPA3-Personal' or w['Authentication'] == 'WPA3-Enterprise': # print green
        color = (Fore.GREEN)
    elif w['Authentication'] == 'WPA2-Personal' or w['Authentication'] == 'WPA2-Enterprise': # print yellow
        color = (Fore.YELLOW)
    else: # print red
        color = (Fore.RED)

    if len(w['BSSID']) > 1: # check for multiple BSSID
        for i in range(0, len(w['BSSID'])):            
            sig_val = (w['Signal Strength'][i].split("%"))
            if int(sig_val[0]) > 69:
                val = (f"[=========]" + color)
                signal_color = Fore.GREEN
            elif int(sig_val[0]) > 39:
                val = (f"[======---]" + color)
                signal_color = Fore.YELLOW
            else:
                val = (f"[===------]" + color)
                signal_color = Fore.RED
            wifi_data.append([w['SSID'], f"{color}{w['Authentication']}{Style.RESET_ALL}", 
                              w['BSSID'][i], f"{signal_color}{w['Signal Strength'][i]}", f"{val}{Style.RESET_ALL}", w['Wi-Fi Standard'][i], w['Band'][i], w['Channel'][i]])
    else: # only 1 BSSID exists
        sig_val = (w['Signal Strength'][0].split("%"))
        if int(sig_val[0]) > 69:
            val = (f"[=========]" + color)
            signal_color = Fore.GREEN
        elif int(sig_val[0]) > 39:
            val = (f"[======---]" + color)
            signal_color = Fore.YELLOW
        else:
            val = (f"[===------]" + color)
            signal_color = Fore.RED
        wifi_data.append([w['SSID'], f"{color}{w['Authentication']}{Style.RESET_ALL}", 
                          w['BSSID'][0], f"{signal_color}{w['Signal Strength'][0]}", f"{val}{Style.RESET_ALL}", w['Wi-Fi Standard'][0], w['Band'][0], w['Channel'][0]])

# create grid table of wifi network data
display(tabulate(wifi_data, headers=headers, tablefmt='grid'))

# graph for Authentication, Wi-Fi Standard
# Pie chart for wifi standard
standard_data = {'802.11a': 0, '802.11n': 0, '802.11ac': 0, '802.11ax': 0, '802.11be': 0}
for x in wifi_data:
    if(x[5] == '802.11a'):
        standard_data['802.11a'] += 1
    elif(x[5] == '802.11n'):
        standard_data['802.11n'] += 1
    elif(x[5] == '802.11ac'):
        standard_data['802.11ac'] += 1
    elif(x[5] == '802.11ax'):
        standard_data['802.11ax'] += 1
    elif(x[5] == '802.11be'):
        standard_data['802.11be'] += 1
    else:
        print(x[5])
        
plt.title('Wi-Fi Standard')
plt.pie(standard_data.values(), labels=standard_data.keys(), autopct='%1.1f%%')
plt.legend(standard_data.keys(), loc="center left")
plt.show()

# bar graph for authentication
auth_data = {'WPA3' : 0, 'WPA2': 0, 'Open': 0}
for x in wifi_data:
    if 'WPA3' in x[1]:
        auth_data['WPA3'] += 1
    elif 'WPA2' in x[1]:
        auth_data['WPA2'] += 1
    elif 'Open' in x[1]:
        auth_data['Open'] += 1
    else:
        print(x[1])

sorted_auth_data = dict(sorted(auth_data.items(), key=lambda item: item[1]))
labels = list(sorted_auth_data.keys())
data = list(sorted_auth_data.values())

plt.figure(figsize=(10,5))
plt.bar(labels, data)
plt.xlabel('Authentication')
plt.ylabel('Total')
plt.title('Local Wifi Authentication')
plt.show()