## ESP32 - Monitoramento de Sensores via MQTT

Este projeto consiste no desenvolvimento de um sistema embarcado em Micropython que lê a temperatura, umidade e distância de sensores conctados a um ESP32 e publica os dados em um broker MQTT, além de receber comandos remotos por subscrição.

## Hardware Necessário

## Hardware necessário

| Componente | Função | Pino |
|---|---|---|
| ESP32 DevKit v1 | Microcontrolador | — |
| DHT22 | Temperatura e umidade | GPIO 4 |
| HC-SR04 | Distância (ultrassônico) | Trig: GPIO 5 / Echo: GPIO 18 |

*(ajuste os pinos conforme o seu código)*

## Tecnologias 

- Micropython
- Protocolo MQTT (biblioteca `umqtt.simple`)
- Broker: Mosquitto ou HiveMQ (ambos grátis)

## Como Rodar:

**1.Instale o Thonny IDE**

**2.Grave o firmware MicroPython no ESP32**

Passo1. - Acesse a página de Downloads do Micropython downloads --> escolha a versão correta para seu chip (por exemplo "ESP32 generic", para os modelos tradicionais)--> baixe a versão mais recente (arquivo com exetensão .bin)
Passo2. - Conecte o ESP32 ao seu computador usando um cabo USB que tenha suporte a transferência de dados.
Passo3. - Abra o Thonny IDE --> Clique em EXECUTAR e depois em CONFIGURAR --> na opção INTERPRETADOR selecione MicroPython (ESP32) --> No campo PORTA selecione a porta COM correta, a qual o seu ESP32 está conctado --> Clique no link INSTALAR ou ATUALIZAR FIRMWARE localizado no canto inferior direito
--> Selecione novamente a porta COM do seu ESP32 --> Clique no botão "..." e selecione o arquivo ".bin" do MicroPython que você baixou no passo 1. --> Deixe marcado a opção "Erase flash before install" --> Clique em instalar e aguarde o processo finalizar.

**3.Configure as credenciais**

- Abra o arquivo `implementacao_esp32_e_sensores.py` pelo Thonny, e preencha:

```
SSID = "sua-rede-wifi"
SENHA = "sua-senha"
BROKER = "broker.hivemq.com"

```


**4. Envie o arquivo para a placa**

```bash
pip install adafruit-ampy
ampy --port COM3 put implementacao_esp32_e_sensores.py main.py
```

**5. Acompanhe as mensagens**

```bash
mosquitto_sub -h broker.hivemq.com -t "esp32/sensores/#" -v
```

## Tópicos MQTT

| Tópico | Direção | Payload |
|---|---|---|
| `esp32/sensores/temperatura` | Publica | `{"valor": 24.3, "unidade": "C"}` |
| `esp32/comandos` | Assina | `led_on` / `led_off` |

*(ajuste para os tópicos reais do seu código)*

## Detalhes de implementação

- **Reconexão de Wi-Fi** com contador de tentativas, evitando travamento em loop infinito.
- **Retry na leitura do DHT22**, que costuma falhar esporadicamente com `OSError`.
- **`try/finally` no loop principal**, garantindo desconexão limpa do broker ao interromper a execução.

## Autor

Rafael de Freitas Brandão — [LinkedIn](https://linkedin.com/in/seu-perfil)











































