import json
import time
import pandas as pd
import paho.mqtt.client as mqtt

# Configuration MQTT
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
TOPIC_PV = "voltis/production/solaire"

CSV_PATH = "/Users/haitamelabdaoui/Desktop/TIPE/TIPE_GITHUB/BDD_RESULT/TIPE_RESULT_F.csv"

print("Chargement des données du TIPE...")

# Lecture du fichier
df = pd.read_csv(CSV_PATH, sep=";")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

print("Début de la diffusion des données...")


for _, ligne in df.iterrows():
        if str(ligne["date_time"]) == "nan":
           continue
        # On permet la conversion en remplaçant la virgule par un point
        eclairement = float(str(ligne["E_W_m2"]).replace(',', '.'))
        p_fixe = float(str(ligne["P_t_W_fixe"]).replace(',', '.'))
        p_suiveur = float(str(ligne["P_t_W_suiveur"]).replace(',', '.'))

        payload = {
            "datetime": str(ligne["date_time"]),
            "eclairement_w_m2": eclairement,
            "puissance_fixe_w": p_fixe,
            "puissance_suiveur_w": p_suiveur,
            "gain_pourcent": 19.85,
        }

        # Publication sur le canal MQTT
        client.publish(TOPIC_PV, json.dumps(payload))
        
        print(f"[{ligne['date_time']}] Envoyé -> Fixe: {p_fixe:.1f}W | Suiveur: {p_suiveur:.1f}W")
        
        # Petite pause pour simuler un flux en temps réel 
        time.sleep(0.1)
