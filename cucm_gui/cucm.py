from lxml import etree
from requests import Session
from requests.auth import HTTPBasicAuth

from zeep import Client, Settings, Plugin
from zeep.transports import Transport

from pathlib import Path


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

    session = Session()

    session.verify = False
    session.auth = HTTPBasicAuth(username, password)

    transport = Transport(session=session, timeout=10)
    settings = Settings(strict=False, xml_huge_tree=True)

    plugin = [MyLoggingPlugin()] if DEBUG else []

    client = Client(WSDL_FILE, settings=settings, transport=transport, plugins=plugin)

    service = client.create_service('{http://www.cisco.com/AXLAPIService/}AXLAPIBinding',
                                    'https://{cucm}:8443/axl/'.format(cucm=cucm_ip))

    return service