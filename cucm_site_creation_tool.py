"""Template script, using the zeep library

This is a template file to make getting started easier.
Copy this file and the creds.py file into your project and start making calls to CUCM.

This was copied from the axlZeep.py file from the DevNet AXL examples
https://github.com/CiscoDevNet/axl-python-zeep-samples


Install Python 3.7
On Windows, choose the option to add to PATH environment variable

If this is a fresh installation, update pip (you may need to use `pip3` on Linux or Mac)

    $ python -m pip install --upgrade pip

Script Dependencies:
    lxml        # Installed when you install zeep
    requests    # Installed when you install zeep
    zeep

Dependency Installation:

    $ pip install zeep

This will install automatically all of zeep dependencies, including lxml, requests

Copyright (c) 2018 Cisco and/or its affiliates.
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import json

from lxml import etree
from requests import Session
from requests.auth import HTTPBasicAuth

from zeep import Client, Settings, Plugin
from zeep.transports import Transport
from zeep.cache import SqliteCache
from zeep.exceptions import Fault

from pathlib import Path

# The WSDL is a local file
WSDL_FILE = 'schema/AXLAPI.wsdl'

# Configure CUCM location and AXL credentials in creds.py
import creds

# Change to true to enable output of request/response headers and XML
DEBUG = False

# If you have a pem file certificate for CUCM, uncomment and define it here

# CERT = 'some.pem'

# These values should work with a DevNet sandbox
# You may need to change them if you are working with your own CUCM server

# If you're not using a certificate, this is how to supress insecure connection warnings
SUPRESS_INSECURE_CONNECTION_WARNINGS = True

if SUPRESS_INSECURE_CONNECTION_WARNINGS:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# This class lets you view the incoming and outgoing http headers and/or XML
class MyLoggingPlugin(Plugin):

    def egress(self, envelope, http_headers, operation, binding_options):

        # Format the request body as pretty printed XML
        xml = etree.tostring(envelope, pretty_print=True, encoding='unicode')

        print(f'\nRequest\n-------\nHeaders:\n{http_headers}\n\nBody:\n{xml}')

    def ingress(self, envelope, http_headers, operation):

        # Format the response body as pretty printed XML
        xml = etree.tostring(envelope, pretty_print=True, encoding='unicode')

        print(f'\nResponse\n-------\nHeaders:\n{http_headers}\n\nBody:\n{xml}')


session = Session()

# We avoid certificate verification by default, but you can uncomment and set
# your certificate here, and comment out the False setting

# session.verify = CERT
session.verify = False
session.auth = HTTPBasicAuth(creds.USERNAME, creds.PASSWORD)

# Create a Zeep transport and set a reasonable timeout value
transport = Transport(session=session, timeout=10)

# strict=False is not always necessary, but it allows zeep to parse imperfect XML
settings = Settings(strict=False, xml_huge_tree=True)

# If debug output is requested, add the MyLoggingPlugin callback
plugin = [MyLoggingPlugin()] if DEBUG else []

# Create the Zeep client with the specified settings
client = Client(WSDL_FILE, settings=settings, transport=transport,
                plugins=plugin)

# service = client.create_service("{http://www.cisco.com/AXLAPIService/}AXLAPIBinding", CUCM_URL)
service = client.create_service('{http://www.cisco.com/AXLAPIService/}AXLAPIBinding',
                                'https://{cucm}:8443/axl/'.format(cucm=creds.CUCM_ADDRESS))


search_all_names = {
    # The percent sign is a mulit-character wildcard in the CUCM searchCriteria parameters
    'name': '%'
}                       # The question mark (not shown) is a single character wild card

# The ZEEP library will return all parameters
# But you have to define which ones you want data for otherwise all you'll get are None values
# in the return data when using the list methods.
list_attributes_to_return = {
    'name': ''
}

################################################################################
#                   Read in site data configuration 
################################################################################
#file_name = input("Input the exact file to read from the `site_configurations` folder: ")
file_name = 'new_site.json'
data_file = Path(f'site_configurations/{file_name}')

if not data_file.exists():
    print(f'The file `{data_file}` does not exist in the "site_configurations" folder')
    exit(1)

with open(data_file) as df:
    file_data = df.read()
    site_data = json.loads(file_data)

################################################################################
#                   Add Locations
################################################################################
if site_data.get('location'):
    need_to_add_location = True 

    cucm_locations = service.listLocation(searchCriteria=search_all_names, returnedTags=list_attributes_to_return)

    # Checking to see if the object in the file already exists in the CUCM
    for location in cucm_locations['return']['location']:
        if site_data['location']['name'] == location['name']:
            need_to_add_location = False 

    if need_to_add_location:
        # Related Locations can cause the add to fail if it refers to itself
        # Removing the data and adding as an update after the new location is created.
        related_locations = site_data['location']['relatedLocations']
        print(site_data['location'].pop('relatedLocations'))

        response = service.addLocation(site_data['location'])
        print(f'Added the location called `{site_data["location"]["name"]}` with a UUID of {response["return"]} to CUCM')

        response = service.updateLocation(name=site_data['location']['name'], relatedLocations=related_locations)
        print(f'Updated the location called `{site_data["location"]["name"]}` with the data for Related Locations')

    else:
        print(f'The location `{site_data["location"]["name"]}` already existed in the CUCM so was not added.')

################################################################################
#                   Add SRST
################################################################################
if site_data.get('srst'):
    need_to_add_location = True 

    srst_entries = service.listSrst(searchCriteria=search_all_names, returnedTags=list_attributes_to_return)
    
    # Checking to see if the object in the file already exists in the CUCM
    for srst in srst_entries['return']['srst']:
        if site_data['srst']['name'] == srst['name']:
            need_to_add_location = False 

    if need_to_add_location:
        response = service.addSrst(site_data['srst'])
        print(f'Added the SRST reference called `{site_data["srst"]["name"]}` with a UUID of {response["return"]} to CUCM')

    else:
        print(f'The SRST reference `{site_data["srst"]["name"]}` already existed in the CUCM so was not added.')

################################################################################
#                   Add Regions
################################################################################
if site_data.get('region'):
    need_to_add_location = True 

    region_entries = service.listRegion(searchCriteria=search_all_names, returnedTags=list_attributes_to_return)
    
    # Checking to see if the object in the file already exists in the CUCM
    for region in region_entries['return']['region']:
        if site_data['region']['name'] == region['name']:
            need_to_add_location = False 

    if need_to_add_location:
        response = service.addRegion(site_data['region'])
        print(f'Added the Region called `{site_data["region"]["name"]}` with a UUID of {response["return"]} to CUCM')

    else:
        print(f'The Region named `{site_data["srst"]["name"]}` already existed in the CUCM so was not added.')

################################################################################
#                   Add Media Resource List
################################################################################


################################################################################
#                   Add Call Manager Group
################################################################################

################################################################################
#                   Add Date Time Group
################################################################################

################################################################################
#                   Add Device Pool
################################################################################

