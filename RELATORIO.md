# 📋 Relatório do Projeto - Ryu Discord Bot

## Visão Geral

O **Nexus Discord Bot** é um bot completo e modular para Discord, desenvolvido em Python com `discord.py`, focado em **moderação avançada**, **automação** e **interações divertidas**. O bot foi projetado para ser escalável, fácil de manter e com funcionalidades que rivalizam com bots comerciais como Sapphire e Dyno.

---

## 🎯 Objetivos Alcançados

### ✅ Moderação Completa
- **Ban**: Banimento permanente com registro de logs
- **Kick**: Expulsão com motivo
- **Mute (Timeout)**: Silenciamento temporário (minutos, horas, dias)
- **Soft Ban**: Ban automático + unban (limpa mensagens)
- **Warn System**: Sistema de avisos com histórico
- **Purge**: Limpeza de mensagens em massa

### ✅ AutoMod Avançado
- **Filtro de Palavras**: Adicionar/remover palavras proibidas
- **Anti-Spam**: Detecta e remove spam automático
- **Modo Lento (Slowmode)**: Controla velocidade de mensagens
- **Logs Detalhados**: Todas as ações registradas em canal específico

### ✅ Gerenciamento de Cargos
- **Painel de Cargos**: Botões interativos para pegar/remover cargos
- **AutoRole**: Cargo automático ao entrar no servidor
- **Adicionar/Remover Cargos**: Gerenciamento manual

### ✅ Sistema de Tickets
- **Setup Automático**: Cria painel de suporte
- **Tickets Privados**: Apenas o usuário e staff veem
- **Fechamento Rápido**: Comando `!fechar` para encerrar

### ✅ Interações Divertidas
- **Box**: Cria caixas ASCII com texto
- **Curtir**: Reage com 👍 em mensagens aleatórias
- **Reação Automática**: 🔥 em mensagens com MAIÚSCULA

### ✅ Inteligência Artificial
- **Gemini AI**: Integração com Google Gemini para respostas inteligentes
- **Comando Pergunte**: Faz perguntas e recebe respostas da IA

### ✅ Sistema de Prefixo Dinâmico
- Cada servidor pode ter seu próprio prefixo
- Alterável com `!setprefix`

---

## 🏗️ Arquitetura do Bot

```
Ryu Bot
├── SystemCog
│   ├── !ajuda (menu interativo)
│   └── !setprefix (muda prefixo)
│
├── Moderation
│   ├── !ban @user [motivo]
│   ├── !kick @user [motivo]
│   ├── !mute @user 10m [motivo]
│   ├── !softban @user [motivo]
│   ├── !warn @user [motivo]
│   ├── !warns @user
│   ├── !purge [quantidade]
│   └── !setlogs #canal
│
├── AutoMod
│   ├── !addfilter palavra
│   ├── !removefilter palavra
│   ├── !listfilter
│   ├── !slow [segundos]
│   ├── !slowoff
│   ├── !antispam on/off
│   └── Listeners (filtro, anti-spam)
│
├── RoleManager
│   ├── !painel_cargos
│   ├── !setautorole @cargo
│   ├── !addrole @user @cargo
│   ├── !removerole @user @cargo
│   └── on_member_join (autorole automático)
│
├── TicketSystem
│   ├── !setup_ticket
│   └── !fechar
│
├── Interactions
│   ├── !box [texto]
│   ├── !curtir
│   └── on_message (reações automáticas)
│
└── AIFeatures
    └── !pergunte [pergunta]
```

---

## 📊 Estrutura do Banco de Dados

### Tabela: `settings`
Armazena configurações por servidor

| Campo | Tipo | Descrição |
|-------|------|-----------|
| guild_id | TEXT (PK) | ID do servidor |
| log_channel_id | TEXT | Canal de logs |
| autorole_id | TEXT | Cargo automático |
| prefix | TEXT | Prefixo customizado |
| antispam | INTEGER | Status do anti-spam |

### Tabela: `warns`
Histórico de avisos

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | INTEGER (PK) | ID único |
| user_id | TEXT | ID do usuário |
| guild_id | TEXT | ID do servidor |
| reason | TEXT | Motivo do aviso |
| admin_id | TEXT | ID do moderador |
| timestamp | DATETIME | Data/hora |

### Tabela: `filter_words`
Palavras filtradas

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | INTEGER (PK) | ID único |
| guild_id | TEXT | ID do servidor |
| word | TEXT | Palavra filtrada |

---

## 🔧 Recursos Técnicos

### Dependências
- `discord.py 2.3.2` - Biblioteca principal
- `aiosqlite 0.19.0` - Banco de dados async
- `python-dotenv 1.0.0` - Variáveis de ambiente
- `google-generativeai 0.3.0` - API Gemini

### Padrões de Código
- **Async/Await**: Todas as operações são assíncronas
- **Cogs**: Modularização em componentes reutilizáveis
- **Error Handling**: Tratamento de exceções em todos os comandos
- **Logging**: Sistema de logs detalhado por servidor
- **Cache**: Prefixos em cache para performance

### Segurança
- Verificação de permissões em todos os comandos
- Validação de entrada do usuário
- Proteção contra operações não autorizadas
- Tratamento de exceções para evitar crashes

---

## 🚀 Como Usar

### 1. Instalação
```bash
git clone <seu-repositorio>
cd Ryu-bot
pip install -r requirements.txt
```

### 2. Configuração
```bash
cp .env.example .env
# Edite .env com seu DISCORD_TOKEN
```

### 3. Executar
```bash
python bot.py
```

---

## 📈 Funcionalidades Futuras

### Dashboard Web
Um site de controle para gerenciar o bot em múltiplos servidores:
- **Painel de Estatísticas**: Visualizar atividade
- **Gerenciador de Configurações**: Alterar prefixo, logs, etc.
- **Visualizador de Warns**: Histórico de avisos
- **Gerenciador de Filtros**: Adicionar/remover palavras
- **Logs em Tempo Real**: Monitorar ações do bot

### Melhorias Planejadas
- Sistema de reputação/pontos
- Comandos de diversão (8ball, dice, etc.)
- Sistema de leveling
- Integração com APIs externas
- Suporte a slash commands
- Painel de customização de embeds

---

## 📝 Notas de Desenvolvimento

### Estrutura Modular
O bot foi desenvolvido com **Cogs**, permitindo fácil adição de novos módulos sem modificar o arquivo principal.

### Banco de Dados
Utiliza SQLite com operações assíncronas para não bloquear o bot durante consultas.

### Tratamento de Erros
Todos os comandos possuem try-except para evitar que erros derrubem o bot.

### Performance
- Cache de prefixos para reduzir consultas ao banco
- Operações assíncronas para não bloquear eventos
- Limite de purge em 100 mensagens para segurança

---

## 🎓 Conclusão

O **Nexus Discord Bot** é uma solução completa e profissional para moderação e gerenciamento de servidores Discord. Com uma arquitetura modular, funcionalidades robustas e código bem documentado, ele está pronto para ser expandido e personalizado conforme necessário.

O bot demonstra boas práticas de desenvolvimento Python, incluindo async/await, tratamento de erros, modularização e segurança.
