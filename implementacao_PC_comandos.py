# pc_mqtt.py
# Aplicacao MQTT no PC - Envia comandos e recebe dados do microcontrolador

import paho.mqtt.client as mqtt
import json

# ---- Configuracoes ----
BROKER = "broker.hivemq.com"
PORTA = 1883
TOPICO_PUBLICAR = "gp6/pc/comandos1"   # PC publica aqui
TOPICO_ASSINAR = "gp6/micro/+"    # PC recebe daqui
CLIENT_ID = "pc-pucpr-001"

# ---- Callbacks ----
def on_connect(client, userdata, flags, rc, properties):
    if rc == 0:
        print("[PC] Conectado ao broker MQTT!")
        client.subscribe(TOPICO_ASSINAR)
        print(f"[PC] Inscrito no topico: {TOPICO_ASSINAR}")
    else:
        print(f"[PC] Falha na conexao, codigo: {rc}")

def on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8")
    print(f"\n[PC] Mensagem recebida em '{msg.topic}': {payload}")

    try:
        dados = json.loads(payload)

        if "temperatura" in dados:
            print(f"\n🌡 Temperatura: {dados['temperatura']} °C")

        if "umidade" in dados:
            print(f"\n💧 Umidade: {dados['umidade']} %")

        if "distancia (cm)" in dados: 
            print(f"\nDistância: {dados['distancia (cm)']}cm")

        if "led" in dados:
            print(f"\n💡 LED: {dados['led']}")

        if "buzzer" in dados:
            print(f"\nBUZZER: {dados['buzzer']}")

    except:
        print("Mensagem não está em JSON")

def on_disconnect(client, userdata, flags, rc, properties):
    print(f"[PC] Desconectado (rc={rc})")

# ---- Programa principal ----
def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=CLIENT_ID)

    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    print(f"[PC] Conectando a {BROKER}:{PORTA}...")
    client.connect(BROKER, PORTA, 60)

    client.loop_start()

    print("\n--- COMANDOS ---")
    print("led_on  -> Liga LED")
    print("led_off -> Desliga LED")
    print("buzzer_on -> Aciona o BUZZER")
    print("buzzer_off -> Desliga o BUZZER")
    print("status  -> Lê sensor")
    print("sair    -> Encerrar\n")

    try:
        while True:
            comando = input("[PC] Digite um comando: ").strip()

            if comando.lower() == "sair":
                break

            if comando:
                mensagem = json.dumps({"comando": comando})
                client.publish(TOPICO_PUBLICAR, mensagem)
                print(f"[PC] Enviado: {mensagem}")

    except KeyboardInterrupt:
        print("\n[PC] Interrompido.")

    finally:
        client.loop_stop()
        client.disconnect()
        print("[PC] Encerrado.")

if __name__ == "__main__":
    main()