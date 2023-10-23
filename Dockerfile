FROM python:3.8-slim
WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN pip install  -r requirements.txt
EXPOSE 8501
COPY . /app
ENTRYPOINT ["streamlit", "run", "usecase1.py"]