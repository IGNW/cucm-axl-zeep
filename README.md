# Details on Using Python/Zeep with CUCM AXL API
This repo contains details on how to use Python/Zeep along
with the CUCM AXL SOAP API to make Administering the CUCM easier.

Ths repo contains the following information
- Information on installing Python and Zeep
- Information on Installing, Configuring, and working with SOAP UI
- Details on how each of the major category of API Calls works 
- Some sample programs that 


# Getting Started

## Install Core Software and Libraries
- Install Python3
- Install required Python3 libraries


# Sample Programs
## AXL API Explorer Commandline Tool
Scenario: You want to develop Python Scripts, but it's difficult to know what data / datastructures are needed.  This tool can help.

Command Line Tool for easily querying the get and list methods of CUCM to better understand the CUCM API
(I think i can do this, wouldn't need SOAPUI if i can do this)

## Data Exporter Use Cases
### Create Custom CSV Reports by pulling data from the CUCM AXL API
Scenario: The standard reports from the CUCM exporter don't have all the data you need in the right order.  You end up having to export multiple tables and merge them together.  Use a python script to automate this process.



## Standardizing Existing Deployments
### Tool to add Jabber Devices to existing users
Scenario: You are rolling out Jabber to all your existing users.  They are currently set up with only a phone.  Using python you can enable Jabber for the user, build all missing devices (CSF, TCT, TAB) and configure all the settings for each user.

### Update the Line Text Label on all lines to match a new standard
Scenario: Your company wants to update the line text label on all the phones to be their extensin plus last name.  Use python to query each phone for their assigned userid, pull the primary extension from that user and use that to create and update the line text label for each phone in the CUCM.





# Understanding how the tools work
Optional - if I have time or Cisco wants this

## Python and Zeep and the CUCM AXL API

### Get Methods

### Add Methods

### List Methods
##### Listing all data
##### Wildcard Searching

### Update Methods

### Remove Methods
