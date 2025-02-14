FROM python:3.10-slim

WORKDIR /usr/src/app
COPY . .
RUN pip install --upgrade --no-cache-dir -r  requirements.txt
EXPOSE 7860
ENV GRADIO_SERVER_NAME="0.0.0.0"

ENTRYPOINT ["/myStartupScript.sh"]
CMD ["sh", "-c", "python watching.py & python gradio_ui.py"]
