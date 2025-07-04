# API de Predição de Íris

API Flask para predição de espécies de íris usando machine learning, com autenticação JWT e persistência de dados.

## 🚀 Deploy no Vercel

### Pré-requisitos
- Conta no [Vercel](https://vercel.com)
- Vercel CLI instalado: `npm i -g vercel`

### Passos para Deploy

1. **Clone/Prepare o projeto:**
   ```bash
   cd projeto_6
   ```

2. **Login no Vercel:**
   ```bash
   vercel login
   ```

3. **Deploy:**
   ```bash
   vercel
   ```
   - Siga as instruções do CLI
   - Confirme as configurações
   - Aguarde o deploy

4. **Deploy de produção:**
   ```bash
   vercel --prod
   ```

## 📋 Endpoints da API

### 🔐 Login
**POST** `/login`

```json
{
  "user_id": "123",
  "username": "usuario",
  "password": "senha"
}
```

**Resposta:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### 🌸 Predição
**POST** `/predict`

**Headers:**
```
Authorization: SEU_TOKEN_JWT
Content-Type: application/json
```

**Body:**
```json
{
  "sepal_length": 5.1,
  "sepal_width": 3.5,
  "petal_length": 1.4,
  "petal_width": 0.2
}
```

**Resposta:**
```json
{
  "prediction": 0
}
```

## 🔧 Funcionalidades

- ✅ Autenticação JWT
- ✅ Cache de predições
- ✅ Persistência no SQLite
- ✅ Logging estruturado
- ✅ Tratamento de erros
- ✅ Compatível com Vercel

## 📁 Estrutura do Projeto

```
projeto_6/
├── api_modelo.py          # API Flask principal
├── modelo_iris.pkl        # Modelo treinado
├── requirements.txt       # Dependências Python
├── vercel.json           # Configuração Vercel
├── .vercelignore         # Arquivos ignorados no deploy
└── README.md             # Este arquivo
```

## 🛠️ Desenvolvimento Local

```bash
python3 api_modelo.py
```

A API estará disponível em `http://localhost:5000`

## 📝 Notas

- Token JWT expira em 1 hora
- Credenciais padrão: `usuario` / `senha`
- Banco SQLite criado automaticamente
- Cache em memória para otimização