# virtual-assistant-ip

## Build
'''ssh
docker build -t chatbot .
'''

## Run

### Windows
'''ssh
docker run -d -p 8501:8501 --name chatbot_container chatbot
'''

### Linux
'''ssh
docker run --network host -d --name chatbot_container chatbot
'''

### Forward to ngrok
'''ssh
ngrok http --url=trivially-distinct-starling.ngrok-free.app 8501 > /dev/null 2>&1 &
'''
