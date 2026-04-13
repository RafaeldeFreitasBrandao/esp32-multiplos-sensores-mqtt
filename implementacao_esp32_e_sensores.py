#bibliotecas e imports
import network
from umqtt.simple import MQTTClient
from machine import Pin, PWM #uso dos GPIO's e buzzer

import time
import json #uso do JSON

import dht #uso do DHT11

from hcsr04 import HCSR04 #uso do sensor de distancia

# CONFIGURAÇÕES DO WIFI E BROKER #
SSID = ""
SENHA = ""
BROKER = "broker.hivemq.com"
PORTA = 1883
CLIENT_ID = "grupo6-dh22-teste"
TOPICO_PUBLICAR_DADOS1 = "gp6/micro/dados1"
TOPICO_PUBLICAR_DADOS2 = "gp6/micro/dados2"
TOPICO_ASSINAR = "gp6/pc/comandos1"

#Declaração do led 
led = Pin(27, Pin.OUT)
led_estado = False

#Declaracao do Buzzer
buzzer = PWM(Pin(14))  # inicia desligado
buzzer_estado = False

buzzer.duty(0)
#Função para o buzzer funcionar
def tocar_som(freq, durac):
    buzzer.freq(freq)
    buzzer.duty_u16(32768) 
    time.sleep(durac)

# Declaração do DHT11
sensor = dht.DHT22(Pin(17, Pin.IN))

# Declaracao do HCSR04
medidor = HCSR04(trigger_pin=5, echo_pin=15)


# ---- Conexao Wi-Fi ----
def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        print("Conectando ao Wi-Fi...")
        wlan.connect(SSID, SENHA)
        tentativas = 0
        while not wlan.isconnected() and tentativas < 20:
            time.sleep(1)
            tentativas += 1
            print(f" Tentativa {tentativas}/20...")
    if wlan.isconnected():
        print(f"Wi-Fi conectado! IP: {wlan.ifconfig()[0]}")
        return True
    else:
        print("ERRO: Nao foi possivel conectar ao Wi-Fi")
        return False


# ---- Callback de mensagens recebidas ----
def callback_mensagem(topico, mensagem):
    global led_estado, buzzer_estado
    topico = topico.decode("utf-8")
    payload = mensagem.decode("utf-8").strip()
    print(f"[MICRO] Recebido em '{topico}': {payload}")

    try:
        dados = json.loads(payload)
        comando = dados.get("comando", "")
    except:
        comando = payload

    # Lógica do LED — bloco independente
    if comando == "led_on":
        led.value(1)
        led_estado = True
        print("[MICRO-DADOS1] LED ligado!")
        publicar_estado_DADOS1()

    elif comando == "led_off":
        led.value(0)
        led_estado = False
        print("[MICRO-DADOS1] LED desligado!")
        publicar_estado_DADOS1()

    # Lógica do Buzzer — bloco independente
    if comando == "buzzer_on":
        tocar_som(500,1)
        buzzer_estado = True
        print("[MICRO-DADOS2] BUZZER ligado!")
        publicar_estado_DADOS2()

    elif comando == "buzzer_off":
        buzzer.duty(0)
        buzzer_estado = False
        print("[MICRO-DADOS2] BUZZER desligado!")
        publicar_estado_DADOS2()

    # Status e desconhecido — bloco independente
    if comando == "status":
        publicar_dados_sensor_dht()
        publicar_dados_sensor_hcsr04()

    elif comando not in ("led_on", "led_off", "buzzer_on", "buzzer_off", "status"):
        print(f"[MICRO] Comando desconhecido: {comando}")


# ---- Funcoes de publicacao ----
def publicar_estado_DADOS1():
    estado1 = "ligado" if led_estado else "desligado"
    msg = json.dumps({"led": estado1})
    client.publish(TOPICO_PUBLICAR_DADOS1, msg)
    print(f"[MICRO-DADOS1] Publicado: {msg}")

def publicar_estado_DADOS2():
    estado2 = "ligado" if buzzer_estado else "desligado"
    msg = json.dumps({"buzzer": estado2})
    client.publish(TOPICO_PUBLICAR_DADOS2, msg)
    print(f"[MICRO-DADOS2] Publicado: {msg}")

def publicar_dados_sensor_dht():
    for tentativa in range(5):
        try:
            time.sleep(1)
            sensor.measure()
            temp = sensor.temperature()
            hum = sensor.humidity()

            dados = {
                "temperatura": temp,
                "umidade": hum,
                "led": "ligado" if led_estado else "desligado"
            }
            msg = json.dumps(dados)
            client.publish(TOPICO_PUBLICAR_DADOS1, msg)
            print(f"[MICRO-DADOS1] Dados publicados: {msg}")
            return
        except OSError as e:
            print(f"[MICRO] Tentativa {tentativa+1}/5 falhou: {e}")
    print("[MICRO] DHT11 nao respondeu apos 5 tentativas.")

def publicar_dados_sensor_hcsr04():
    distancia = medidor.distance_cm()

    dados = {
        "distancia (cm)": distancia,
        "buzzer": "ligado" if buzzer_estado else "desligado"
    }
    msg = json.dumps(dados)
    client.publish(TOPICO_PUBLICAR_DADOS2, msg)
    print(f"[MICRO-DADOS2] Dados publicados: {msg}")


# ---- Conexao e loop principal ----
if not conectar_wifi():
    print("Abortando: sem Wi-Fi.")
    raise SystemExit

print("[MICRO] Conectando ao broker MQTT...")
client = MQTTClient(CLIENT_ID, BROKER, port=PORTA)
client.set_callback(callback_mensagem)
client.connect()

print(f"[MICRO] Conectado a {BROKER}")
client.subscribe(TOPICO_ASSINAR)
print(f"[MICRO] Inscrito em: {TOPICO_ASSINAR}")
print("[MICRO] Aguardando comandos...\n")

# Loop principal
contador = 0
try:
    while True:
        client.check_msg()

        contador += 1
        if contador >= 20:
            publicar_dados_sensor_dht()
            publicar_dados_sensor_hcsr04()
            contador = 0

        time.sleep(0.5)

except KeyboardInterrupt:
    print("\n[MICRO] Interrompido pelo usuario.")
finally:
    client.disconnect()
    print("[MICRO] Desconectado do broker.")
