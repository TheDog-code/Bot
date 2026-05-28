# 🌳 Árvore de Funcionalidades - Ryu Discord Bot

```
Ryu DISCORD BOT
│
├── 👮 MODERAÇÃO
│   ├── Ban
│   │   └── !ban @user [motivo]
│   │       ├── Remove usuário permanentemente
│   │       ├── Registra em logs
│   │       └── Requer permissão: ban_members
│   │
│   ├── Kick
│   │   └── !kick @user [motivo]
│   │       ├── Expulsa usuário do servidor
│   │       ├── Registra em logs
│   │       └── Requer permissão: kick_members
│   │
│   ├── Mute (Timeout)
│   │   └── !mute @user 10m [motivo]
│   │       ├── Formatos: 10m, 1h, 1d
│   │       ├── Silencia temporariamente
│   │       ├── Registra em logs
│   │       └── Requer permissão: moderate_members
│   │
│   ├── Soft Ban
│   │   └── !softban @user [motivo]
│   │       ├── Ban + Unban automático
│   │       ├── Limpa todas as mensagens
│   │       ├── Registra em logs
│   │       └── Requer permissão: ban_members
│   │
│   ├── Sistema de Avisos
│   │   ├── !warn @user [motivo]
│   │   │   ├── Adiciona aviso ao usuário
│   │   │   ├── Registra em banco de dados
│   │   │   ├── Registra em logs
│   │   │   └── Requer permissão: moderate_members
│   │   │
│   │   └── !warns @user
│   │       ├── Exibe todos os avisos
│   │       ├── Mostra motivos
│   │       └── Consulta banco de dados
│   │
│   ├── Purge (Limpeza)
│   │   └── !purge [quantidade]
│   │       ├── Máximo 100 mensagens
│   │       ├── Deleta do canal atual
│   │       └── Requer permissão: manage_messages
│   │
│   └── Logs
│       └── !setlogs #canal
│           ├── Define canal de logs
│           ├── Registra todas as ações
│           └── Requer permissão: administrator
│
├── 🤖 AUTOMOD
│   ├── Filtro de Palavras
│   │   ├── !addfilter palavra
│   │   │   ├── Adiciona palavra à lista negra
│   │   │   ├── Armazena em banco de dados
│   │   │   └── Requer permissão: administrator
│   │   │
│   │   ├── !removefilter palavra
│   │   │   ├── Remove palavra da lista negra
│   │   │   └── Requer permissão: administrator
│   │   │
│   │   └── !listfilter
│   │       └── Exibe todas as palavras filtradas
│   │
│   ├── Anti-Spam
│   │   ├── !antispam on/off
│   │   │   ├── Ativa/desativa proteção
│   │   │   ├── Detecta 5+ mensagens em 5s
│   │   │   └── Requer permissão: administrator
│   │   │
│   │   └── Listener automático
│   │       ├── Monitora velocidade de mensagens
│   │       ├── Deleta mensagens de spam
│   │       └── Avisa o usuário
│   │
│   ├── Modo Lento (Slowmode)
│   │   ├── !slow [segundos]
│   │   │   ├── Ativa modo lento no canal
│   │   │   ├── Padrão: 5 segundos
│   │   │   └── Requer permissão: administrator
│   │   │
│   │   └── !slowoff
│   │       ├── Desativa modo lento
│   │       └── Requer permissão: administrator
│   │
│   └── Listener de Filtro
│       ├── Monitora mensagens
│       ├── Detecta palavras proibidas
│       ├── Deleta automaticamente
│       └── Avisa o usuário
│
├── 🎭 GERENCIAMENTO DE CARGOS
│   ├── Painel de Cargos
│   │   └── !painel_cargos
│   │       ├── Cria botões interativos
│   │       ├── Mostra 3 últimos cargos
│   │       ├── Usuários clicam para pegar/remover
│   │       └── Requer permissão: administrator
│   │
│   ├── AutoRole
│   │   ├── !setautorole @cargo
│   │   │   ├── Define cargo automático
│   │   │   ├── Armazena em banco de dados
│   │   │   └── Requer permissão: administrator
│   │   │
│   │   └── Listener on_member_join
│   │       ├── Monitora entrada de membros
│   │       ├── Adiciona cargo automaticamente
│   │       └── Sem intervenção necessária
│   │
│   ├── Adicionar Cargo
│   │   └── !addrole @user @cargo
│   │       ├── Adiciona cargo manualmente
│   │       ├── Valida hierarquia de cargos
│   │       └── Requer permissão: manage_roles
│   │
│   └── Remover Cargo
│       └── !removerole @user @cargo
│           ├── Remove cargo do usuário
│           └── Requer permissão: manage_roles
│
├── 🎫 SISTEMA DE TICKETS
│   ├── Setup
│   │   └── !setup_ticket
│   │       ├── Cria painel de suporte
│   │       ├── Adiciona botão "Abrir Ticket"
│   │       └── Requer permissão: administrator
│   │
│   ├── Criação de Ticket
│   │   └── Botão "Abrir Ticket"
│   │       ├── Cria categoria "Tickets"
│   │       ├── Cria canal privado
│   │       ├── Apenas usuário + staff veem
│   │       └── Sem permissão necessária
│   │
│   └── Fechamento
│       └── !fechar
│           ├── Detecta canal de ticket
│           ├── Aguarda 3 segundos
│           └── Deleta o canal
│
├── 🎮 INTERAÇÕES DIVERTIDAS
│   ├── Box ASCII
│   │   └── !box [texto]
│   │       ├── Cria caixa com bordas
│   │       ├── Suporta múltiplas linhas
│   │       └── Sem permissão necessária
│   │
│   ├── Curtir Aleatório
│   │   └── !curtir
│   │       ├── Busca 50 mensagens anteriores
│   │       ├── Reage com 👍 aleatoriamente
│   │       └── Sem permissão necessária
│   │
│   └── Reação Automática
│       └── Listener on_message
│           ├── Detecta mensagens com MAIÚSCULA
│           ├── Reage com 🔥 automaticamente
│           └── Sem intervenção necessária
│
├── 🧠 INTELIGÊNCIA ARTIFICIAL
│   └── Pergunte
│       └── !pergunte [pergunta]
│           ├── Integração com Gemini AI
│           ├── Responde qualquer pergunta
│           ├── Respostas até 2000 caracteres
│           ├── Requer GEMINI_API_KEY configurada
│           └── Sem permissão necessária
│
├── ⚙️ SISTEMA
│   ├── Menu de Ajuda
│   │   └── !ajuda
│   │       ├── Exibe menu interativo
│   │       ├── Seletor de categorias
│   │       ├── Mostra comandos por categoria
│   │       └── Sem permissão necessária
│   │
│   └── Prefixo Customizado
│       └── !setprefix [novo]
│           ├── Muda prefixo do servidor
│           ├── Armazena em banco de dados
│           ├── Cache para performance
│           └── Requer permissão: administrator
│
└── 💾 BANCO DE DADOS
    ├── Tabela: settings
    │   ├── guild_id (chave primária)
    │   ├── log_channel_id
    │   ├── autorole_id
    │   ├── prefix
    │   └── antispam
    │
    ├── Tabela: warns
    │   ├── id (chave primária)
    │   ├── user_id
    │   ├── guild_id
    │   ├── reason
    │   ├── admin_id
    │   └── timestamp
    │
    └── Tabela: filter_words
        ├── id (chave primária)
        ├── guild_id
        └── word
```

