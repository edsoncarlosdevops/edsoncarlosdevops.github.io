const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const express = require('express');
const axios = require('axios');
require('dotenv').config();

const app = express();
app.use(express.json());

// Initialize WhatsApp client
const client = new Client({
    authStrategy: new LocalAuth({
        dataPath: './.wwebjs_auth'
    }),
    puppeteer: {
        args: ['--no-sandbox', '--disable-setuid-sandbox'],
        executablePath: process.env.PUPPETEER_EXECUTABLE_PATH || undefined
    }
});

let isReady = false;
let groupId = process.env.WHATSAPP_GROUP_ID || null;

// QR Code generation
client.on('qr', (qr) => {
    console.log('📱 Scan this QR code with WhatsApp:');
    qrcode.generate(qr, { small: true });
});

// Client ready
client.on('ready', () => {
    console.log('✅ WhatsApp client is ready!');
    isReady = true;

    // List all groups to help find the group ID
    client.getChats().then(chats => {
        console.log('\n📋 Available groups:');
        chats.forEach(chat => {
            if (chat.isGroup) {
                console.log(`  - ${chat.name}: ${chat.id._serialized}`);
            }
        });
        console.log('\nSet WHATSAPP_GROUP_ID in .env file with your group ID\n');
    });
});

// Handle incoming messages
client.on('message', async (message) => {
    const chat = await message.getChat();

    // Only respond in the configured group or if no group is set
    if (groupId && chat.id._serialized !== groupId) {
        return;
    }

    const body = message.body.toLowerCase();

    try {
        if (body === '/ranking-semanal' || body === '/semanal') {
            const response = await axios.get('http://localhost:8000/ranking/weekly');
            await chat.sendMessage(response.data.message);
        } else if (body === '/ranking-mensal' || body === '/mensal') {
            const response = await axios.get('http://localhost:8000/ranking/monthly');
            await chat.sendMessage(response.data.message);
        } else if (body === '/help' || body === '/ajuda') {
            const helpMessage = `🏃‍♂️ *Bot de Corridas - Comandos Disponíveis*\n\n` +
                `/ranking-semanal ou /semanal - Ranking da semana\n` +
                `/ranking-mensal ou /mensal - Ranking do mês\n` +
                `/help ou /ajuda - Esta mensagem de ajuda\n\n` +
                `O bot notifica automaticamente quando alguém completa uma corrida no Strava! 🎉`;
            await chat.sendMessage(helpMessage);
        }
    } catch (error) {
        console.error('Error handling message:', error);
        await chat.sendMessage('❌ Erro ao processar comando. Tente novamente mais tarde.');
    }
});

// Initialize WhatsApp client
client.initialize();

// API endpoint to send messages from Python
app.post('/send-message', async (req, res) => {
    if (!isReady) {
        return res.status(503).json({ error: 'WhatsApp client not ready' });
    }

    const { message, groupId: targetGroupId } = req.body;
    const targetId = targetGroupId || groupId;

    if (!targetId) {
        return res.status(400).json({ error: 'No group ID configured' });
    }

    try {
        const chat = await client.getChatById(targetId);
        await chat.sendMessage(message);
        res.json({ success: true });
    } catch (error) {
        console.error('Error sending message:', error);
        res.status(500).json({ error: error.message });
    }
});

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({ status: isReady ? 'ready' : 'initializing' });
});

// Get list of groups
app.get('/groups', async (req, res) => {
    if (!isReady) {
        return res.status(503).json({ error: 'WhatsApp client not ready' });
    }

    try {
        const chats = await client.getChats();
        const groups = chats
            .filter(chat => chat.isGroup)
            .map(chat => ({
                id: chat.id._serialized,
                name: chat.name
            }));
        res.json({ groups });
    } catch (error) {
        console.error('Error getting groups:', error);
        res.status(500).json({ error: error.message });
    }
});

const PORT = process.env.WHATSAPP_API_PORT || 3000;
app.listen(PORT, () => {
    console.log(`🚀 WhatsApp API listening on port ${PORT}`);
});
