from cucm_gui import app
from flask import render_template, flash, redirect, url_for, session
from cucm_gui.forms import LoginForm

from lxml import etree
from requests import Session
from requests.auth import HTTPBasicAuth

from zeep import Client, Settings, Plugin
from zeep.transports import Transport

from pathlib import Path


@app.route('/')
def main_page():
    return render_template('base.html')


@app.route('/list_cucm_device_pools', methods=['GET', 'POST'])
def cucm_list_device_pools():
    form = LoginForm()
    if form.validate_on_submit():
        session['cucm_username'] = form.cucm_username.data
        session['cucm_password'] = form.cucm_password.data
        session['cucm_ip'] = form.cucm_ip.data
        flash(f'Returned data from the CUCM at IP: {form.cucm_ip.data}')
        return redirect(url_for('cucm_device_pools'))
    return render_template('cucm_login.html', title='CUCM Data', form=form)


@app.route('/cucm_device_pools', methods=['GET', 'POST'])
def cucm_device_pools():
    cucm = connect_to_cucm(username=session.get('cucm_username'), password=session.get('cucm_password'), cucm_ip=session.get('cucm_ip'))
    returned_data = cucm.listDevicePool(searchCriteria={'name': '%'}, returnedTags={'name': ''})
    device_pools = [x['name'] for x in returned_data['return']['devicePool']]
    return render_template('cucm_device_pools.html', title='CUCM Device Pools', device_pools=device_pools)


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
