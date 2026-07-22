# AI Phishing Email Analyzer

Sistema web para detecção e análise de e-mails de phishing utilizando **Machine Learning**, **motor de regras** e **Inteligência Artificial Generativa**.

O projeto foi desenvolvido com Python e Flask como uma aplicação de apoio à identificação de mensagens fraudulentas, combinando análise determinística, classificação estatística e explicações em linguagem natural geradas pelo Google Gemini.

---

# Objetivo

O objetivo deste projeto é auxiliar usuários na identificação de possíveis ataques de phishing através de uma análise automatizada do conteúdo de e-mails.

A aplicação combina diferentes técnicas para fornecer uma avaliação mais completa:

- Motor de regras baseado em indicadores conhecidos de phishing;
- Modelo de Machine Learning treinado para classificação de e-mails;
- Score de risco unificado;
- Explicação em linguagem natural utilizando Inteligência Artificial.

O sistema foi desenvolvido com fins acadêmicos e educacionais.

---

# Demonstração

## Aplicação publicada

**Render**


```
https://ai-phishing-email-analyzer.onrender.com
```

---

## Capturas de tela

As imagens da aplicação encontram-se na pasta:

```
docs/images/
```

Capturas recomendadas:

- Interface inicial
- Resultado da análise
- Comentário gerado pelo Gemini
- Workflow do n8n
- Aplicação publicada no Render

---

# Tecnologias Utilizadas

## Backend

- Python 3
- Flask
- Requests
- Joblib

## Machine Learning

- Scikit-learn
- TF-IDF
- Logistic Regression

## Inteligência Artificial

- Google Gemini API

## Automação

- n8n

## Frontend

- HTML5
- CSS3

---

# Arquitetura da Solução

```
                     Usuário
                        │
                        ▼
                Interface Web (Flask)
                        │
         ┌──────────────┴──────────────┐
         ▼                             ▼
  Motor de Regras             Machine Learning
         │                             │
         └──────────────┬──────────────┘
                        ▼
               Cálculo do Score
                        │
                        ▼
                Integração com n8n
                        │
                        ▼
               Google Gemini API
                        │
                        ▼
           Comentário Explicativo
                        │
                        ▼
             Resultado exibido ao usuário
```

---

# Funcionalidades

- Análise automática de e-mails
- Motor de regras para detecção de phishing
- Identificação de URLs suspeitas
- Detecção de indicadores de engenharia social
- Classificação utilizando Machine Learning
- Cálculo de score de risco
- Classificação do risco
- Explicação textual utilizando IA
- Interface web responsiva
- API REST
- Integração com n8n
- Funcionamento mesmo sem IA

---

# Estrutura do Projeto

```
.
├── analyzer/
│   ├── analysis_service.py
│   ├── ml_classifier.py
│   ├── n8n_client.py
│   ├── risk_engine.py
│   └── url_analyzer.py
│
├── models/
│   ├── phishing_model.joblib
│   └── vectorizer.joblib
│
├── static/
│   └── style.css
│
├── templates/
│   └── index.html
│
├── training/
│
├── docs/
│   └── images/
│
├── app.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

# Funcionamento da Aplicação

## 1. Entrada

O usuário envia o conteúdo completo de um e-mail para análise.

---

## 2. Motor de Regras

São verificados diversos indicadores de phishing, incluindo:

- palavras de urgência;
- engenharia social;
- solicitações de credenciais;
- URLs suspeitas;
- domínios conhecidos;
- indicadores de spam;
- ameaças;
- tentativas de fraude.

---

## 3. Machine Learning

O texto é processado utilizando TF-IDF.

Em seguida, um modelo de **Logistic Regression** estima a probabilidade de o e-mail ser phishing.

---

## 4. Score Final

O sistema combina:

- resultado do motor de regras;
- probabilidade produzida pelo modelo.

A partir dessa combinação é calculado um score entre **0 e 100**.

---

## 5. Inteligência Artificial

Após a classificação, os resultados são enviados para um workflow do **n8n**.

O n8n consulta o **Google Gemini**, responsável apenas por gerar uma explicação em linguagem natural sobre os resultados encontrados.

A IA **não interfere** na classificação do e-mail.

---

## 6. Resultado

A aplicação apresenta:

- Score final;
- Classificação;
- Nível de risco;
- Indicadores encontrados;
- URLs identificadas;
- Probabilidades do modelo;
- Comentário da IA.

---

# Modelo de Machine Learning

## Algoritmo

- Logistic Regression

## Vetorização

- TF-IDF

## Dataset

Phishing Email Dataset

https://huggingface.co/datasets/ealvaradob/phishing-dataset

---

# Integração com Inteligência Artificial

O Google Gemini é utilizado exclusivamente para gerar comentários explicativos.

Fluxo:

```
Flask
      │
      ▼
n8n Webhook
      │
      ▼
Google Gemini
      │
      ▼
Comentário textual
```

Caso o serviço esteja indisponível, a aplicação continua funcionando normalmente utilizando apenas:

- Motor de regras;
- Machine Learning.

---

# Executando Localmente

## Clonar o repositório

```bash
git clone https://github.com/lucaslimacelino-dev/ai-phishing-email-analyzer.git
```

---

## Entrar na pasta

```bash
cd AI-Phishing-Email-Analyzer
```

---

## Criar ambiente virtual

Windows

```bash
python -m venv .venv
```

---

## Ativar ambiente virtual

Windows

```bash
.venv\Scripts\activate
```

Linux

```bash
source .venv/bin/activate
```

---

## Instalar dependências

```bash
pip install -r requirements.txt
```

---

## Configurar variável de ambiente

```
N8N_WEBHOOK_URL=https://celino.app.n8n.cloud/webhook/fe025c47-e62e-498b-b1d5-63d1e9b3f71a
```

---

## Executar

```bash
python app.py
```

A aplicação ficará disponível em:

```
http://127.0.0.1:5000
```

---

# Deploy

## Aplicação

- Render

## Workflow

- n8n Cloud

## Inteligência Artificial

- Google Gemini API

---

# Melhorias Futuras

- Upload de arquivos `.eml`
- Upload de anexos
- Histórico de análises
- Dashboard administrativo
- Autenticação de usuários
- Geração de relatórios em PDF
- API pública
- Suporte a múltiplos idiomas
- Novos modelos de Machine Learning

---

# Considerações

Este projeto foi desenvolvido para fins acadêmicos e demonstra a integração entre:

- Desenvolvimento Web
- Machine Learning
- Cibersegurança
- Inteligência Artificial
- Automação de Processos

A ferramenta não substitui soluções profissionais de segurança da informação.

---

# Autor

**Lucas Lima Celino**

Projeto desenvolvido para estudos nas áreas de:

- Cibersegurança
- Machine Learning
- Inteligência Artificial
- Engenharia de Software
- Desenvolvimento Web