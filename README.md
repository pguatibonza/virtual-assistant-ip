# virtual-assistant-ip

build
'''ssh
docker build -t chatbot .
'''

run

### Windows
'''ssh
docker run -d -p 8501:8501 --name chatbot_container chatbot
'''

### Linuxs
'''ssh
docker run --network host -d chatbot
'''