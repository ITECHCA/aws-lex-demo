import boto3

from Config import Config


class SetupLexBot:
    INTENT_NAME = 'GetWeather'

    def __init__(self) -> None:
        self.client = boto3.client('lex-models',
                                   region_name="us-east-1",
                                   aws_access_key_id=Config.get_aws_key(),
                                   aws_secret_access_key=Config.get_aws_secret())

    def create_bot(self, name: str, description: str):
        checksum = self.get_bot_checksum(name)
        if checksum is not None:
            response = self.client.put_bot(
                name=name,
                description=description,
                intents=[
                    {
                        'intentName': self.INTENT_NAME,
                        'intentVersion': '1',
                    },
                ],
                clarificationPrompt={
                    'messages': [
                        {
                            'contentType': 'PlainText',
                            'content': 'I\'m not 100% sure what you mean. Could you try phrasing that differently?',
                            'groupNumber': 1
                        },
                    ],
                    'maxAttempts': 3
                },
                abortStatement={
                    'messages': [
                        {
                            'contentType': 'PlainText',
                            'content': 'I\'m having a hard time understanding you. Let\'s Try this from the beginning.',
                            'groupNumber': 1
                        },
                    ]
                },
                idleSessionTTLInSeconds=5 * 60,
                voiceId='Joanna',
                locale='en-US',
                childDirected=False,
                checksum=checksum,
                createVersion=True
            )

        else:
            response = self.client.put_bot(
                name=name,
                description=description,
                intents=[
                    {
                        'intentName': self.INTENT_NAME,
                        'intentVersion': '1',
                    },
                ],
                clarificationPrompt={
                    'messages': [
                        {
                            'contentType': 'PlainText',
                            'content': 'I\'m not 100% sure what you mean. Could you try phrasing that differently?',
                            'groupNumber': 1
                        },
                    ],
                    'maxAttempts': 3
                },
                abortStatement={
                    'messages': [
                        {
                            'contentType': 'PlainText',
                            'content': 'I\'m having a hard time understanding you. Let\'s Try this from the beginning.',
                            'groupNumber': 1
                        },
                    ]
                },
                idleSessionTTLInSeconds=5 * 60,
                voiceId='Joanna',
                locale='en-US',
                childDirected=False,
                createVersion=True
            )

        return response

    def make_intents(self):
        checksum = self.get_intent_checksum()
        if checksum is not None:
            response = self.client.put_intent(
                name=self.INTENT_NAME,
                slots=self.get_slots(),
                sampleUtterances=self.get_sample_utterances(),
                fulfillmentActivity={
                    'type': 'CodeHook',
                    'codeHook': {
                        'uri': Config.get_lambda_uri(),
                        'messageVersion': '1.0'
                    }
                },
                checksum=checksum,
                createVersion=True
            )
        else:
            response = self.client.put_intent(
                name=self.INTENT_NAME,
                description='Main Intent',
                slots=self.get_slots(),
                sampleUtterances=self.get_sample_utterances(),
                fulfillmentActivity={
                    'type': 'CodeHook',
                    'codeHook': {
                        'uri': Config.get_lambda_uri(),
                        'messageVersion': '1.0'
                    }
                },
                createVersion=True
            )

        return response

    def get_intent_checksum(self):
        try:
            response = self.client.get_intent(
                name=self.INTENT_NAME,
                version="$LATEST"
            )
            return response['checksum']
        except:
            return None

    def get_bot_checksum(self, name):
        try:
            response = self.client.get_bot(
                name=name,
                versionOrAlias="$LATEST"
            )
            return response['checksum']
        except:
            return None

    def get_sample_utterances(self) -> list:
        with open("sample_utterances.txt") as sample_utterance_file:
            utterances = sample_utterance_file.read()
            return utterances.split("\n")

    def get_slots(self) -> list:
        return [
            {
                'name': 'location',
                'slotConstraint': 'Required',
                'slotType': 'AMAZON.US_CITY',
                'sampleUtterances': [],
                'valueElicitationPrompt': {
                    'messages': [
                        {
                            'contentType': 'PlainText',
                            'content': 'For what city?',
                            'groupNumber': 1
                        },
                        {
                            'contentType': 'PlainText',
                            'content': 'What city are we talking about?',
                            'groupNumber': 1
                        },
                    ],
                    'maxAttempts': 3,
                    'responseCard': 'string'
                }
            }
        ]

    def prep_lambda(self):
        lambda_client = boto3.client('lambda',
                                     region_name="us-east-1",
                                     aws_access_key_id=Config.get_aws_key(),
                                     aws_secret_access_key=Config.get_aws_secret())
        current_function = lambda_client.get_function_configuration(
            FunctionName=Config.get_lambda_uri(),
        )

        response = lambda_client.add_permission(
            FunctionName=Config.get_lambda_uri(),
            StatementId='lex-us-east-1-%s' % self.INTENT_NAME,
            Action='lambda:invokeFunction',
            Principal="lex.amazonaws.com",
            RevisionId=current_function['RevisionId']
        )

        return response


if __name__ == '__main__':
    setup = SetupLexBot()
    try:
        setup.prep_lambda()
    except:
        print("Lambda Permissions Already Set")

    setup.make_intents()
    setup.create_bot("WeatherDemo",
                     "Example Lex Bot for getting Weather Information")
