#!/usr/bin/python

from argparse import ArgumentParser
import urllib2
import json
from numbers import Number
from math import ceil

# Globals
customer_endpoint = 'https://backend-challenge-winter-2017.herokuapp.com/customers.json'


def validate_field(field, rule_name, rule_args, customer):
    '''
    Given a customer, customer field, and validation rule, check whether the
    field passes validation.
    '''
    if rule_name == 'required':
        if rule_args == True:
            return (field in customer)
        else:
            return True

    if rule_name == 'type':
        if field not in customer:
            return True

        if rule_args == 'boolean':
            return isinstance(customer[field], bool)
        elif rule_args == 'number':
            return isinstance(customer[field], Number)
        elif rule_args == 'string':
            return isinstance(customer[field], basestring)

    elif rule_name == 'length':
        if field not in customer:
            return True

        if not isinstance(customer[field], basestring):
            return False

        char_count = len(customer[field])
        if 'max' in rule_args and char_count > rule_args['max']:
            return False
        elif 'min' in rule_args and char_count < rule_args['min']:
            return False
        else:
            return True

    else:
        # Unregistered rule
        print('***Error: found unexpected rule {} for field {}' % (rule_name, field))
        return False


def validate_customers(customers, validations):
    '''
    Checks an array of customers against a dictionary of validations.
    '''
    # We will eventually return this var
    invalid_customers = []

    for customer in customers:
        # Keep track of which fields are invalid for this customer
        invalid_fields = []

        # Validate all fields with validations
        for validation in validations:
            field = validation.keys()[0]
            rules = validation[field]
            for rule_name, rule_args in rules.items():
                if not validate_field(field, rule_name, rule_args, customer):
                    invalid_fields.append(field)
                    # Move on to next field; don't check any remaining rules
                    break

        # If we have any invalid fields, add this customer to invalid_customers
        if len(invalid_fields) > 0:
            invalid_customers.append({
                'id': customer['id'],
                'invalid_fields': invalid_fields
            })

    return invalid_customers


def load_page(page):
    '''
    Returns the raw JSON data from the given page of `customer_endpoint`.
    '''
    res = urllib2.urlopen(customer_endpoint + '?page=' + str(page))
    return json.load(res)


def main():
    # Get page argument from command line args
    parser = ArgumentParser(description='Validate a customer list.')
    parser.add_argument('-p', '--page', type=int, default=1,
                        help='page number to validate')
    parser.add_argument('--all', action='store_true', help='if provided, validate all pages')
    args = parser.parse_args()
    page = args.page
    validate_all_pages = args.all


    # Fetch customers from API
    result = []
    if validate_all_pages:
        # Fetch first page to get pagination data, then fetch remaining pages
        data = load_page(0)
        result.extend(validate_customers(data['customers'], data['validations']))

        pages_to_fetch = int(ceil(float(data['pagination']['total']) / data['pagination']['per_page']))

        for page in range(1, pages_to_fetch):
            data = load_page(page)
            result.extend(validate_customers(data['customers'], data['validations']))
    else:
        customers, validations = load_page(page)
        result = validate_customers(customers, validations)

    # Print result
    print(json.dumps(result))


if __name__ == '__main__':
    main()
