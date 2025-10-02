# Sistema de Detecção de Faces e Times com RabbitMQ

Sistema distribuído que utiliza RabbitMQ para processamento assíncrono de imagens, detectando expressões faciais e times de futebol.

## Arquitetura

O sistema é composto por 4 serviços principais:

1. **RabbitMQ**: Message broker que gerencia a comunicação entre os serviços
2. **Producer**: Gera mensagens com imagens de faces e times
3. **Consumer-Face**: Processa imagens de faces (48x48px)
4. **Consumer-Team**: Processa imagens de times (512x512px)

## Estrutura de Diretórios

```
.
├── dataset-face/          # Dataset de expressões faciais
│   └── train/            # Imagens de treino (48x48px)
│       ├── angry/
│       ├── disgust/
│       ├── fear/
│       ├── happy/
│       ├── neutral/
│       ├── sad/
│       └── surprise/
├── dataset-team/         # Dataset de times brasileiros
│   ├── corinthians/
│   ├── cruzeiro/
│   ├── flamengo/
│   └── palmeiras/
├── results/             # Resultados do processamento
│   ├── faces/          # Imagens processadas de faces
│   └── teams/          # Imagens processadas de times
├── consumer.py         # Consumidor de faces
├── consumer_team.py    # Consumidor de times
├── producer.py         # Produtor de mensagens
└── docker-compose.yml  # Configuração dos containers
```

## Funcionamento

### Producer
- Gera mensagens alternando entre faces e times
- Processa 10 faces e depois foca apenas em times
- Taxa de 5 mensagens por segundo (200ms de intervalo)

### Consumer-Face
- Processa imagens 48x48 de expressões faciais
- Adiciona bounding box e rótulo da emoção
- Para após processar 10 imagens
- Salva resultados em /results/faces

### Consumer-Team
- Processa imagens 512x512 de escudos
- Adiciona nome do time na parte inferior
- Continua processando indefinidamente
- Salva resultados em /results/teams

## Como Executar

1. Preparar ambiente:
```bash
mkdir -p results/faces results/teams
```

2. Iniciar os serviços:
```bash
docker-compose up --build
```

3. Monitorar RabbitMQ:
- Interface web: http://localhost:15672
- Credenciais: guest/guest

## Tecnologias Utilizadas

- Python 3.8+
- RabbitMQ 3.13
- OpenCV
- Docker & Docker Compose
- Ubuntu 20.04 (base image)

## Características

- Comunicação assíncrona via RabbitMQ
- Topic Exchange para roteamento de mensagens
- Containerização completa
- Processamento em paralelo
- Health check no RabbitMQ
- Persistência de resultados

## Limitações

- Processamento facial limitado a 10 imagens
- Sem treinamento real de IA (simulado)
- Detecção facial simplificada para imagens 48x48
