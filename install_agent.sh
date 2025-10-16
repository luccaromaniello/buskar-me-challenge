#!/bin/bash

# Variáveis (edite conforme necessário)
SERVICE_NAME="linux-agent"
AGENT_SCRIPT_PATH="/usr/local/bin/agent.py"
SERVICE_PATH="/etc/systemd/system/${SERVICE_NAME}.service"

# Verifique se o script agent.py está na pasta atual
if [ ! -f "agent.py" ]; then
  echo "ERRO: Não encontrei agent.py na pasta atual."
  exit 1
fi

# Copia o agent.py para /usr/local/bin
echo "Copiando agent.py para $AGENT_SCRIPT_PATH"
sudo cp agent.py $AGENT_SCRIPT_PATH
sudo chmod +x $AGENT_SCRIPT_PATH

# Cria o arquivo de serviço systemd
echo "Criando arquivo de serviço systemd em $SERVICE_PATH"

sudo bash -c "cat > $SERVICE_PATH" << EOF
[Unit]
Description=Linux Agent para execução remota via Discord
After=network.target
^CINFO:     Stopping reloader process [21103]
[Service]
ExecStart=/usr/bin/python3 $AGENT_SCRIPT_PATH
Restart=always
Environment=SERVER_URL=https://buskar-96ef670202d0.herokuapp.com/
Environment=MACHINE_NAME=maquina1
Environment=MACHINE_ID=$(uuidgen)

[Install]
WantedBy=multi-user.target
EOF

# Recarrega os serviços do systemd
echo "Recarregando daemon do systemd..."
sudo systemctl daemon-reload

# Ativa o serviço para iniciar no boot
echo "Ativando serviço $SERVICE_NAME para iniciar no boot..."
sudo systemctl enable $SERVICE_NAME

# Inicia o serviço agora
echo "Iniciando serviço $SERVICE_NAME..."
sudo systemctl start $SERVICE_NAME

echo "Status do serviço $SERVICE_NAME:"
sudo systemctl status $SERVICE_NAME --no-pager
