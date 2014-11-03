"""
Validate.

Some functions to validate methods.
"""
from .config import RESOURCES


def validate_address(address, verb, sub_resource=None):
    """ Test if address is valid. """
    address_available = (address in RESOURCES)

    if address_available:
        resource = RESOURCES[address]
    else:
        raise LookupError('address not found')

    can_use_verb = (verb in resource['verbs'])

    if can_use_verb:
        pass
    else:
        raise LookupError('Verb not valid')

    if sub_resource is not None:

        if 'resources' in resource:
            sub_resource_available = (sub_resource in resource['resources'])
        else:
            sub_resource_available = False

        if sub_resource_available:
            pass
        else:
            raise LookupError('Resource not valid')

    return resource


def validate_required_params(resource, payload):
    """ Make sure no required params were missed. """
    missed = [
        x for x in resource['required']
        if x not in list(payload.keys())
    ]
    if len(missed) > 0:
        missed = ', '.join(missed)
        raise ValueError(
            'Missing required params in payload: %s' % missed
        )


def validate_response(response, expected_code):
    """ Validate response. """
    success = (response.status_code == expected_code)
    valid_response = (
        response.headers['content-type'] == 'application/json; charset=utf-8'
    )
    data = response.json()

    if success & valid_response:
        return True
    elif 'error_description' in data:
        raise ValueError(data['error_description'])
    else:
        raise ValueError(data)
