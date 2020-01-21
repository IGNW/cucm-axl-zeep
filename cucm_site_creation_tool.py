"""Template script, using the zeep library

This is a template file to make getting started easier.
Copy this file and the creds.py file into your project and start making calls to CUCM.

This was copied from the axlZeep.py file from the DevNet AXL examples
https://github.com/CiscoDevNet/axl-python-zeep-samples


Install Python 3.7
On Windows, choose the option to add to PATH environment variable

If this is a fresh installation, update pip (you may need to use `pip3` on Linux or Mac)

For Windows
    $ python -m pip install --upgrade pip

For Linux/Mac
    $ python3 -m pip install --upgrade pip

Script Dependencies:
    lxml        # Installed when you install zeep
    requests    # Installed when you install zeep
    zeep

For Windows
    $ pip install zeep

For Linux
    $ pip3 install zeep

This will install automatically all of zeep dependencies, including lxml, requests

Copyright (c) 2020 Cisco and/or its affiliates.
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

from zeep import Client, Settings, Plugin, xsd
from zeep.transports import Transport

from pathlib import Path

# The WSDL is a local file
# Using Pathlib.Path to make Windows/Unix path difference issues go away
WSDL_FILE = str(Path('schema') / 'AXLAPI.wsdl')

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
file_name = input("Input the exact file to read from the `site_configurations` folder: ")
data_file = Path('site_configurations') / f'{file_name}'

if not data_file.exists():
    print(f'The file `{data_file}` does not exist in the "site_configurations" folder')
    exit(1)
else:
    print(f'Opening `{data_file}` and reading in the contents.')

with open(data_file) as df:
    file_data = df.read()
    site_data = json.loads(file_data)

################################################################################
#                   Add Locations
################################################################################
cucm_resource_friendly_name = "Location"
cucm_resource_name = "location"

if site_data.get(cucm_resource_name):
    need_to_add_location = True

    cucm_locations = service.listLocation(searchCriteria=search_all_names, returnedTags=list_attributes_to_return)

    # Checking to see if the object in the file already exists in the CUCM
    for location in cucm_locations['return'][cucm_resource_name]:
        if site_data[cucm_resource_name]['name'] == location['name']:
            need_to_add_location = False

    if need_to_add_location:
        # Related Locations can cause the add to fail if it refers to itself
        # Removing the data and adding as an update after the new location is created.
        related_locations = site_data[cucm_resource_name]['relatedLocations']
        site_data[cucm_resource_name].pop('relatedLocations')

        # If the between locations tag is empty, tell Zeep to ignore this parameter because it's missing
        if site_data[cucm_resource_name]['betweenLocations'] is None:
            site_data[cucm_resource_name]['betweenLocations'] = xsd.SkipValue

        response = service.addLocation(site_data[cucm_resource_name])
        print(f'Added the {cucm_resource_friendly_name} called `{site_data[cucm_resource_name]["name"]}` with a UUID of {response["return"]} to CUCM')

        response = service.updateLocation(name=site_data['location']['name'], relatedLocations=related_locations)
        print(f'Updated the {cucm_resource_friendly_name} called `{site_data[cucm_resource_name]["name"]}` with the data for Related Locations')

    else:
        print(f'The {cucm_resource_friendly_name} `{site_data[cucm_resource_name]["name"]}` already existed in the CUCM so was not added.')

################################################################################
#                   Add SRST
################################################################################
cucm_resource_friendly_name = "SRST Reference"
cucm_resource_name = "srst"

if site_data.get(cucm_resource_name):
    need_to_add_location = True

    srst_entries = service.listSrst(searchCriteria=search_all_names, returnedTags=list_attributes_to_return)

    # Checking to see if the object in the file already exists in the CUCM
    for srst in srst_entries['return'][cucm_resource_name]:
        if site_data[cucm_resource_name]['name'] == srst['name']:
            need_to_add_location = False

    if need_to_add_location:
        response = service.addSrst(site_data[cucm_resource_name])
        print(f'Added the {cucm_resource_friendly_name} called `{site_data[cucm_resource_name]["name"]}` with a UUID of {response["return"]} to CUCM')

    else:
        print(f'The {cucm_resource_friendly_name} named `{site_data[cucm_resource_name]["name"]}` already existed in the CUCM so was not added.')

################################################################################
#                   Add Regions
################################################################################
cucm_resource_friendly_name = "Region"
cucm_resource_name = "region"

if site_data.get(cucm_resource_name):
    need_to_add_location = True

    region_entries = service.listRegion(searchCriteria=search_all_names, returnedTags=list_attributes_to_return)

    # Checking to see if the object in the file already exists in the CUCM
    for region in region_entries['return'][cucm_resource_name]:
        if site_data[cucm_resource_name]['name'] == region['name']:
            need_to_add_location = False

    if need_to_add_location:
        response = service.addRegion(site_data[cucm_resource_name])
        print(f'Added the {cucm_resource_friendly_name} called `{site_data[cucm_resource_name]["name"]}` with a UUID of {response["return"]} to CUCM')

    else:
        print(f'The {cucm_resource_friendly_name} named `{site_data[cucm_resource_name]["name"]}` already existed in the CUCM so was not added.')

################################################################################
#                   Add Media Resource List
################################################################################
cucm_resource_friendly_name = "Media Resource Group List"
cucm_resource_name = "mediaResourceList"

if site_data.get(cucm_resource_name):
    need_to_add_location = True

    mrgl_entries = service.listMediaResourceList(searchCriteria=search_all_names, returnedTags=list_attributes_to_return)

    # Checking to see if the object in the file already exists in the CUCM
    for mrgl in mrgl_entries['return'][cucm_resource_name]:
        if site_data[cucm_resource_name]['name'] == mrgl['name']:
            need_to_add_location = False

    if need_to_add_location:

        # You can create a MRGL without members, but Zeep requires all values to be present
        # This is how to work add an MRGL with no members
        if site_data[cucm_resource_name]['members'] is None:
            site_data[cucm_resource_name]['members'] = xsd.SkipValue

        response = service.addMediaResourceList(site_data[cucm_resource_name])
        print(f'Added the {cucm_resource_friendly_name} called `{site_data[cucm_resource_name]["name"]}` with a UUID of {response["return"]} to CUCM')

    else:
        print(f'The {cucm_resource_friendly_name} named `{site_data[cucm_resource_name]["name"]}` already existed in the CUCM so was not added.')

################################################################################
#                   Add Call Manager Group
################################################################################
cucm_resource_friendly_name = "CallManager Group"
cucm_resource_name = "callManagerGroup"

if site_data.get(cucm_resource_name):
    need_to_add_location = True

    cmg_entries = service.listCallManagerGroup(searchCriteria=search_all_names, returnedTags=list_attributes_to_return)

    # Checking to see if the object in the file already exists in the CUCM
    for cmg in cmg_entries['return'][cucm_resource_name]:
        if site_data[cucm_resource_name]['name'] == cmg['name']:
            need_to_add_location = False

    if need_to_add_location:
        response = service.addCallManagerGroup(site_data[cucm_resource_name])
        print(f'Added the {cucm_resource_friendly_name} called `{site_data[cucm_resource_name]["name"]}` with a UUID of {response["return"]} to CUCM')

    else:
        print(f'The {cucm_resource_friendly_name} named `{site_data[cucm_resource_name]["name"]}` already existed in the CUCM so was not added.')

################################################################################
#                   Add Date Time Group
################################################################################
cucm_resource_friendly_name = "Date/Time Group"
cucm_resource_name = "dateTimeGroup"

if site_data.get(cucm_resource_name):
    need_to_add_location = True

    dtg_entries = service.listDateTimeGroup(searchCriteria=search_all_names, returnedTags=list_attributes_to_return)

    # Checking to see if the object in the file already exists in the CUCM
    for dtg in dtg_entries['return'][cucm_resource_name]:
        if site_data[cucm_resource_name]['name'] == dtg['name']:
            need_to_add_location = False

    if need_to_add_location:
        response = service.addDateTimeGroup(site_data[cucm_resource_name])
        print(f'Added the {cucm_resource_friendly_name} called `{site_data[cucm_resource_name]["name"]}` with a UUID of {response["return"]} to CUCM')

    else:
        print(f'The {cucm_resource_friendly_name} named `{site_data[cucm_resource_name]["name"]}` already existed in the CUCM so was not added.')

################################################################################
#                   Add Device Pool
################################################################################
cucm_resource_friendly_name = "Device Pool"
cucm_resource_name = "devicePool"

if site_data.get(cucm_resource_name):
    need_to_add_location = True

    dp_entries = service.listDevicePool(searchCriteria=search_all_names, returnedTags=list_attributes_to_return)

    # Checking to see if the object in the file already exists in the CUCM
    for dp in dp_entries['return'][cucm_resource_name]:
        if site_data[cucm_resource_name]['name'] == dp['name']:
            need_to_add_location = False

    if need_to_add_location:
        response = service.addDevicePool(site_data[cucm_resource_name])
        print(f'Added the {cucm_resource_friendly_name} called `{site_data[cucm_resource_name]["name"]}` with a UUID of {response["return"]} to CUCM')

    else:
        print(f'The {cucm_resource_friendly_name} named `{site_data[cucm_resource_name]["name"]}` already existed in the CUCM so was not added.')
