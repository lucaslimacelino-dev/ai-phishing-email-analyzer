# AI Phishing Email Analyzer

Aplicação desenvolvida em Python para análise de indicadores de phishing utilizando regras de detecção e inteligência artificial local com Ollama.

## Objetivo

O projeto identifica características comuns encontradas em e-mails de phishing, calcula um nível de risco e gera uma explicação utilizando um modelo de linguagem executado localmente.

Este projeto foi desenvolvido para fins educacionais e demonstra conhecimentos em:

- Python
- Flask
- HTML/CSS
- Cybersecurity
- Análise de URLs
- Inteligência Artificial Local (Ollama)
- Engenharia de Prompts

---

## Funcionalidades

- Análise de e-mails
- Detecção de linguagem de urgência
- Detecção de solicitações de credenciais
- Extração de URLs
- Análise de URLs suspeitas
- Cálculo de pontuação de risco
- Classificação:
  - Baixo
  - Médio
  - Alto
- Explicação utilizando IA local (Gemma 3 via Ollama)

---

## Tecnologias

- Python
- Flask
- HTML
- CSS
- Ollama
- Gemma 3
- Jinja2

---

## Estrutura

```
ai-phishing-email-analyzer
│
├── analyzer
│   ├── ai_explainer.py
│   ├── risk_engine.py
│   ├── url_analyzer.py
│   └── __init__.py
│
├── static
│   └── style.css
│
├── templates
│   └── index.html
│
├── app.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Instalação

Clone o projeto

```bash
git clone https://github.com/SEU_USUARIO/ai-phishing-email-analyzer.git
```

Entre na pasta

```bash
cd ai-phishing-email-analyzer
```

Crie um ambiente virtual

```bash
python -m venv .venv
```

Ative

Windows

```bash
.venv\Scripts\activate
```

Linux

```bash
source .venv/bin/activate
```

Instale as dependências

```bash
pip install -r requirements.txt
```

Execute

```bash
python app.py
```

Abra

```
http://127.0.0.1:5000
```

---

## IA Local

Este projeto utiliza o Ollama.

Baixe o modelo:

```bash
ollama pull gemma3:4b
```

---

## Exemplo

Pontuação:

```
82/100
```

Classificação

```
HIGH RISK
```

Indicadores encontrados

- Linguagem de urgência
- Solicitação de senha
- URL suspeita
- HTTP
- Endereço IP

---

## Aviso

Esta ferramenta possui finalidade educacional.

Ela não substitui soluções profissionais de segurança nem garante que um e-mail seja legítimo ou malicioso.

Utilize somente e-mails fictícios ou previamente anonimizados.

---

## Licença

MIT License