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
#PROXY_URL_TEMPLATE = 'https://proxy.hxlstandard.org/data/-FTw3n.{format}?url={url}'
PROXY_URL_TEMPLATE = 'https://proxy.hxlstandard.org/data.{format}?url={url}&stub={stub}&tagger-20-header=actual_project_reach&tagger-11-tag=%23sector%2Blist&tagger-28-tag=%23meta%2Burl&tagger-15-tag=%23date%2Bbudget&tagger-23-header=location&tagger-13-header=budget_numeric&tagger-32-tag=%23org%2Bdonor%2Blist&tagger-25-tag=%23contact%2Brole&tagger-19-header=target_project_reach&tagger-27-header=project_contact_phone_number&tagger-09-tag=%23date%2Bstart&tagger-13-tag=%23budget%2Bnum&cut-exclude-tags01=contact&header-row=1&tagger-07-header=activities&tagger-27-tag=%23contact%2Bphone&tagger-15-header=budget_value_date&tagger-10-tag=%23date%2Bend&tagger-22-header=target_groups&tagger-04-header=project_tags&tagger-06-tag=%23activity%2Bdescription&tagger-02-header=interaction_intervention_id&tagger-06-header=project_description&tagger-18-tag=%23org%2Bprime&tagger-11-header=sectors&tagger-10-header=end_date&tagger-19-tag=%23targeted%2Bnum&tagger-09-header=start_date&tagger-16-tag=%23org%2Bpartner%2Binternational%2Blist&tagger-29-header=date_provided&tagger-12-tag=%23subsector%2Bcrosscut&tagger-17-header=local_partners&tagger-04-tag=%23meta%2Btags&tagger-12-header=cross_cutting_issues&tagger-05-header=project_name&tagger-01-header=organization&tagger-30-tag=%23date%2Bupdated&tagger-07-tag=%23activity%2Bdetails&tagger-26-header=project_contact_email&tagger-08-header=additional_information&tagger-05-tag=%23activity%2Bname&tagger-31-tag=%23status%2Bcode&force=on&tagger-24-header=project_contact_person&tagger-14-header=budget_currency&tagger-01-tag=%23org%2Bimplementing%2Bname&tagger-14-tag=%23budget%2Bcurrency&tagger-29-tag=%23date%2Bprovided&tagger-03-header=org_intervention_id&tagger-30-header=date_updated&tagger-21-header=project_reach_unit&tagger-02-tag=%23meta%2Bid%2Binteraction&tagger-20-tag=%23reached%2Bnum&tagger-21-tag=%23targeted%2Btype&tagger-31-header=status&tagger-22-tag=%23targeted%2Bdescription&tagger-03-tag=%23meta%2Bid%2Borg&tagger-25-header=project_contact_position&tagger-32-header=donors&tagger-23-tag=%23loc&filter01=cut&tagger-16-header=international+partners&tagger-24-tag=%23contact%2Bname&tagger-28-header=project_website&tagger-08-tag=%23meta%2Bnotes&tagger-17-tag=%23org%2Bpartner%2Blocal%2Blist&tagger-26-tag=%23contact%2Bemail&tagger-18-header=prime_awardee'
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
        'maintainer': 'eyox',
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
        proxy_url = PROXY_URL_TEMPLATE.format(url=q(interaction_url), format=format, stub=stub)
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
