# 🏃‍♂️ WhatsApp Strava Bot

Bot para WhatsApp que monitora corridas dos integrantes de um grupo através do Strava, envia notificações automáticas e gera rankings semanais e mensais.

## 📋 Funcionalidades

- ✅ **Notificações automáticas** quando alguém completar uma corrida no Strava
- 📊 **Ranking semanal** de quilômetros percorridos
- 📊 **Ranking mensal** de quilômetros percorridos
- 🏃 **Estatísticas detalhadas** (distância, tempo, pace médio)
- 🐳 **Docker ready** para fácil deployment
- 🔄 **Integração em tempo real** com Strava via webhooks

## 🚀 Início Rápido

### Pré-requisitos

- Docker e Docker Compose
- Conta Strava Developer
- Número de telefone para WhatsApp Web

### 1. Criar aplicação no Strava

1. Acesse https://www.strava.com/settings/api
2. Crie uma nova aplicação
3. Anote o **Client ID** e **Client Secret**
4. Defina a **Authorization Callback Domain** como `localhost` (para desenvolvimento)

### 2. Clonar e configurar

```bash
# Clone o repositório
cd whatsapp-strava-bot

# Copie o arquivo de exemplo
cp .env.example .env

# Edite o arquivo .env com suas credenciais
nano .env
```

### 3. Configurar variáveis de ambiente

Edite o arquivo `.env`:

```env
# Strava API (obtenha em https://www.strava.com/settings/api)
STRAVA_CLIENT_ID=seu_client_id
STRAVA_CLIENT_SECRET=seu_client_secret
STRAVA_VERIFY_TOKEN=qualquer_string_aleatoria_segura

# URL pública do webhook (para produção, use ngrok ou domínio real)
WEBHOOK_URL=https://seu-dominio.com
WEBHOOK_PORT=8000

# ID do grupo WhatsApp (será obtido após primeira execução)
WHATSAPP_GROUP_ID=

# Fuso horário
TIMEZONE=America/Sao_Paulo
```

### 4. Executar com Docker

```bash
# Build e start
docker-compose up --build

# Ou em background
docker-compose up -d --build

# Ver logs
docker-compose logs -f
```

### 5. Executar sem Docker (desenvolvimento)

```bash
# Instalar dependências Python
pip install -r requirements.txt

# Instalar dependências Node.js
npm install

# Executar
python src/main.py
```

## 📱 Configuração do WhatsApp

### Primeira execução

1. Execute o bot
2. Um QR Code aparecerá no terminal
3. Escaneie com WhatsApp no seu celular
4. Aguarde a mensagem "WhatsApp client is ready!"
5. O bot listará todos os grupos disponíveis

### Obter ID do grupo

Após o bot conectar, você verá uma lista assim:

```
📋 Available groups:
  - Corrida Galera: 123456789@g.us
  - Outro Grupo: 987654321@g.us
```

Copie o ID do grupo desejado e adicione no `.env`:

```env
WHATSAPP_GROUP_ID=123456789@g.us
```

## 🔗 Configuração do Strava

### Registrar atletas

Cada pessoa do grupo deve autorizar o app:

1. Acesse: `http://localhost:8000/strava/auth`
2. Copie a URL de autorização retornada
3. Abra no navegador e autorize o app
4. Você será redirecionado e o atleta será registrado

### Configurar webhook (produção)

Para receber notificações em tempo real, você precisa de uma URL pública.

#### Opção 1: Usar ngrok (desenvolvimento/teste)

```bash
# Instale ngrok: https://ngrok.com/
ngrok http 8000

# Copie a URL HTTPS fornecida (ex: https://abc123.ngrok.io)
# Atualize WEBHOOK_URL no .env
```

#### Opção 2: Deploy em servidor real

1. Deploy em servidor com IP público
2. Configure DNS e SSL
3. Atualize `WEBHOOK_URL` no `.env`

#### Registrar webhook no Strava

```bash
# Método 1: Via API do bot
curl http://localhost:8000/strava/webhook/subscribe

# Método 2: Manualmente via Strava API
curl -X POST https://www.strava.com/api/v3/push_subscriptions \
  -F client_id=SEU_CLIENT_ID \
  -F client_secret=SEU_CLIENT_SECRET \
  -F callback_url=https://seu-dominio.com/webhook \
  -F verify_token=SEU_VERIFY_TOKEN
```

Verificar inscrições:

```bash
curl http://localhost:8000/strava/webhook/subscriptions
```

## 💬 Comandos do Bot

Use estes comandos no grupo do WhatsApp:

- `/ranking-semanal` ou `/semanal` - Mostra ranking da semana atual
- `/ranking-mensal` ou `/mensal` - Mostra ranking do mês atual
- `/help` ou `/ajuda` - Lista todos os comandos

## 📊 Exemplo de Notificação

Quando alguém completar uma corrida:

```
🏃‍♂️ Nova Corrida Registrada!

👤 João Silva
📝 Corrida Matinal
📏 Distância: 10.50 km
⏱️ Tempo: 52:30
🏃 Pace: 5.00 min/km

Parabéns! 👏🎉
```

## 📈 Exemplo de Ranking

