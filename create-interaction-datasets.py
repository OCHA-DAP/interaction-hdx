#!/usr/bin/python3
"""Create per-country datasets for the Interaction activity data

http://ngoaidmap.org/

See README.md for more details.

Started 2015-11-16 by David Megginson
"""

import config

import ckanapi
import hxl
import urllib

import pprint

#
# Constants
#
INPUTS_URL = 'https://docs.google.com/spreadsheets/d/1TfDOvNysztJCMLc0-EjnC2MpnYlpiVO0eio6XkT8V6I/edit#gid=0'
RESOURCE_URL_TEMPLATE = 'http://ngoaidmap.org/downloads?doc={format}&geolocation={code}&level=0&name={filename}&status=active'


ckan = ckanapi.RemoteCKAN(config.CONFIG['ckanurl'], apikey=config.CONFIG['apikey'])

for row in hxl.data(INPUTS_URL, True):
    country = row.get('country+name+interaction')
    hdx_code = row.get('country+code+m49')
    interaction_code = row.get('country+code+interaction')
    stub = 'ngoaidmap-{code}'.format(code=hdx_code.lower())

    if not hdx_code:
        continue
    
    dataset = {
        'name': stub,
        'title': 'InterAction member activities in {country}'.format(country=country),
        'notes': 'List of aid activities by InterAction members in {country}. '
                 'Source: http://ngoaidmap.org/location/{code}'.format(country=country, code=interaction_code),
        'dataset_source': 'InterAction NGO Aid Map',
        'owner_org': 'interaction',
        'package_creator': 'script',
        'license_id': 'Public Domain',
        'methodology': 'Survey',
        'caveats': 'Unverified live data. May change at any time. '
                   'For information on data limitations, visit http://ngoaidmap.org/p/data',
        'groups': [hdx_code],
        'tags': ['3w', 'ngo'],
        'resources': []
    }

    for format in ['csv', 'xls', 'kml']:
        dataset['resources'].append({
            'name': 'List of activities in {country}'.format(country=country),
            'description': 'Spreadsheet listing InterAction member activities in {country}. '
                           'Unverified member-uploaded data. '
                           'Note that this data comes live from the web site, and can change at any time.'.format(country=country),
            'url': RESOURCE_URL_TEMPLATE.format(format=format, code=interaction_code, filename='activities'.format(format=format)),
            'format': format
            })

    try:
        ckan.call_action('package_create', dataset)
        print("Created {stub}...".format(stub=stub))
    except:
        ckan.call_action('package_update', dataset)
        print("Updated {stub}...".format(stub=stub))

exit(0)
