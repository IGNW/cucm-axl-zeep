"""CUCM Site Data Extraction Tool

This is a where you put in a Device Pool and it crawls the CUCM and Pulls out all the related fields.

The output will be into a YAML file.

The intent is you could use that to create a file that could modified and be fed back 
into the cucm_site_creation_tool in this repo to make deploying sites to match existing sites easier.

This core of this was copied from the axlZeep.py file from the DevNet AXL examples
https://github.com/CiscoDevNet/axl-python-zeep-samples

A minimum of Python 3.6 is required for this as it depends on the Dictionaries preserving order and
that feature was introduced in Python 3.6

Install Python 3.6 or later.
On Windows during the install, choose the option in the installer to add to PATH environment variable

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


from lxml import etree
from requests import Session
from requests.auth import HTTPBasicAuth

from zeep import Client, Settings, Plugin
from zeep.transports import Transport
from zeep.cache import SqliteCache
from zeep.exceptions import Fault

# The WSDL is a local file
WSDL_FILE = 'schema/AXLAPI.wsdl'

# Configure CUCM location and AXL credentials in creds.py
import creds
# Change to true to enable output of request/response headers and XML
DEBUG = False

# If you have a pem file certificate for CUCM, uncomment and define it here

#CERT = 'some.pem'

# These values should work with a DevNet sandbox
# You may need to change them if you are working with your own CUCM server



# This class lets you view the incoming and outgoing http headers and/or XML
class MyLoggingPlugin( Plugin ):

    def egress( self, envelope, http_headers, operation, binding_options ):

        # Format the request body as pretty printed XML
        xml = etree.tostring( envelope, pretty_print = True, encoding = 'unicode')

        print( f'\nRequest\n-------\nHeaders:\n{http_headers}\n\nBody:\n{xml}' )

    def ingress( self, envelope, http_headers, operation ):

        # Format the response body as pretty printed XML
        xml = etree.tostring( envelope, pretty_print = True, encoding = 'unicode')

        print( f'\nResponse\n-------\nHeaders:\n{http_headers}\n\nBody:\n{xml}' )

session = Session()

# We avoid certificate verification by default, but you can uncomment and set
# your certificate here, and comment out the False setting

#session.verify = CERT
session.verify = False
session.auth = HTTPBasicAuth( creds.USERNAME, creds.PASSWORD )

# Create a Zeep transport and set a reasonable timeout value
transport = Transport( session = session, timeout = 10 )

# strict=False is not always necessary, but it allows zeep to parse imperfect XML
settings = Settings( strict=False, xml_huge_tree=True )

# If debug output is requested, add the MyLoggingPlugin callback
plugin = [ MyLoggingPlugin() ] if DEBUG else [ ]

# Create the Zeep client with the specified settings
client = Client( WSDL_FILE, settings = settings, transport = transport,
        plugins = plugin )

# service = client.create_service("{http://www.cisco.com/AXLAPIService/}AXLAPIBinding", CUCM_URL)
service = client.create_service( '{http://www.cisco.com/AXLAPIService/}AXLAPIBinding',
                                'https://{cucm}:8443/axl/'.format( cucm = creds.CUCM_ADDRESS ))


# Create a dictionary for the output
output_data = {}

# Enter the device pool you're looking for
device_pool_to_find = "Default"

# List all of the devices in the system
# Each list method has various tags you can search on
# Most every method has the name parameter though
search_all_names = {
    'name': '%'         # The percent sign is a mulit-character wildcard in the CUCM searchCriteria parameters 
}                       # The question mark (not shown) is a single character wild card

# The ZEEP library will return all parameters
# But you have to define which ones you want data for otherwise all you'll get are None values
# in the return data when using the list methods.
device_pool_attributes_to_return = {
    'name': '',
}


device_pools = service.listDevicePool(searchCriteria={'name': '%'}, returnedTags=device_pool_attributes_to_return)

# Determine if the desired Device Pool is in the list of returned data
found_device_pool = False

for dp in device_pools['return']['devicePool']:
    if device_pool_to_find == dp['name']:
        found_device_pool = True

if not found_device_pool:
    print("The device pool you entered could not be found.\nPlease try again.")
    exit(1)     # Non-zero exit codes indicate a problem

################################################################################
#                   Device Pool
################################################################################
# Get all the device pool info
device_pool = service.getDevicePool(name=device_pool_to_find)
device_pool_data = device_pool['return']['devicePool']

# Extract the data from the returned output
device_pool_output_data = {
    'name': device_pool_data['name'],
    'dateTimeSettingName': device_pool_data['dateTimeSettingName']['_value_1'],
    'callManagerGroupName': device_pool_data['callManagerGroupName']['_value_1'],
    'mediaResourceListName': device_pool_data['mediaResourceListName']['_value_1'],
    'regionName': device_pool_data['regionName']['_value_1'],
    'srstName': device_pool_data['srstName']['_value_1'],
    'locationName': device_pool_data['locationName']['_value_1'],
}

output_data['devicePool'] = device_pool_output_data

################################################################################
#                   Date Time Group
################################################################################
# Get the name of the Date Time Group Used
date_time_group_name = output_data['devicePool']['dateTimeSettingName']

date_time_group = service.getDateTimeGroup(name=date_time_group_name)
date_time_group_data = date_time_group['return']['dateTimeGroup']

ntp_ref_data = []
# Strip out unneeded values from return data
for ntp_ref in date_time_group_data['phoneNtpReferences']['selectedPhoneNtpReference']:
    data = {
        'phoneNtpName': ntp_ref['phoneNtpName']['_value_1'],
        'selectionOrder': ntp_ref['selectionOrder']
    }
    ntp_ref_data.append(data)

date_time_group_output_data = {
    'name': date_time_group_data['name'],
    'timeZone': date_time_group_data['timeZone'],
    'separator': date_time_group_data['separator'],
    'dateformat': date_time_group_data['dateformat'],
    'timeFormat': date_time_group_data['timeFormat'],
    'phoneNtpReferences': {'selectedPhoneNtpReference': ntp_ref_data}
}

output_data['dateTimeGroup'] = date_time_group_output_data

print(output_data)

#output_data['dateTimeGroup']['name'] = 'JoeNTP'
#to_add = service.addDateTimeGroup(output_data['dateTimeGroup'])
#print(to_add)