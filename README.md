# Rastreador de Preços de Produtos em Python

Sistema simples, modular e extensível em Python para monitorar o preço de produtos específicos em lojas online via URLs diretas e notificar quando o preço atingir ou ficar abaixo de um valor configurado.

---

## 🎯 Objetivo

Monitorar preços de produtos associados a URLs específicas de e-commerce e exibir alertas no terminal.

O projeto foi projetado para:
- Evitar pesquisas genéricas ou agregadores que mostram modelos antigos ou sem estoque.
- Permitir cadastrar múltiplos produtos e múltiplas lojas centralizadamente.
- Continuar executando mesmo se uma das lojas falhar (resiliência contra timeouts, 404, 403, seletor alterado, etc).
- Ser agendado gratuitamente no **GitHub Actions** a cada 30 minutos.
- Estar preparado para expansões futuras (Playwright/Selenium, alertas via Telegram/Discord/Email e histórico em SQLite).

---

## 📦 Estrutura do Projeto

```text
rastreador-de-precos/
│
├── .github/
│   └── workflows/
│       └── price-monitor.yml     # Workflow do GitHub Actions (execução a cada 30 min)
│
├── src/
│   ├── __init__.py
│   ├── main.py                   # Ponto de entrada (execução única)
│   ├── config/
│   │   ├── __init__.py
│   │   └── products.py           # Catálogo centralizado de produtos e lojas
│   ├── scrapers/
│   │   ├── __init__.py
│   │   ├── base.py                   # Abstração BaseScraper para scrapers futuros
│   │   └── generic_scraper.py        # Scraper genérico (requests + BeautifulSoup + CSS selector)
│   ├── models/
│   │   ├── __init__.py
│   │   └── product.py            # Dataclasses de Produto, Loja e Resultado
│   ├── services/
│   │   ├── __init__.py
│   │   ├── price_service.py      # Orquestrador do monitoramento
│   │   └── notification_service.py # Serviço de notificações (Terminal, Telegram, Discord, etc)
│   └── utils/
│       ├── __init__.py
│       └── price_parser.py       # Conversor de preços em formato brasileiro (BRL)
│
├── tests/
│   ├── __init__.py
│   ├── test_generic_scraper.py   # Testes unitários do scraper genérico (com mocks)
│   ├── test_price_parser.py      # Testes unitários de conversão de valores BRL
│   └── test_product_model.py     # Testes da lógica de avaliação de preço-alvo
│
├── .env.example                  # Modelo de variáveis de ambiente
├── .gitignore                    # Regras do git
├── requirements.txt              # Dependências Python
└── README.md                     # Documentação oficial
```

---

## 🛠️ Requisitos

- **Python 3.10+**
- **pip**

---

## 🚀 Instalação e Configuração Local

### 1. Clonar o repositório

```bash
git clone https://github.com/ludson96/rastreador-de-precos.git
cd rastreador-de-precos
```

### 2. Criar e ativar o ambiente virtual (.venv)

**No Windows:**
```powershell
python -m venv .venv
.venv\Scripts\activate
```

**No Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar as dependências

```bash
pip install -r requirements.txt
```

---

## ⚙️ Como Cadastrar / Alterar Produtos e Lojas

