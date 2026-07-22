# AI Phishing Email Analyzer

Projeto de cibersegurança desenvolvido em Python com Flask para identificar e analisar e-mails suspeitos utilizando um motor de regras, Machine Learning e inteligência artificial.

---

## Objetivo

O sistema analisa mensagens de e-mail procurando indicadores de phishing e apresenta:

- score de risco;
- classificação da mensagem;
- indicadores encontrados;
- explicação gerada por IA.

A classificação é realizada localmente pelo sistema. A IA (Google Gemini) é utilizada apenas para explicar o resultado ao usuário.

---

# Tecnologias

- Python 3
- Flask
- Scikit-learn
- TF-IDF
- Logistic Regression
- Joblib
- Requests
- n8n
- Google Gemini API
- HTML
- CSS

---

# Arquitetura

```
Usuário
        │
        ▼
Flask
        │
        ├──────────────┐
        ▼              ▼
Motor de regras    Machine Learning
        │              │
        └──────┬───────┘
               ▼
      Score final
               │
               ▼
        Webhook (n8n)
               │
               ▼
     Google Gemini
               │
               ▼
Comentário explicativo
               │
               ▼
Página HTML
```

---

# Funcionalidades

- Análise por motor de regras
- Classificação utilizando Machine Learning
- Cálculo do score final
- Detecção de indicadores de phishing
- Identificação de URLs
- Interface web
- API REST
- Comentários explicativos utilizando Google Gemini
- Integração com n8n

---

# Estrutura do projeto

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
│
├── templates/
│
├── training/
│
├── app.py
├── requirements.txt
└── README.md
```

---

# Fluxo da aplicação

1. O usuário envia um e-mail.

2. O motor de regras analisa:

- urgência
- links
- credenciais
- ameaças
- engenharia social
- indicadores de spam

3. O modelo de Machine Learning calcula a probabilidade de phishing.

4. O sistema calcula o score final.

5. Os resultados são enviados ao n8n.

6. O n8n consulta o Google Gemini.

7. O Gemini gera uma explicação.

8. A página exibe:

- Score
- Classificação
- Indicadores
- Comentário da IA

---

# Machine Learning

Modelo utilizado:

- TF-IDF
- Logistic Regression

Treinado utilizando o conjunto de dados:

https://huggingface.co/datasets/ealvaradob/phishing-dataset

---

# Integração com IA

O Google Gemini **não realiza a classificação**.

Ele recebe apenas os resultados produzidos pelo sistema e gera uma explicação em linguagem natural.

Caso o n8n ou o Gemini estejam indisponíveis, a aplicação continua funcionando normalmente utilizando apenas:

- motor de regras;
- Machine Learning.

---

# Executando localmente

Clone o projeto

```bash
git clone URL_DO_REPOSITORIO
```

Instale as dependências

```bash
pip install -r requirements.txt
```

Configure

```
N8N_WEBHOOK_URL=http://localhost:5678/webhook/SEU_WEBHOOK
```

Execute

```bash
python app.py
```

---

# Deploy

Frontend e Backend:

- Render

Automação:

- n8n

Modelo de IA:

- Google Gemini API

---

# Autor

Lucas Lima

Projeto acadêmico voltado para estudos em:

- Cibersegurança
- Machine Learning
- Inteligência Artificial
- Engenharia de Software