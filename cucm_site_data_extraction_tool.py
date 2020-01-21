"""CUCM Site Data Extraction Tool

This is a where you enter in a Device Pool and it pulls out the Device Pool as well as data for dependant objects.

The output will be a JSON file in the output folder.


The intent is you could use that to create a file that could modified and be fed back
into the cucm_site_creation_tool in this repo to make deploying sites to match existing sites easier.

This core connectivity code was copied from the axlZeep.py file from the DevNet AXL examples
https://github.com/CiscoDevNet/axl-python-zeep-samples

A minimum of Python 3.6 is required for this tool.

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
import json

from lxml import etree
from requests import Session
from requests.auth import HTTPBasicAuth

from zeep import Client, Settings, Plugin
from zeep.transports import Transport

from pathlib import Path
from datetime import datetime

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


# Create a dictionary for the output
output_data = {}

# Enter the device pool you're looking for
device_pool_to_find = input("Enter the exact name of the Device Pool in the CUCM: ")

# List all of the devices in the system
# Each list method has various tags you can search on
# Most every method has the name parameter though
search_all_names = {
    # The percent sign is a mulit-character wildcard in the CUCM searchCriteria parameters
    'name': '%'
}                       # The question mark (not shown) is a single character wild card

# The ZEEP library will return all parameters
# But you have to define which ones you want data for otherwise all you'll get are None values
# in the return data when using the list methods.
device_pool_attributes_to_return = {
    'name': '',
}


device_pools = service.listDevicePool(
    searchCriteria=search_all_names, returnedTags=device_pool_attributes_to_return)

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
    'locationName': device_pool_data['locationName']['_value_1']
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
if not date_time_group_data['phoneNtpReferences']:
    ntp_refs = None
else:
    for ntp_ref in date_time_group_data['phoneNtpReferences']['selectedPhoneNtpReference']:
        data = {
            'phoneNtpName': ntp_ref['phoneNtpName']['_value_1'],
            'selectionOrder': ntp_ref['selectionOrder']
        }
        ntp_ref_data.append(data)
    ntp_refs = {'selectedPhoneNtpReference': ntp_ref_data}

date_time_group_output_data = {
    'name': date_time_group_data['name'],
    'timeZone': date_time_group_data['timeZone'],
    'separator': date_time_group_data['separator'],
    'dateformat': date_time_group_data['dateformat'],
    'timeFormat': date_time_group_data['timeFormat'],
    'phoneNtpReferences': ntp_refs
}

output_data['dateTimeGroup'] = date_time_group_output_data

################################################################################
#                   CallManger Group
################################################################################
call_manager_group_name = output_data['devicePool']['callManagerGroupName']

call_manager_group = service.getCallManagerGroup(name=call_manager_group_name)
call_manager_group_data = call_manager_group['return']['callManagerGroup']
cm_member_data = []

# Strip out unneeded values from return data
for member in call_manager_group_data['members']['member']:
    data = {
        'callManagerName': member['callManagerName']['_value_1'],
        'priority': member['priority']
    }
    cm_member_data.append(data)

call_manager_group_output_data = {
    'name': call_manager_group_data['name'],
    'tftpDefault': call_manager_group_data['tftpDefault'],
    'members': {'member': cm_member_data}
}

output_data['callManagerGroup'] = call_manager_group_output_data

################################################################################
#                   Media Resource Group List
################################################################################
mrgl_name = output_data['devicePool']['mediaResourceListName']

# A MRGL might not be set, verifies one is configured for the Device Pool
if mrgl_name:
    mrgl = service.getMediaResourceList(name=mrgl_name)
    mrgl_data = mrgl['return']['mediaResourceList']
    mrgl_member_data = []

    # Strip out unneeded values from return data assuming there is data in the object
    if not mrgl_data['members']:
        mrgl_members = None
    else:
        for member in mrgl_data['members']['member']:
            data = {
                'mediaResourceGroupName': member['mediaResourceGroupName']['_value_1'],
                'order': member['order']
            }
            mrgl_member_data.append(data)
        mrgl_members = {'member': mrgl_member_data}

    mrgl_output_data = {
        'name': mrgl_data['name'],
        'clause': mrgl_data['clause'],
        'members': mrgl_members
    }

    output_data['mediaResourceList'] = mrgl_output_data

else:
    output_data['mediaResourceList'] = {}

################################################################################
#                   Region
################################################################################
region_name = output_data['devicePool']['regionName']

region = service.getRegion(name=region_name)

region_data = region['return']['region']
related_region_data = []

# Strip out unneeded values from return data assuming there is data in the object
if not region_data['relatedRegions']:
    related_region = None
else:
    for region in region_data['relatedRegions']['relatedRegion']:
        data = {
            'regionName': region['regionName']['_value_1'],
            'bandwidth': region['bandwidth'],
            'videoBandwidth': region['videoBandwidth'],
            'lossyNetwork': region['lossyNetwork'],
            'codecPreference': region['codecPreference']['_value_1'],
            'immersiveVideoBandwidth': region['immersiveVideoBandwidth']
        }

        related_region_data.append(data)
        related_region = {'relatedRegion': related_region_data}

region_output_data = {
    'name': region_data['name'],
    'relatedRegions': related_region,
    'defaultCodec': region_data['defaultCodec']
}

output_data['region'] = region_output_data

################################################################################
#                   SRST Name
################################################################################
srst_name = output_data['devicePool']['srstName']

region = service.getSrst(name=srst_name)
srst_data = region['return']['srst']

srst_output_data = {
    'name': srst_data['name'],
    'port': srst_data['port'],
    'ipAddress': srst_data['ipAddress'],
    'ipv6Address': srst_data['ipv6Address'],
    'SipNetwork': srst_data['SipNetwork'],
    'SipPort': srst_data['SipPort'],
    'srstCertificatePort': srst_data['srstCertificatePort'],
    'isSecure': srst_data['isSecure']
}
output_data['srst'] = srst_output_data

################################################################################
#                   Location
################################################################################
location_name = output_data['devicePool']['locationName']

if location_name:
    location = service.getLocation(name=location_name)
    location_data = location['return']['location']
    related_location_data = []
    between_location_data = []

    # Strip out unneeded values from return data assuming there is data in the object
    if not location_data['relatedLocations']:
        related_location = None
    else:
        for rel_loc in location_data['relatedLocations']['relatedLocation']:
            data = {
                'locationName': rel_loc['locationName']['_value_1'],
                'rsvpSetting': rel_loc['rsvpSetting']
            }
            related_location_data.append(data)
        related_location = {'relatedLocation': related_location_data}

    if not location_data['betweenLocations']:
        between_location = None
    else:
        for bet_loc in location_data['betweenLocations']['betweenLocation']:
            data = {
                'locationName': bet_loc['locationName']['_value_1'],
                'weight': bet_loc['weight'],
                'audioBandwidth': bet_loc['audioBandwidth'],
                'videoBandwidth': bet_loc['videoBandwidth'],
                'immersiveBandwidth': bet_loc['immersiveBandwidth']
            }
            between_location_data.append(data)
        between_location = {'betweenLocation': between_location_data}

    location_output_data = {
        'name': location_data['name'],
        'relatedLocations': related_location,
        'withinAudioBandwidth': location_data['withinAudioBandwidth'],
        'withinVideoBandwidth': location_data['withinVideoBandwidth'],
        'withinImmersiveKbits': location_data['withinImmersiveKbits'],
        'betweenLocations': between_location
    }

    output_data['location'] = location_output_data

else:
    output_data['location'] = {}


################################################################################
#                   Write Gathered Data to a JSON File
################################################################################
now = datetime.now().strftime('%Y%m%d_%H%M%S')
output_file = Path("site_configurations") / f"site_export_{device_pool_to_find}_{creds.CUCM_ADDRESS}_{now}.json"

with open(output_file, 'w') as out:
    output_json = json.dumps(output_data, indent=2)
    out.write(output_json)
    print(f"Site Data written to the file `{output_file}` successfully.")
