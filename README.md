# Sistema Distribuído de Processamento de Imagens com IA e RabbitMQ

Sistema distribuído desenvolvido em Java que utiliza RabbitMQ para processamento assíncrono de imagens com IA embutida, detectando expressões faciais e identificando times de futebol.

## 📋 Descrição do Sistema

O projeto implementa um sistema de processamento distribuído composto por 4 containers que trabalham em conjunto para gerar, enfileirar e processar imagens utilizando diferentes modelos de IA.

## 🏗️ Arquitetura

```
┌─────────────┐      ┌──────────────┐      ┌─────────────────┐
│   Producer  │─────>│   RabbitMQ   │─────>│  Consumer Face  │
│  (Gerador)  │      │ Topic Exchange│      │   (IA Smile)    │
└─────────────┘      │              │      └─────────────────┘
                     │              │
                     │              │      ┌─────────────────┐
                     └──────────────┘─────>│  Consumer Team  │
                                            │   (IA Smile)    │
                                            └─────────────────┘
```

### Componentes

1. **Producer (Gerador de Mensagens)**
   - Gera 5+ mensagens por segundo
   - Alterna entre imagens de faces e brasões de times
   - Publica com routing keys: `face` e `team`

2. **RabbitMQ (Message Broker)**
   - Topic Exchange para roteamento inteligente
   - Interface de administração habilitada (porta 15672)
   - Filas separadas para faces e times

3. **Consumer Face (Consumidor 1)**
   - Processa imagens de rostos
   - IA: Análise de sentimento/expressão (feliz/triste)
   - Biblioteca: **Smile (Statistical Machine Intelligence & Learning Engine)**
   - Processamento mais lento que geração (fila cresce)

4. **Consumer Team (Consumidor 2)**
   - Processa imagens de brasões de times
   - IA: Identificação de time de futebol
   - Biblioteca: **Smile (Statistical Machine Intelligence & Learning Engine)**
   - Processamento mais lento que geração (fila cresce)

## 📁 Estrutura do Projeto

```
sistema-carga-ia/
├── producer/
│   ├── Dockerfile
│   ├── pom.xml
│   └── src/
│       └── main/
│           └── java/
│               └── MessageProducer.java
├── consumer-face/
│   ├── Dockerfile
│   ├── pom.xml
│   └── src/
│       └── main/
│           └── java/
│               └── FaceConsumer.java
├── consumer-team/
│   ├── Dockerfile
│   ├── pom.xml
│   └── src/
│       └── main/
│           └── java/
│               └── TeamConsumer.java
├── datasets/
│   ├── faces/           # Imagens de rostos
│   └── teams/           # Brasões de times
├── docker-compose.yml
└── README.md
```

## 🚀 Como Executar

### Pré-requisitos

- Docker 20.10+
- Docker Compose 1.29+
- 4GB RAM disponível

### Passo a Passo

1. **Clone o repositório**
```bash
git clone https://github.com/DanielRodri87/RabbitMQ.git
cd RabbitMQ
```

2. **Construa e inicie os containers**
```bash
docker-compose up -
```

3. **Monitore as filas**
   - Observe o crescimento das filas `face_queue` e `team_queue`
   - Veja as mensagens sendo processadas em tempo real

4. **Para parar o sistema**
```bash
docker-compose build --no-cache
docker-compose up
```

## 🔧 Tecnologias Utilizadas

### Linguagem e Framework
- **Java 11+** (JDK 11 ou superior)
- **Maven** (Gerenciamento de dependências)

### Bibliotecas Principais
- **RabbitMQ Java Client** (amqp-client 5.x)
- **Smile ML Library** (Statistical Machine Intelligence & Learning Engine)
  - `com.github.haifengl:smile-core`
  - `com.github.haifengl:smile-nlp`
- **SLF4J** (Logging)

### Infraestrutura
- **Docker** (Containerização)
- **Docker Compose** (Orquestração)
- **RabbitMQ 3.13** (Message Broker)

## ⚙️ Configuração do RabbitMQ

### Topic Exchange
```
Exchange Name: image_exchange
Type: topic
Durable: true
Auto-delete: false
```

