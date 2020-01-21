"""This reads in a config template and writes a json file that can be
used by the site creation or removal tool.


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
    jinja2

For Windows
    $ pip install jinja2

For Linux
    $ pip3 install jinja2

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

from pathlib import Path
from jinja2 import Template     # Remember to 'pip install jinja2'
from datetime import datetime

################################################################################
#                   Read in site data configuration
################################################################################
file_name = input("Input the exact file to read from the `templates` folder: ")
template_name = 'site_data_template.j2'
template_path = Path('templates') / f'{template_name}'

site_name_from_user_input = input("Input the sitename to use in the template: ")

if not template_path.exists():
    print(f'The file `{template_path}` does not exist in the "site_configurations" folder')
    exit(1)
else:
    print(f'Opening `{template_path}` and reading in the contents.')

with open(template_path) as df:
    template_data = df.read()

template = Template(template_data)
rendered_template = template.render(site_name=site_name_from_user_input)

################################################################################
#                   Write Gathered Data to a JSON File
################################################################################
now = datetime.now().strftime('%Y%m%d_%H%M%S')
output_file = Path("site_configurations") / f"rendered_template_{site_name_from_user_input}_{now}.json"

with open(output_file, 'w') as out:
    out.write(rendered_template)
    print(f"Site Data written to the file `{output_file}` successfully.")
