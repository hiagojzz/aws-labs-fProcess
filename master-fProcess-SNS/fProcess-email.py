# -----------------------------------
# git: @hiagojzz                    |
# contact: hiago_j@hotmail.com      |
# -----------------------------------

from __future__ import print_function
import boto3
import json
import datetime

sns = boto3.client('sns')
inspector = boto3.client('inspector')

# Topico SNS
SNS_TOPIC = "Inspetor-De-Pacotes-Delivery"

DEST_EMAIL_ADDR = "metroque@example.com"

# função rápida LAMBDA
enco = lambda obj: (
    obj.isoformat()
    if isinstance(obj, datetime.datetime)
    or isinstance(obj, datetime.date)
    else None
)

def lambda_handler(event, context):

    # extrair a mensagem e os eventos singulares
    message = event['Records'][0]['Sns']['Message']

    # pegar o inspetor de payload
    notificationType = json.loads(message)['event']

    # pular tudo exceto as notificações do report_finding
    if notificationType != "FINDING_REPORTED":
        print('Skipping notification that is not a new finding: ' + notificationType)
        return 1
    
    # extrair o achado do ARN
    findingArn = json.loads(message)['finding']

    # extrair os detalhes do achado
    response = inspector.describe_findings(findingArns = [ findingArn ], locale='EN_US')
    print(response)
    finding = response['findings'][0]
    
    # pule as partes que não são úteis
    title = finding['title']
    if title == "Unsupported Operating System or Version":
        print('Skipping finding: ', title)
        return 1
        
    if title == "No potential security issues found":
        print('Skipping finding: ', title)
        return 1
    
    # pegue a informação para enviar por e-mail.
    subject = title[:100] # truncar em @ 100 caracteres, SNS tem limite subjetivo
    messageBody = "Title:\n" + title + "\n\nDescription:\n" + finding['description'] + "\n\nRecommendation:\n" + finding['recommendation']
    
    # messageBody = json.dumps(finding, default=enco, indent=2)

    # cria um tópico SNS se for necessário
    response = sns.create_topic(Name = SNS_TOPIC)
    snsTopicArn = response['TopicArn']

    # checa se o sub-registro realmente existe
    subscribed = False
    response = sns.list_subscriptions_by_topic( TopicArn = snsTopicArn )

    nextPageToken = ""
    
    # lista a chamada da API
    while True:
        response = sns.list_subscriptions_by_topic(
            TopicArn = snsTopicArn,
            NextToken = nextPageToken
            )

        for subscription in response['Subscriptions']:
            if ( subscription['Endpoint'] == DEST_EMAIL_ADDR ):
                subscribed = True
                break
        
        if 'NextToken' not in response:
            break
        else:
            nextPageToken = response['NextToken']
       
        
    # cria a subescrição se necessário
    if ( subscribed == False ):
        response = sns.subscribe(
            TopicArn = snsTopicArn,
            Protocol = 'email',
            Endpoint = DEST_EMAIL_ADDR
            )

    # publica a notificação pro tópico
    response = sns.publish(
        TopicArn = snsTopicArn,
        Message = messageBody,
        Subject = subject
        )

    return 0
