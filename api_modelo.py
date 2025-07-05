# from ntpath import sep  # Importação removida - não utilizada
import os
import logging
import datetime
import jwt
from functools import wraps

from flask import Flask, request, jsonify
from sqlalchemy import create_engine, Column, Integer, Float, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base

JWT_SECRET = "MINHASENHA"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_DELTA = datetime.timedelta(hours=1)

# Configuração do logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("apli_modelo")

# Configuração do banco de dados para ambiente serverless
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///predictions.db')
engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    sepal_length = Column(Float, nullable=False)
    sepal_width = Column(Float, nullable=False)
    petal_length = Column(Float, nullable=False)
    petal_width = Column(Float, nullable=False)
    predicted_class = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

# Criar tabelas apenas se necessário
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Banco de dados inicializado com sucesso")
except Exception as e:
    logger.warning(f"Aviso na inicialização do banco: {e}")

# Modelo simples baseado em regras para classificação de íris
def simple_iris_model(sepal_length, sepal_width, petal_length, petal_width):
    """
    Modelo simples para classificação de íris baseado em regras
    0: Setosa, 1: Versicolor, 2: Virginica
    """
    # Regras baseadas nas características típicas das espécies de íris
    if petal_length < 2.5:
        return 0  # Setosa
    elif petal_length < 5.0 and petal_width < 1.8:
        return 1  # Versicolor
    else:
        return 2  # Virginica

logger.info("Modelo simples carregado com sucesso")

def create_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'message': 'Token ausente'}), 401
        
        try:
            data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token inválido'}), 401
        
        return f(*args, **kwargs)
    
    return decorated

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chave_secreta'

prediction_cache = {}

@app.route('/', methods=['GET'])
def health_check():
    """Endpoint de health check"""
    return jsonify({
        'status': 'healthy',
        'message': 'API de Classificação de Íris está funcionando',
        'version': '1.0.0'
    })

def save_prediction(sepal_length, sepal_width, petal_length, petal_width, predicted_class):
    """Função para salvar predição no banco de dados"""
    try:
        db = SessionLocal()
        try:
            db_prediction = Prediction(
                sepal_length=sepal_length,
                sepal_width=sepal_width,
                petal_length=petal_length,
                petal_width=petal_width,
                predicted_class=predicted_class
            )
            db.add(db_prediction)
            db.commit()
            db.refresh(db_prediction)
            logger.info("Predição salva com sucesso")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Erro ao salvar predição: {e}")
        # Não falha a API se o banco falhar

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user_id = data.get('user_id')
    username = data.get('username')
    password = data.get('password')

    # Verificar as credenciais (substitua pelo seu próprio mecanismo de autenticação)
    if username == 'usuario' and password == 'senha':
        token = create_token(user_id)
        return jsonify({'token': token})
    else:
        return jsonify({'message': 'Credenciais inválidas'}), 401

@app.route('/predict', methods=['POST'])
@token_required
def predict():
    """
    Endpoint protegido por token para obter predição
    ---
    parameters:
        - name: body
          in: body
          required: true
          schema:
            id: DadoModelo
            required:
                - sepal_length
                - sepal_width
                - petal_length
                - petal_width
            properties:
                sepal_length:
                    type: number
                    description: Comprimento da sépala
                sepal_width:
                    type: number
                    description: Largura da sépala
                petal_length:
                    type: number
                    description: Comprimento da pétala
                petal_width:
                    type: number
                    description: Largura da pétala
    responses:
        200:
            description: Retorna a predição do modelo
            schema:
                id: Prediction
                properties:
                    prediction:
                        type: number
                        description: Classe prevista pelo modelo
    """
    data = request.get_json(force=True)
    try:
        sepal_length = float(data['sepal_length'])
        sepal_width = float(data['sepal_width'])
        petal_length = float(data['petal_length'])
        petal_width = float(data['petal_width'])
    except (KeyError, ValueError, TypeError):
        return jsonify({'message': 'Dados inválidos'}), 400
    features = [sepal_length, sepal_width, petal_length, petal_width]
    features_tuple = tuple(features)  # Converte para tupla para usar como chave do cache
    if features_tuple in prediction_cache:
        logger.info("Cache hit para %s", features)
        prediction = prediction_cache[features_tuple]
    else:
        prediction = simple_iris_model(sepal_length, sepal_width, petal_length, petal_width)
        predicted_class = int(prediction)
        prediction_cache[features_tuple] = predicted_class
        logger.info("Cache updated para %s", features)
        save_prediction(sepal_length, sepal_width, petal_length, petal_width, predicted_class)
    
    return jsonify({'prediction': int(prediction)})

# Para desenvolvimento local
if __name__ == '__main__':
    app.run(debug=True)