Todas as configurações ficam centralizadas no arquivo [src/config/products.py](file:///d:/Code/projetos-pessoal/rastreador-de-precos/src/config/products.py).

Para cadastrar ou editar um produto, basta adicionar uma nova instância de `ProductConfig`:

```python
ProductConfig(
    id="consul_ccb07gb",
    name="Ar-condicionado de Janela Consul 7.500 BTUs Frio",
    model="CCB07GB",
    capacity="7500 BTU",
    voltage="110V",  # Configurável por variação
    target_price=1500.00,
    enabled=True,
    stores={
        "loja_exemplo": StoreConfig(
            name="Nome da Loja",
            url="https://www.sitedaloja.com.br/produto-exemplo",
            selector=".preco-destaque",  # Seletor CSS contendo o preço
            enabled=True,
            scraper_type="generic"
        )
    }
)
```

---

## 🏃 Como Executar

Execute o comando a seguir na raiz do projeto:

```bash
python -m src.main
```

### Exemplo de saída no terminal:

```text
============================================================
                PAINEL DE MONITORAMENTO DE PREÇOS             
============================================================

Produto: Ar-condicionado de Janela Consul 7.500 BTUs Frio
Loja: Consul Oficial
Preço atual: R$ 1.489,90
Preço-alvo: R$ 1.500,00
Status: 🚀 PREÇO-ALVO ATINGIDO!
------------------------------------------------------------
```

---

## 🧪 Executando os Testes Unitários

O projeto possui uma suíte completa de testes utilizando `pytest`:

```bash
pytest
```

---

## 📊 Relatório Diário por E-mail & Diagnóstico de Erros

O sistema conta com um **Relatório Diário de Preços e Saúde do Monitoramento**:

1. **Agendamento Automático**: O GitHub Actions envia este relatório **1 vez ao dia** às **08:00 AM (BRT)**.
2. **Conteúdo do Relatório**:
   - **Tabela Consolidada**: Produto, Loja, Preço Atual, **Menor Preço das últimas 24 horas** (salvo no banco de dados SQLite `price_history.db`), Preço-alvo e Status.
   - **⚠️ Seção de Diagnóstico de Erros**: Se alguma loja apresentar falha (como mudança no layout/seletor CSS, erro HTTP 404, 403 ou timeout), o relatório destaca exatamente qual loja falhou, exibindo o tipo de erro, a mensagem e o link para você atualizar os seletores em `src/config/products.py`!

### Executando o Relatório Diário Manualmente

Para disparar o relatório diário manualmente na sua máquina:

```bash
python -m src.main --daily-report
```

---

## 📧 Configuração de Notificações por E-mail (SMTP)


O sistema agora possui suporte a notificações por e-mail via **SMTP**. 

⚠️ **Importante**: O e-mail só é enviado **exclusivamente quando houver um desconto** (ou seja, quando o preço atual for **menor ou igual ao preço-alvo**). Se o preço estiver acima do preço-alvo ou se houver um erro de scraping, nenhum e-mail é enviado.

### Como Ativar Localmente

No seu arquivo `.env` (criado a partir do `.env.example`), adicione:

```env
EMAIL_ENABLED=true
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=seu_email@gmail.com
SMTP_PASSWORD=sua_senha_de_app
EMAIL_TO=destinatario@email.com
```

*Nota para Gmail*: Utilize uma **Senha de App** gerada nas configurações de segurança da sua conta Google (não use a sua senha principal do Gmail).

### Configuração no GitHub Actions (Secrets)

Para receber e-mails quando executado pelo GitHub Actions, configure as seguintes variáveis em **Settings > Secrets and variables > Actions > Repository secrets**:

- `EMAIL_ENABLED`: `true`
- `SMTP_SERVER`: `smtp.gmail.com`
- `SMTP_PORT`: `587`
- `SMTP_USERNAME`: `seu_email@gmail.com`
- `SMTP_PASSWORD`: `sua_senha_de_app`
- `EMAIL_TO`: `seu_email_para_receber_alertas@gmail.com`

---

## ⚡ Preparação para GitHub Actions


O arquivo `.github/workflows/price-monitor.yml` está configurado para executar o monitoramento automaticamente a cada **30 minutos** sem custos:

```yaml
on:
  schedule:
    - cron: '*/30 * * * *'
  workflow_dispatch:
```

---

## 🔮 Arquitetura e Extensões Futuras

1. **Novos Scrapers (ex: APIs Oficiais ou Scraping via Proxies)**:
   Implemente uma subclasse de `BaseScraper` em `src/scrapers/` e registre-a no `PriceService`.
2. **Novos Alertas (Telegram / Discord / E-mail)**:
   Crie uma classe que herde de `BaseNotifier` em `src/services/notification_service.py` e adicione ao `NotificationService`.
3. **Histórico em SQLite**:
   Adicione um módulo `src/database/history.py` para gravar os objetos `PriceResult` após cada execução.
