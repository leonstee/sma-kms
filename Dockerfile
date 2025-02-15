FROM python:3.10-slim

RUN apt update && apt install -y libgl1 libglib2.0-0

WORKDIR /usr/src/app
COPY . .
RUN pip install --upgrade --no-cache-dir -r  requirements.txt
EXPOSE 7860
ENV GRADIO_SERVER_NAME="0.0.0.0"


CMD ["sh", "-c", "python watching.py & python gradio_ui.py"]
