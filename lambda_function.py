"""
This sample demonstrates an implementation of the Lex Code Hook Interface
in order to serve a sample bot which manages reservations for hotel rooms and car rentals.
Bot, Intent, and Slot models which are compatible with this sample can be found in the Lex Console
as part of the 'BookTrip' template.

For instructions on how to set up and test this bot, as well as additional samples,
visit the Lex Getting Started documentation http://docs.aws.amazon.com/lex/latest/dg/getting-started.html.
"""

from botocore.vendored import requests

import time
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

WUNDERGROUND_API_KEY = "YOUR API KEY"

# --- Helpers that build all of the responses ---


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }


def confirm_intent(session_attributes, intent_name, slots, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ConfirmIntent',
            'intentName': intent_name,
            'slots': slots,
            'message': message
        }
    }


def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response


def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }


# --- Helper Functions ---


def safe_int(n):
    """
    Safely convert n value to int.
    """
    if n is not None:
        return int(n)
    return n


def try_ex(func):
    """
    Call passed in function in try block. If KeyError is encountered return None.
    This function is intended to be used to safely access dictionary.

    Note that this function would have negative impact on performance.
    """

    try:
        return func()
    except KeyError:
        return None


""" --- Functions that control the bot's behavior --- """


def get_weather(intent_request):
    try:
        location = intent_request['currentIntent']['slots']['location']
    except KeyError:
        location = intent_request['currentIntent']['slots']['Location']

    session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}

    logger.debug("Location = " + location)
    complete_location = requests.get("http://autocomplete.wunderground.com/aq?c=US&query=" + location).json()
    location_quick_link = complete_location['RESULTS'][0]['l']

    response = ""

    # Add Current Conditions to Response
    current_weather = requests.get("http://api.wunderground.com/api/%s/conditions/%s.json" % (
        WUNDERGROUND_API_KEY,
        location_quick_link
    )).json()

    response += "Currently in %s, it is %.1f degrees fahrenheit, with winds %s. " % (
        current_weather['current_observation']['display_location']['full'],
        current_weather['current_observation']['temp_f'],
        current_weather['current_observation']['wind_string']
    )

    # Add Forecast to Response
    forecast = requests.get("http://api.wunderground.com/api/%s/forecast/%s.json" % (
        WUNDERGROUND_API_KEY,
        location_quick_link
    )).json()

    response += "The forecast for today from WeatherUnderground has %s" % forecast['forecast']['txt_forecast']['forecastday'][0]['fcttext']

    # Submit Response back to Lex
    return close(
        session_attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': response
        }
    )


# --- Intents ---


def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'GetWeather':
        return get_weather(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')


# --- Main handler ---


def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))

    return dispatch(event)