### Routing Keys
- `image.face` → Fila `face_queue`
- `image.team` → Fila `team_queue`

### Filas
```
face_queue:
  - Binding: image.face
  - Durable: true
  
team_queue:
  - Binding: image.team
  - Durable: true
```

## 🤖 Inteligência Artificial

### Consumer Face - Análise de Sentimento
- **Biblioteca**: Smile ML
- **Modelo**: Classificação de expressões faciais
- **Classes**: Feliz, Triste, Neutro, Surpreso, Raiva, Medo, Nojo
- **Input**: Imagem de rosto (Base64)
- **Output**: Emoção detectada + confiança

### Consumer Team - Identificação de Times
- **Biblioteca**: Smile ML
- **Modelo**: Classificação de imagens
- **Classes**: Times brasileiros (Flamengo, Corinthians, Palmeiras, São Paulo, etc.)
- **Input**: Imagem de brasão (Base64)
- **Output**: Time identificado + confiança

## 📊 Características do Sistema

### Performance
- ✅ Geração: 5+ mensagens/segundo
- ✅ Processamento: Intencionalmente mais lento
- ✅ Fila: Cresce visivelmente no RabbitMQ
- ✅ Containerização: Todos os serviços isolados
- ✅ Network: Docker network compartilhada

### Observabilidade
- Interface RabbitMQ Management para monitoramento
- Logs estruturados em cada container
- Métricas de fila em tempo real
- Visualização de taxa de produção vs consumo

## 📦 Dependências Maven (pom.xml)

```xml
<dependencies>
    <!-- RabbitMQ -->
    <dependency>
        <groupId>com.rabbitmq</groupId>
        <artifactId>amqp-client</artifactId>
        <version>5.20.0</version>
    </dependency>
    
    <!-- Smile ML -->
    <dependency>
        <groupId>com.github.haifengl</groupId>
        <artifactId>smile-core</artifactId>
        <version>3.0.2</version>
    </dependency>
    
    <!-- JSON Processing -->
    <dependency>
        <groupId>com.google.code.gson</groupId>
        <artifactId>gson</artifactId>
        <version>2.10.1</version>
    </dependency>
    
    <!-- Logging -->
    <dependency>
        <groupId>org.slf4j</groupId>
        <artifactId>slf4j-simple</artifactId>
        <version>2.0.9</version>
    </dependency>
</dependencies>
```

## 🐳 Docker Network

Todos os containers estão conectados na mesma rede Docker:

```yaml
networks:
  rabbitmq-network:
    driver: bridge
```

Isso permite comunicação entre os serviços usando nomes de host.

## 📈 Monitoramento

### Via Logs
```bash
# Producer
docker-compose logs -f producer

# Consumer Face
docker-compose logs -f consumer-face

# Consumer Team
docker-compose logs -f consumer-team
```

## 🔍 Troubleshooting

### Filas não estão crescendo
- Verifique se o processamento está realmente mais lento
- Aumente o delay nos consumidores (Thread.sleep)
- Reduza recursos do container

### Consumidores não recebem mensagens
- Verifique as bindings no RabbitMQ
- Confirme as routing keys no producer
- Verifique a conectividade da rede Docker

### Erro de conexão com RabbitMQ
- Aguarde o RabbitMQ inicializar completamente (health check)
- Verifique se a porta 5672 está disponível

## 📝 Notas de Implementação

- Os consumidores processam propositalmente mais devagar que o producer
- Isso simula um cenário real de carga alta
- A fila do RabbitMQ deve crescer visivelmente
- Imagens são transmitidas em Base64 via JSON

## 👥 Autores

[Seu Nome] - [Seu Email/GitHub]

## 📄 Licença

Este projeto foi desenvolvido para fins acadêmicos.



## 🔗 Links Úteis

- [RabbitMQ Documentation](https://www.rabbitmq.com/documentation.html)
- [Smile ML Library](https://haifengl.github.io/)
- [Docker Documentation](https://docs.docker.com/)
- [Java AMQP Client](https://www.rabbitmq.com/java-client.html)