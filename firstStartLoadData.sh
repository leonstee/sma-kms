CONTAINER_ALREADY_STARTED="CONTAINER_ALREADY_STARTED_PLACEHOLDER"
if [ ! -e $CONTAINER_ALREADY_STARTED ]; then
    touch $CONTAINER_ALREADY_STARTED
    echo "-- First container startup --"
    echo "Preparing to store present Files in Qdrant Vectorstore."
    URL="${QDRANT_URL:-http://localhost:6333}"
    is_up=false
    while [ "$is_up" = false ]; do
        STATUS_CODE=$(curl -sL -w "%{http_code}\n" "$URL" -o /dev/null)
        if [ "$STATUS_CODE" -eq 200 ]; then
            echo "Qdrant is up. Storing data now."
            is_up=true
        else
            echo "Qdrant is down. Waiting..."
            sleep 2
        fi
    done

    python load_data.py
    echo "Storing finished."
else
    echo "-- Not first container startup --"
fi