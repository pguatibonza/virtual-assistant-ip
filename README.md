# virtual-assistant-ip

## Build
'''ssh
docker build -t chatbot .
'''

## Run

### Windows
```bash
docker run -d -p 8501:8501 --name chatbot_container chatbot
```

### Linux
```bash
docker run --network host -d --name chatbot_container chatbot
```

### Forward to ngrok
```bash
nohup ngrok http --url=trivially-distinct-starling.ngrok-free.app 8501 > ngrok.log 2>&1 &
```

### Stop ngrok
```bash
pkill ngrok
```