---

## 📊 Resumo Estatístico

| Categoria | Quantidade |
|-----------|-----------|
| Comandos de Moderação | 7 |
| Comandos de AutoMod | 6 |
| Comandos de Cargos | 4 |
| Comandos de Tickets | 2 |
| Comandos de Interação | 2 |
| Comandos de IA | 1 |
| Comandos de Sistema | 2 |
| **Total de Comandos** | **24** |
| Listeners (Automáticos) | 5 |
| Tabelas de Banco de Dados | 3 |

---

## 🎯 Fluxo de Execução

```
Mensagem recebida
    ↓
[Listener on_message]
    ├─→ Filtro de palavras? → Deleta + Avisa
    ├─→ Anti-spam? → Deleta + Avisa
    ├─→ MAIÚSCULA? → Reage com 🔥
    └─→ Comando? → Processa
        ↓
    [Verificação de Permissões]
        ├─→ Sem permissão? → Nega
        └─→ Com permissão? → Executa
            ↓
        [Execução do Comando]
            ├─→ Atualiza banco de dados
            ├─→ Registra em logs
            └─→ Responde ao usuário
```

---

## 🔐 Hierarquia de Permissões

```
Administrator (Máximo)
    ├── Ban Members
    ├── Kick Members
    ├── Manage Messages
    ├── Manage Roles
    ├── Moderate Members
    └── Manage Channels

Moderator
    ├── Moderate Members
    ├── Manage Messages
    └── Kick Members

Member (Mínimo)
    └── Usar comandos públicos
```

---

## 🚀 Escalabilidade

O bot foi desenvolvido para ser escalável:
- **Modular**: Cada funcionalidade é um Cog separado
- **Assíncrono**: Não bloqueia durante operações
- **Cacheable**: Prefixos em cache para performance
- **Extensível**: Fácil adicionar novos Cogs
- **Robusto**: Tratamento de erros em todos os comandos
