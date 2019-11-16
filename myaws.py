from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_model.ui import SimpleCard
from mta import get_stop_times
import logging

log = logging.getLogger()
logging.basicConfig(level=logging.INFO)

# Create the Lambda handler for alexa. The handler contains a LaunchRequest handler and
# standard intent handlers for help, cancel and ending. the launch request handler is the handler
# that gets the train times and returns those times converted to speech.

# this file defines the handlers first and constructs the lamba handler at the end using
# the AWS SDK skill builder.


# utility function to convert train times to text.
# train times is an array of numbers which represent minutes to the next train.
def getwords(traintimes):
    if len(traintimes) == 0:
        return 'No L trains found.'
    elif len(traintimes == 1):
        return "The next L train leaves in {0} minutes.".format(traintimes[0])
    else:
        words = 'The next L trains leave in '
        for ct in range(0, len(traintimes - 2)): # treat the last time differently.
            words += "{0}, ".format(traintimes[ct])
        words += " and {0} minutes.", traintimes[len(traintimes - 1)]
    return words


# handle launch request. this is the only class that delivers train times.
# we only respond to launch requests, not other intents to simplify the interaction model.
class LaunchRequestHandler(AbstractRequestHandler):

    # returns true if we can handle the launch request
    def can_handle(self, handler_input):
        log.info('signalling can handle launch request')
        return is_request_type("LaunchRequest")(handler_input)

    # handle the actual launch request by getting the train times and converting to speech
    def handle(self, handler_input):
        log.info('handling launch request...')
        traintimes = get_stop_times()
        speech_text = getwords(traintimes)
        log.info('{0} train times found.'.format(len(traintimes)))

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("L Train Times", speech_text)).set_should_end_session(
            False)
        log.info('returning response to launch request')
        return handler_input.response_builder.response


# required methods to handle alexa cancel/stop intents.
class CancelAndStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.CancelIntent")(handler_input) \
               or is_intent_name("AMAZON.StopIntent")(handler_input)

    def handle(self, handler_input):
        speech_text = "Goodbye!"
        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Train Times", speech_text)).set_should_end_session(True)
        return handler_input.response_builder.response


# session end handler and cleanup.
class SessionEndedRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # add cleanup logic here if needed (it isn't currently).
        return handler_input.response_builder.response


# catch-all exception handler
class AllExceptionHandler(AbstractExceptionHandler):

    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        print(exception) # Log the exception in CloudWatch Logs
        log.info('exception handler fired. {0}'.format(exception))

        speech = "Sorry! I couldn't do that."
        handler_input.response_builder.speak(speech).ask(speech)
        return handler_input.response_builder.response


# create the lambda handler with the request handlers.
sb = SkillBuilder()
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(CancelAndStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_exception_handler(AllExceptionHandler())

handler = sb.lambda_handler()
