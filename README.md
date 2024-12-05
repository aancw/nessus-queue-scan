# nessus-queue-scan
A tool to automate Nessus scan scheduling, allowing pentesters to queue scans without the hassle of manually creating schedules. Simply define scan details, and the tool will automatically launch the next scan once the previous one finishes, preventing any overlap.

## Requirements
- requests
- selenium
- python-dotenv
- chromedriver

## How To

You’ll need Selenium and ChromeDriver(search guide on how to install by yourself) to run this tool, as well as some environment variables like your Nessus API key (Admin > My Account > API Key > Generate) and login credentials. The tool will first list all available scan information, and you can then select which scan(s) to manage by entering their comma-separated IDs. Once chosen, you can leave the rest to the tool, and check back later to see if the scan is finished. I'm a bit lazy to implement a notifier for when the scan is complete—maybe I’ll add that in a future update!

## Usage
```
% python nessus-queue-scan.py
Listing available scan information...
ID: 36, Name: test6, Status: completed
ID: 34, Name: test5, Status: completed
ID: 31, Name: test3, Status: completed
ID: 27, Name: test3, Status: completed
ID: 24, Name: test2, Status: completed
ID: 22, Name: test1, Status: completed
ID: 40, Name: test8, Status: empty
ID: 42, Name: test9, Status: empty
Enter the IDs of scans to monitor (comma-separated): 40,42
Checking status of Scan ID 40...
Launching scan for id 40
Scan ID 40 is Running. Closing the browser.
Checking status of Scan ID 40...
Scan with ID 40 is completed.
Scan with ID 40 is completed. Moving to next scan...
Checking status of Scan ID 42...
Launching scan for id 42
Scan ID 42 is Running. Closing the browser.
Checking status of Scan ID 42...
Scan with ID 42 is completed.
Scan with ID 42 is completed. Moving to next scan...
All selected scans have been checked.
```

## PoC
 <img src="https://s7.gifyu.com/images/SJxGY.gif?raw=true" width="200px" height="200px"/>

## Motivation

When pentesting large networks, I got tired of manually setting up scan schedules and figuring out the right timing for each scan to finish. Instead of dealing with that, I just want to create scan details by slicing the large network into smaller parts. 

For example, if I have 1000 IPs to scan, I’ll split it into batches of 100 IPs per scan. The tool will automatically launch each scan as soon as the previous one finishes, ensuring no overlap and a smooth process. 

This tool uses the Nessus Professional API to retrieve scan data and then simulates the scan launch using Selenium. Since the Nessus Professional API doesn’t support creating or launching scans, nor does it allow queuing scans to run sequentially after one finishes, I built this tool specifically for my own needs. If you find it useful, I’m really proud it could help you too!

## License

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
