# AmazonInspectorfProcess(SNS)
Este script foi projetado para ser executado no AWS Lambda e não funcionará em outro lugar.

Quando configurado corretamente, o script recebe descobertas (notificações de problemas de segurança no formato JSON) do serviço Amazon Inspector na AWS, via SNS, e depois as formata e encaminha para um endereço de e-mail de destino de sua escolha.

Você DEVE alterar o valor de DEST_EMAIL_ADDR na linha 13, ou o script não funcionará.
