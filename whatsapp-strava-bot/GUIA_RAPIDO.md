# 🚀 Guia Rápido - WhatsApp Strava Bot

## Instalação em 5 Passos

### 1️⃣ Criar App no Strava

1. Acesse: https://www.strava.com/settings/api
2. Clique em "Create New App"
3. Preencha:
   - **Application Name**: Bot WhatsApp Corridas
   - **Category**: Social
   - **Website**: http://localhost
   - **Authorization Callback Domain**: localhost
4. Copie **Client ID** e **Client Secret**

### 2️⃣ Configurar o Projeto

```bash
# Clone ou entre no diretório
cd whatsapp-strava-bot

# Copie o exemplo de configuração
cp .env.example .env

# Edite e adicione suas credenciais
nano .env
```

Configure no `.env`:
```env
STRAVA_CLIENT_ID=seu_id_aqui
STRAVA_CLIENT_SECRET=seu_secret_aqui
STRAVA_VERIFY_TOKEN=escolha_uma_senha_qualquer
WEBHOOK_URL=http://localhost:8000
```

### 3️⃣ Executar

**Com Docker (recomendado):**
```bash
chmod +x setup.sh
./setup.sh
# Escolha opção 1
```

**Sem Docker:**
```bash
pip install -r requirements.txt
npm install
python src/main.py
```

### 4️⃣ Conectar WhatsApp

1. Quando o bot iniciar, um QR Code aparecerá no terminal
2. Abra WhatsApp no celular
3. Vá em **Configurações** → **Aparelhos conectados**
4. Clique em **Conectar um aparelho**
5. Escaneie o QR Code
6. Aguarde mensagem: "WhatsApp client is ready!"

### 5️⃣ Configurar Grupo

Após conectar, você verá:
```
📋 Available groups:
  - Meu Grupo de Corrida: 120363041234567890@g.us
```

1. Copie o ID do seu grupo
2. Adicione no `.env`:
```env
WHATSAPP_GROUP_ID=120363041234567890@g.us
```
3. Reinicie o bot

## 🎯 Registrar Corredores

Cada pessoa do grupo precisa autorizar o app:

1. Acesse no navegador: http://localhost:8000/strava/auth
2. Copie a URL que aparecer
3. Cole no navegador e autorize
4. Pronto! 🎉

## ✅ Testar

1. Vá em https://www.strava.com
2. Adicione uma corrida de teste
3. O bot deve notificar no grupo do WhatsApp!

## 📱 Comandos no WhatsApp

No grupo, envie:
- `/semanal` - Ver ranking da semana
- `/mensal` - Ver ranking do mês
- `/ajuda` - Ver ajuda

## 🌐 Configurar Webhook (Para Notificações Automáticas)

### Desenvolvimento Local com ngrok

```bash
# Instale ngrok: https://ngrok.com/download
ngrok http 8000

# Copie a URL HTTPS (ex: https://abc123.ngrok.io)
```

Atualize `.env`:
```env
WEBHOOK_URL=https://abc123.ngrok.io
```

Registre o webhook:
```bash
curl http://localhost:8000/strava/webhook/subscribe
```

### Produção (Servidor Real)

1. Deploy em servidor com domínio
2. Configure SSL (Let's Encrypt)
3. Atualize `WEBHOOK_URL` no `.env`
4. Registre webhook com comando acima

## 🔍 Verificar Status

```bash
# Ver atletas registrados
curl http://localhost:8000/athletes

# Ver webhooks ativos
curl http://localhost:8000/strava/webhook/subscriptions

# Ver ranking semanal
curl http://localhost:8000/ranking/weekly
```

## ❓ Problemas Comuns

### QR Code não aparece
```bash
# Execute diretamente o bot WhatsApp
node src/whatsapp/bot.js
```

### Webhook não funciona
- ✅ Certifique-se que a URL é HTTPS
- ✅ Verifique se está pública (não localhost)
- ✅ Teste com ngrok primeiro

### Não recebe notificações
- ✅ Registre os atletas primeiro
- ✅ Configure o webhook
- ✅ Verifique se o grupo está correto no `.env`

### Bot desconecta do WhatsApp
- Mantenha o bot rodando continuamente
- Use Docker para maior estabilidade
- Em produção, use PM2 ou similar

## 📊 Fluxo Completo

```
Corredor faz corrida no Strava
         ↓
Strava envia webhook → Bot recebe
         ↓
Bot busca detalhes da corrida
         ↓
Salva no banco de dados
         ↓
Envia notificação no WhatsApp
         ↓
Corredor digita /semanal
         ↓
Bot calcula ranking → Mostra no grupo
```

## 🎯 Próximos Passos

1. ✅ Configure SSL para produção
2. ✅ Adicione todos os corredores
3. ✅ Personalize mensagens
4. ✅ Configure backup do banco de dados
5. ✅ Monitore logs regularmente

## 🆘 Precisa de Ajuda?

- Verifique o arquivo `README.md` completo
- Cheque os logs: `docker-compose logs -f`
- Consulte: https://developers.strava.com/docs/

---

Boas corridas! 🏃‍♂️💨
