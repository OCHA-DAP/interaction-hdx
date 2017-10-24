#!/usr/bin/python3
"""Create per-country datasets for the Interaction activity data

http://ngoaidmap.org/

See README.md for more details.

Started 2015-11-16 by David Megginson
"""

import ckanapi
import hxl
import urllib

# read configuration values from config.py
import config

#
# Constants
#

INPUTS_URL = 'https://docs.google.com/spreadsheets/d/1TfDOvNysztJCMLc0-EjnC2MpnYlpiVO0eio6XkT8V6I/edit#gid=0'
PROXY_URL_TEMPLATE = 'https://proxy.hxlstandard.org/data/-FTw3n.{format}?url={url}'
INTERACTION_URL_TEMPLATE = 'http://ngoaidmap.org/downloads?doc={format}&geolocation={code}&level=0&name={filename}&status=active'


def q(s):
    """Quote a parameter for a URL."""
    return urllib.parse.quote(s)


#
# Create the CKAN API object
#
ckan = ckanapi.RemoteCKAN(config.CONFIG['ckanurl'], apikey=config.CONFIG['apikey'], user_agent=config.CONFIG.get('user_agent', None))

#
# Loop through every HXL data row in the source spreadsheet (INPUTS_URL)
#

for row in hxl.data(INPUTS_URL, True):

    # Skip if there's no M49 code for HDX
    hdx_code = row.get('country+code+m49')
    if hdx_code:
        hdx_code = hdx_code.lower()
    else:
        continue

    country = row.get('country+name+interaction')
    interaction_code = row.get('country+code+interaction')
    stub = 'ngoaidmap-{code}'.format(code=hdx_code.lower())


    # Make sure the country exists on HDX
    try:
        country_data = ckan.action.group_show(id=hdx_code)
    except:
        print("** Country not found on HDX: {} {}".format(hdx_code, country))
        continue

    # Create the basic dataset object, with an empty list of resources
    dataset_new_properties = {
        'name': stub,
        'title': 'InterAction member activities in {country}'.format(country=country),
        'notes': 'List of aid activities by InterAction members in {country}. '
                 'Source: http://ngoaidmap.org/location/{code}'.format(country=country, code=q(interaction_code)),
        'dataset_source': 'InterAction NGO Aid Map',
        'private': False,
        'owner_org': 'interaction',
        'package_creator': 'script',
        'license_id': 'Public Domain',
        'methodology': 'Survey',
        'data_update_frequency': '0',
        'dataset_date': '11/16/2015-12/31/2027',
        'caveats': 'Unverified live data. May change at any time. '
                   'For information on data limitations, visit http://ngoaidmap.org/p/data',
        'groups': [{'name': hdx_code}],
        'tags': [{'name': '3w'}, {'name': 'ngo'}, {'name': hdx_code}, {'name': 'hxl'}],
        'resources': []
    }

    # Add resources to the dataset
    for format in ['csv', 'json']:
        interaction_url = INTERACTION_URL_TEMPLATE.format(
            format='csv', 
            code=q(interaction_code), 
            filename='activities.csv'
        )
        proxy_url = PROXY_URL_TEMPLATE.format(url=q(interaction_url), format=format)
        dataset_new_properties['resources'].append({
            'name': 'List of activities in {country}'.format(country=country),
            'description': 'Spreadsheet listing InterAction member activities in {country}. '
            'Unverified member-uploaded data. '
            'Note that this data comes live from the web site, and can change at any time.'.format(country=country),
            'url': proxy_url,
            'format': format
        })
        
    # Update or create, as appropriate
    try:
        dataset = ckan.action.package_show(id=stub)
    except:
        dataset = False

    try:
        if dataset:
            for prop in dataset_new_properties:
                dataset[prop] = dataset_new_properties[prop]
            ckan.call_action('package_update', dataset)
            print("Updated {stub}...".format(stub=stub))
        else:
            dataset = dataset_new_properties
            ckan.call_action('package_create', dataset)
            print("Created {stub}...".format(stub=stub))
    except Exception as e:
        print("*** Failed to create record for {}: {}".format(stub, str(e)))

exit(0)

# end
