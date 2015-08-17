# -*- coding: utf-8 -*-

import sys
from os import listdir
import re
import datetime
import operator
from decimal import *

reload(sys)  
sys.setdefaultencoding('utf8')

# Number of weeks not including the current week
number_of_weeks = 20
include_this_week = False

def main():
    payments = get_payments('Statements.txt', 'Santander')

    current_week_number = datetime.datetime.now().isocalendar()[1]

    with open('template.html', 'r') as f:
        page_template = f.read()

    with open('pie_template.js', 'r') as f:
        pie_template = f.read()

    with open('bar_template.js', 'r') as f:
        bar_template = f.read()

    script_tags = ''
    chart_divs = "<div class='chart_row'>"
    bar_datapoints = ''

    adjustment = 1 if include_this_week else 0

    for chart_number, week_number in enumerate(range(current_week_number - number_of_weeks - (1 - adjustment), current_week_number + adjustment)):
        if chart_number % 3 == 0:
            chart_divs += "</div><div class='chart_row'>"

        chart_divs += "<div id='chart{0}' class='chart'></div>".format(chart_number)

        week_total = 0
        week_payments = {}

        week_start_date = iso_to_gregorian(datetime.datetime.now().year, week_number, 1) # Monday
        week_start_date_str = week_start_date.strftime('{0} %b').format(get_suffix(week_start_date.day))
        week_end_date = iso_to_gregorian(datetime.datetime.now().year, week_number + 1, 0) # Sunday
        week_end_date_str = week_end_date.strftime('{0} %b').format(get_suffix(week_end_date.day))
        week_name = '{0} - {1}'.format(week_start_date_str, week_end_date_str)

        if week_number == current_week_number:
            week_name += ' (this week)'

        for payment in payments:
            if payment['Date'].isocalendar()[1] == week_number:
                week_total += payment['Amount']

                # Transform names
                # First pass
                payment['Name'] = re.sub('^CARD PAYMENT TO (.+?),.*$', r'\1', payment['Name'])
                payment['Name'] = re.sub('^CASH WITHDRAWAL .*', 'ATM Withdrawl', payment['Name'])
                payment['Name'] = re.sub('^DIRECT DEBIT PAYMENT TO PAYPAL.*', 'PayPal', payment['Name'])
                payment['Name'] = re.sub('&amp;', r'&', payment['Name'])

                # Second pass
                payment['Name'] = re.sub('(TESCO)(\s|-)(?:STORES \d\d\d\d|METRO)', r'\1', payment['Name'])
                payment['Name'] = re.sub('LUL TICKET MACHINE', 'Oyster Topup', payment['Name'])

                # Put payments into buckets by name
                if week_payments.get(payment['Name']) is None:
                    week_payments[payment['Name']] = payment['Amount']
                else:
                    week_payments[payment['Name']] += payment['Amount']

        datapoint_template = '''{{
                                    name: "{0}",
                                    y: {1}
                                }}, '''

        pie_datapoints = ''
        week_payments_sorted = sorted(week_payments.items(), key=operator.itemgetter(1), reverse=True)
        for name, amount in week_payments_sorted:
            percentage = (amount / week_total) * 100
            pie_datapoints += datapoint_template.format('{0} - £{1}'.format(name, amount), percentage)

        bar_datapoints += datapoint_template.format('{0}'.format(week_name), week_total)

        chart_pie_template = pie_template 
        chart_pie_template = re.sub('{chart_number}', str(number_of_weeks - chart_number), chart_pie_template)
        chart_pie_template = re.sub('{week_name}', str(week_name), chart_pie_template)
        chart_pie_template = re.sub('{week_total}', str(week_total), chart_pie_template)
        chart_pie_template = re.sub('{datapoints}', pie_datapoints, chart_pie_template)

        script_tags += '<script>{0}</script>\n'.format(chart_pie_template)

    chart_bar_template = re.sub('{datapoints}', bar_datapoints, bar_template)
    script_tags += '<script>{0}</script>\n'.format(chart_bar_template)

    page_template = page_template.format(script_tags=script_tags, chart_divs=chart_divs)

    with open('charts.html', 'w+') as f:
        f.write(page_template)

def get_payments(statement_filename, bank):
    payments = []

    if bank == 'Santander':
        payment_pattern = 'Date:(.*)\sDescription:(.*)\sAmount:(.*)\s'
        card_payment_pattern = 'CARD PAYMENT .* ON (\d\d-\d\d-\d\d\d\d)'

        with open(statement_filename, 'r') as f:
            content = unicode(f.read(), errors='ignore').encode('ascii')
            matches = re.findall(payment_pattern, content)
            for match in matches:
                # Get original date of card payment
                card_payment_match = re.match(card_payment_pattern, match[1])
                if card_payment_match is not None:
                    date = datetime.datetime.strptime(card_payment_match.group(1), '%d-%m-%Y')
                else:
                    date = datetime.datetime.strptime(match[0], '%d/%m/%Y')

                amount = Decimal(match[2].replace('GBP', ''))

                if amount < 0:
                    payment = {
                        'Date': date,
                        'Name': match[1].strip(),
                        'Amount': abs(amount)}
                    payments.append(payment)

    return payments

def iso_year_start(iso_year):
    "The gregorian calendar date of the first day of the given ISO year"
    fourth_jan = datetime.date(iso_year, 1, 4)
    delta = datetime.timedelta(fourth_jan.isoweekday()-1)
    return fourth_jan - delta 

def iso_to_gregorian(iso_year, iso_week, iso_day):
    "Gregorian calendar date for the given ISO year, week and day"
    year_start = iso_year_start(iso_year)
    return year_start + datetime.timedelta(days=iso_day-1, weeks=iso_week-1)


def get_suffix(n):
    '''Horrible line-noise function for getting number ord suffixes'''
    return str(n) + ("th" if 4 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th"))

main()