```
📊 Ranking Semanal - Corridas

🥇 João Silva
   📏 42.50 km em 5 corrida(s)
   ⏱️ Tempo total: 03:30:45
   🏃 Pace médio: 4.95 min/km

🥈 Maria Santos
   📏 35.20 km em 4 corrida(s)
   ⏱️ Tempo total: 02:58:12
   🏃 Pace médio: 5.08 min/km

🥉 Pedro Costa
   📏 28.75 km em 3 corrida(s)
   ⏱️ Tempo total: 02:25:30
   🏃 Pace médio: 5.05 min/km
```

## 🗂️ Estrutura do Projeto

```
whatsapp-strava-bot/
├── src/
│   ├── bot/
│   │   ├── whatsapp_client.py    # Cliente Python para WhatsApp
│   │   └── webhook_server.py     # Servidor FastAPI para webhooks
│   ├── database/
│   │   └── models.py             # Modelos SQLAlchemy
│   ├── rankings/
│   │   └── calculator.py         # Cálculo de rankings
│   ├── strava/
│   │   └── client.py             # Cliente Strava API
│   ├── whatsapp/
│   │   └── bot.js                # Bot WhatsApp (Node.js)
│   └── main.py                   # Entry point principal
├── data/                         # Banco de dados SQLite
├── config/                       # Arquivos de configuração
├── .env                          # Variáveis de ambiente
├── .env.example                  # Exemplo de .env
├── requirements.txt              # Dependências Python
├── package.json                  # Dependências Node.js
├── Dockerfile                    # Imagem Docker
├── docker-compose.yml            # Orquestração Docker
└── README.md                     # Esta documentação
```

## 🔧 API Endpoints

O bot expõe uma API REST:

- `GET /` - Health check
- `GET /webhook` - Verificação do webhook Strava
- `POST /webhook` - Receber eventos do Strava
- `GET /ranking/weekly` - Obter ranking semanal
- `GET /ranking/monthly` - Obter ranking mensal
- `GET /strava/auth` - URL de autorização Strava
- `GET /strava/callback` - Callback OAuth Strava
- `POST /strava/webhook/subscribe` - Registrar webhook
- `GET /strava/webhook/subscriptions` - Listar webhooks
- `GET /athletes` - Listar atletas registrados

API WhatsApp (porta 3000):

- `POST /send-message` - Enviar mensagem
- `GET /health` - Status do bot
- `GET /groups` - Listar grupos disponíveis

## 🐳 Docker

### Build e execução

```bash
# Build
docker-compose build

# Start
docker-compose up

# Stop
docker-compose down

# Ver logs
docker-compose logs -f bot

# Reconstruir e reiniciar
docker-compose up --build --force-recreate
```

### Volumes

- `./data:/app/data` - Banco de dados persistente
- `./config:/app/config` - Configurações
- `./.wwebjs_auth:/app/.wwebjs_auth` - Sessão WhatsApp

## 🚀 Deploy em Produção

### Opção 1: VPS/Cloud (Recomendado)

1. Configure servidor Ubuntu/Debian
2. Instale Docker e Docker Compose
3. Clone o repositório
4. Configure `.env` com domínio público
5. Configure SSL (Let's Encrypt)
6. Execute com `docker-compose up -d`

### Opção 2: Heroku

```bash
# Não recomendado devido a necessidade de sessão WhatsApp persistente
```

### Opção 3: AWS/GCP/Azure

- Use EC2/Compute Engine/VM
- Configure Security Groups/Firewall
- Use RDS/Cloud SQL para PostgreSQL (opcional)
- Configure Load Balancer com SSL

## 🛠️ Troubleshooting

### QR Code não aparece

- Verifique se o Chromium está instalado
- Execute sem Docker: `node src/whatsapp/bot.js`
- Verifique permissões de diretório `.wwebjs_auth`

### Webhook não recebe eventos

- Verifique se URL é HTTPS e pública
- Confirme que webhook está registrado: `GET /strava/webhook/subscriptions`
- Verifique logs: `docker-compose logs -f`
- Teste manualmente: `curl -X POST http://localhost:8000/webhook -H "Content-Type: application/json" -d '...'`

### Atleta não encontrado

- Certifique-se que o atleta autorizou o app
- Verifique se está no banco: `GET /athletes`
- Reautorize: `GET /strava/auth`

### Rankings vazios

- Verifique período (semana/mês atual)
- Confirme que atividades foram sincronizadas
- Apenas corridas (tipo "Run") são contabilizadas

## 📝 TODO

- [ ] Adicionar suporte para PostgreSQL
- [ ] Implementar refresh automático de tokens Strava
- [ ] Adicionar testes unitários
- [ ] Criar dashboard web para administração
- [ ] Suporte para múltiplos grupos
- [ ] Estatísticas avançadas (elevação, zonas de pace, etc)
- [ ] Notificações personalizáveis
- [ ] Sistema de metas e desafios

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

MIT License - sinta-se livre para usar este projeto!

## 🆘 Suporte

- Problemas? Abra uma issue
- Dúvidas? Consulte a documentação do Strava API
- WhatsApp Web.js docs: https://github.com/pedroslopez/whatsapp-web.js

## 🙏 Agradecimentos

- [Strava API](https://developers.strava.com/)
- [whatsapp-web.js](https://github.com/pedroslopez/whatsapp-web.js)
- [FastAPI](https://fastapi.tiangolo.com/)
- [stravalib](https://github.com/stravalib/stravalib)

---

Feito com ❤️ para corredores que amam competição saudável! 🏃‍♂️🏃‍♀️
