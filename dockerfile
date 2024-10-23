# Use a imagem base do Python
FROM python:3.10

# Define o diretório de trabalho
WORKDIR /app

# Copia o arquivo requirements.txt para o contêiner
COPY requirements.txt requirements.txt

# Instala as dependências do projeto
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código fonte da aplicação para o contêiner
COPY . .

# Expõe a porta que a aplicação Flask irá rodar
EXPOSE 5000

# Define a variável de ambiente para rodar o Flask
ENV FLASK_APP=app.py

# Comando para rodar a aplicação
CMD ["flask", "run", "--host=0.0.0.0"]
