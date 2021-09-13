import argparse
import sys
import requests
import getpass
import configparser
import re
from bs4 import BeautifulSoup
from os.path import expanduser
from urllib.parse import urlparse, urlunparse
import configparser

CONFIG_PREFIX="awsume_saml_"
CONFIG_PREFIX_CUSTOM_INPUT=f"{CONFIG_PREFIX}custom_input_"
SSLVERIFICATION = True

from awsume.awsumepy import hookimpl, safe_print


def get_custom_config(profile, config_path='~/.aws/config'):
    config_path = expanduser(config_path)
    config = configparser.ConfigParser()
    config.read(config_path)
    saml_config = {
        'custom_input' : {}
    }
    xprofile = profile if profile in config else "profile "+profile
    if xprofile not in config:
        print(f'[ERROR] Neither "{profile}" nor "{xprofile}" can be found in {config_path}', file=sys.stderr)
        return None

    for (k,v) in config[xprofile].items():
        if k.startswith(CONFIG_PREFIX):
            if k.startswith(CONFIG_PREFIX_CUSTOM_INPUT):
                saml_config['custom_input'][k[len(CONFIG_PREFIX_CUSTOM_INPUT):]] = v
            else:
                saml_config[k[len(CONFIG_PREFIX):]] = v

    return saml_config

def get_login_info(custom_config, arguments):
    if 'username' in custom_config:
        username = custom_config['username']
    else:
        safe_print("Username:", end=' ')
        username = input()
    if 'password' in custom_config:
        password = custom_config['password']
    else:
        password = getpass.getpass()
        safe_print('')
    
    # possibly adding mfa token to password 
    # E.g. config file:
    # [profile test]
    # awsume_saml_username = u1
    # awsume_saml_password = abc{mfa_token}
    return username, password.format(**arguments)

def generate_payload(formsoup, custom_config=None):
    # being used for automatic username search
    payload = {}
    # search for username and password input fields
    for inputtag in formsoup.find_all(re.compile('(INPUT|input)')):
        name = inputtag.get('name','')
        value = inputtag.get('value','')
        if "user" in name.lower():
            #Make an educated guess that this is the right field for the username
            payload[name] = custom_config['username']
        elif "email" in name.lower():
            #Some IdPs also label the username field as 'email'
            payload[name] = custom_config['username']
        elif "pass" in name.lower():
            #Make an educated guess that this is the right field for the password
            payload[name] = custom_config['password']
        else:
            #Simply populate the parameter with the existing value (picks up hidden fields in the login form)
            payload[name] = value
    # add custom input fields
    if custom_config and custom_config['custom_input']:
        for k,v in custom_config['custom_input'].items():
            payload[k] = v
    return payload

def get_saml_submit_url(formsoup, login_url):
    # Some IdPs don't explicitly set a form action, but if one is set we should
    # build the idpauthformsubmiturl by combining the scheme and hostname 
    # from the entry url with the form action target
    # If the action tag doesn't exist, we just stick with the 
    # idpauthformsubmiturl above
    for inputtag in formsoup.find_all(re.compile('(FORM|form)')):
        action = inputtag.get('action')
        if action:
            if action.startswith("https://"):
                idpauthformsubmiturl = action
            else:
                parsedurl = urlparse(login_url)
                idpauthformsubmiturl = parsedurl.scheme + "://" + parsedurl.netloc + action
    return idpauthformsubmiturl

def get_assertion(session, idpauthformsubmiturl, payload):
    # Performs the submission of the IdP login form with the above post data
    response = session.post(
    idpauthformsubmiturl, data=payload, verify=SSLVERIFICATION)
    # Decode the response and extract the SAML assertion
    soup = BeautifulSoup(response.text, 'html.parser')
    assertion = ''

    # Look for the SAMLResponse attribute of the input tag (determined by
    # analyzing the debug print lines above)
    for inputtag in soup.find_all('input'):
        if(inputtag.get('name') == 'SAMLResponse'):
            #print(inputtag.get('value'))
            assertion = inputtag.get('value')

    # Better error handling is required for production use.
    if (assertion == ''):
        #TODO: Insert valid error checking/handling
        safe_print('Response did not contain a valid SAML assertion')
        sys.exit(0)
    return assertion

def get_config_file(arguments):
    return expanduser(arguments['config_file'] if arguments['config_file'] else '~/.aws/config')

@hookimpl
def get_credentials_with_saml(config: dict, arguments: argparse.Namespace):
    args = vars(arguments)
    config_path = get_config_file(args)
    if not args['profile_name']:
        print(f'[ERROR] No profile given to get saml information from.', file=sys.stderr)
        return None

    custom_config = get_custom_config(args['profile_name'], config_path)
    if 'endpoint' not in custom_config:
        print(f'[ERROR] No endpoint given in profile.', file=sys.stderr)
        return None

    custom_config['username'], custom_config['password'] = get_login_info(custom_config, args)
    # Initiate session handler
    session = requests.Session()
    # Programmatically get the SAML assertion
    # Opens the initial IdP url and follows all of the HTTP302 redirects, and
    # gets the resulting login page
    formresponse = session.get(custom_config['endpoint'], verify=SSLVERIFICATION)
    # Parse the response and extract all the necessary values
    # in order to build a dictionary of all of the form values the IdP expects
    formsoup = BeautifulSoup(formresponse.text, 'html.parser')
    payload = generate_payload(formsoup, custom_config)
    idpauthformsubmiturl = get_saml_submit_url(formsoup, custom_config['endpoint'])
    assertion = get_assertion(session, idpauthformsubmiturl, payload)
    return assertion
