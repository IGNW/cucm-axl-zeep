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
## Data Exporter Use Cases
### Export Device Pool (site) and related objects to a JSON file
`cucm_site_data_extraction_tool.py`
Enter a Device Pool name and export data from that object to a JSON file.  This export file is the file format
for all the rest of the export tools.

You can take the names in the output and modify them.  This give a way to export data, modify, and quickly
import it back into the CUCM.

NOTE: This program does not export all the data for a site, but enough to give you an idea of how to build out a
full site export tool for your needs.


### Deploy a site based on a JSON file input
`cucm_site_creation_tool.py`
Input the name of a json file in the `site_configurations` folder.  Then will build out the objects
in CUCM based on the settings in the file.

You can use the output of the Site Extraction Tool and modify that to create a new site in the CUCM.

NOTE: This program does not build all the objects required to deploy a site, but gives you enough information
to customize the tool for your uses.


### Remove a site based on a JSON file input
`cucm_site_removal_tool.py`
Input the name of a json file in the `site_configurations` folder.  Then you can remove all the objects
from CUCM that are also in the JSON file.

You can use the output of the Site Extraction Tool or the JSON file used for the site creation tool to remove a site.

NOTE: If an object is used by another object, it will likely error out.  But if the CUCM allows the 
delete operation, then it won't.  Be careful using this tool against a production system.

The tool will check if the object exists before attempting to build it.  If it does, it will not.


### Convert an export to a Jinja2 Template to quickly and easily make lots of site config files
`create_config_from_template.py`
If you have to create numerious sites from an export, use Jinja2 to create the files quickly and
consistently.


### Create Custom CSV Reports by pulling data from the CUCM AXL API
Scenario: The standard reports from the CUCM exporter don't have all the data you need in the right order.  You end up having to export multiple tables and merge them together.  Use a python script to automate this process.
Tool #2 - TBD


## Standardizing Existing Deployments
### Tool to add Jabber Devices to existing users
Scenario: You are rolling out Jabber to all your existing users.  They are currently set up with only a phone.  Using python you can enable Jabber for the user, build all missing devices (CSF, TCT, TAB) and configure all the settings for each user.
#3

### Update the Line Text Label on all lines to match a new standard
Scenario: Your company wants to update the line text label on all the phones to be their extensin plus last name.  Use python to query each phone for their assigned userid, pull the primary extension from that user and use that to create and update the line text label for each phone in the CUCM.
#4




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
