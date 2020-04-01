from lxml import etree
from requests import Session
from requests.auth import HTTPBasicAuth


from zeep import Client, Settings, Plugin
from zeep.transports import Transport
from zeep.helpers import serialize_object

from pathlib import Path

from flask import session


def connect_to_cucm(username=None, password=None, cucm_ip=None):
    WSDL_FILE = str(Path('schema') / 'AXLAPI.wsdl')

    DEBUG = False
    SUPRESS_INSECURE_CONNECTION_WARNINGS = True

    if SUPRESS_INSECURE_CONNECTION_WARNINGS:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # This class lets you view the incoming and outgoing http headers and/or XML
    class MyLoggingPlugin(Plugin):
        def egress(self, envelope, http_headers, operation, binding_options):
            xml = etree.tostring(envelope, pretty_print=True, encoding='unicode')
            print(f'\nRequest\n-------\nHeaders:\n{http_headers}\n\nBody:\n{xml}')

        def ingress(self, envelope, http_headers, operation):
            xml = etree.tostring(envelope, pretty_print=True, encoding='unicode')
            print(f'\nResponse\n-------\nHeaders:\n{http_headers}\n\nBody:\n{xml}')

    sess = Session()

    sess.verify = False
    sess.auth = HTTPBasicAuth(username, password)

    transport = Transport(session=sess, timeout=10)
    settings = Settings(strict=False, xml_huge_tree=True)

    plugin = [MyLoggingPlugin()] if DEBUG else []

    client = Client(WSDL_FILE, settings=settings, transport=transport, plugins=plugin)

    service = client.create_service('{http://www.cisco.com/AXLAPIService/}AXLAPIBinding',
                                    'https://{cucm}:8443/axl/'.format(cucm=cucm_ip))

    return service


def list_users():
    # Connect to CUCM and pull all the users
    cucm = connect_to_cucm(username=session.get('cucm_username'),
                           password=session.get('cucm_password'),
                           cucm_ip=session.get('cucm_ip'))

    returned_data = cucm.listUser(searchCriteria={'userid': '%'},
                                  returnedTags={'userid': '', 'firstName': '', 'lastName': ''})

    # Connect to the CUCM DB and pull which users are local users
    sql_query = "select userid from enduser where fkdirectorypluginconfig is NULL"
    query_results = cucm.executeSQLQuery(sql=sql_query)
    local_users = [x[0].text for x in query_results['return']['row']]

    # The listUser AXL Call doesn't include if the user is LDAP or Local User.
    # This pulls all the local users directly from the database and filters
    users_data = []
    for user in returned_data['return']['user']:
        # Filter out the ldap users
        if not session['include_ldap_users'] and user['userid'] not in local_users:
            pass
        else:
            # The WTForms library requires a list of Tuples to create dynamic UI drop downs
            users_data.append((f"{user['userid']}", f"{user['firstName']} {user['lastName']}"))

    return users_data


def get_user():
    userid = session.get('selected_user')
    cucm = connect_to_cucm(username=session.get('cucm_username'),
                           password=session.get('cucm_password'),
                           cucm_ip=session.get('cucm_ip'))

    returned_data = cucm.getUser(userid=userid)
    return serialize_object(returned_data['return']['user'])


def update_user():
    data = session.get('user_data_to_update')
    cucm = connect_to_cucm(username=session.get('cucm_username'),
                           password=session.get('cucm_password'),
                           cucm_ip=session.get('cucm_ip'))

    # The **data is unpacking a dictionary to be used as parameters for the function
    returned_data = cucm.updateUser(**data)
    return serialize_object(returned_data)


def list_device_pools():
    cucm = connect_to_cucm(username=session.get('cucm_username'),
                           password=session.get('cucm_password'),
                           cucm_ip=session.get('cucm_ip'))

    returned_tags = {
        'name': '',
        'dateTimeSettingName': '',
        'callManagerGroupName': '',
        'mediaResourceListName': '',
        'regionName': '',
        'networkLocale': '',
        'srstName': '',
        'locationName': '',
        'mobilityCssName': '',
        'physicalLocationName': '',
        'deviceMobilityGroupName': ''
    }

    returned_data = cucm.listDevicePool(searchCriteria={'name': '%'}, returnedTags=returned_tags)
    returned_dict = serialize_object(returned_data['return']['devicePool'])
    filtered_data = []

    for device_pool in returned_dict:
        filtered_pool = {}
        for k, v in device_pool.items():
            if device_pool[k] is not None:
                from collections import OrderedDict
                if isinstance(device_pool[k], OrderedDict):
                    filtered_pool[k] = v['_value_1']
                else:
                    filtered_pool[k] = v

        filtered_data.append(filtered_pool)

    return filtered_data


def list_user_groups():
    cucm = connect_to_cucm(username=session.get('cucm_username'),
                           password=session.get('cucm_password'),
                           cucm_ip=session.get('cucm_ip'))

    returned_data = cucm.listUserGroup(searchCriteria={'name': '%'}, returnedTags={'name': ''})

    user_groups = []

    for group in returned_data['return']['userGroup']:
        # Puts the data into a list of tuples so it can be passed into the selector form
        group_tuple = ({"name": group["name"]}, group["name"])
        user_groups.append(group_tuple)

    return user_groups


def is_ldap_user():
    user_data = session.get('user_data')

    if user_data['ldapDirectoryName']['uuid']:
        return True
    else:
        return False
