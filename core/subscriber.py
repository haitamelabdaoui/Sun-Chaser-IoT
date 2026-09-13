import json
import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# Configuration MQTT
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
TOPIC_PV = "voltis/production/solaire"

# Configuration InfluxDB 
INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "psh_jk1Wjfxc56mCdP0vPf3Eow6uv2b3JL9jY0Bco3lSFqERlCX5EVU-EFJF5i-bzO1JuM5R48VERtBtXDJaHA=="  # Ton token InfluxDB v2
INFLUX_ORG = "voltis_org"
INFLUX_BUCKET = "voltis_bucket"

# Initialisation du client InfluxDB
influx_client = InfluxDBClient(
    url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG
)
write_api = influx_client.write_api(write_options=SYNCHRONOUS)

#s'execute une fois que le client est connecté au broker MQTT
def on_connect(client, userdata, flags, rc, properties=None): #rc est le code de retour de la connexion, si rc = 0, la connexion est réussie, sinon il y a une erreur.
  print(f"Connecté au broker MQTT (code: {rc})")
  client.subscribe(TOPIC_PV)

#s'execute à chaque fois qu'un message est reçu sur le topic auquel le client est abonné
def on_message(client, userdata, msg): #msg est le message reçu, il contient le topic, le payload et d'autres informations.
  try:
    data = json.loads(msg.payload.decode("utf-8")) #utf-8 est un encodage de caractères qui permet de représenter tous les caractères possibles, y compris les caractères spéciaux et les accents. On décode le payload du message en utf-8 pour obtenir une chaîne de caractères, puis on la convertit en dictionnaire Python avec json.loads().

    # Structuration du point de donnée pour InfluxDB
    point = (                 #point est un objet qui représente une mesure dans InfluxDB. Il contient un nom de mesure, des tags (des paires clé-valeur qui permettent de filtrer les données), et des champs (des paires clé-valeur qui contiennent les valeurs mesurées).
        Point("production_pv")
        .tag("source", "simulateur_TIPE")
        .field("eclairement_w_m2", float(data["eclairement_w_m2"]))
        .field("puissance_fixe_w", float(data["puissance_fixe_w"]))
        .field("puissance_suiveur_w", float(data["puissance_suiveur_w"]))
    )

    write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
    print(f"[{data['datetime']}] Donnée enregistrée dans InfluxDB")

  except Exception as e:
    print(f"Erreur lors de l'écriture : {e}")


# Client MQTT
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.loop_forever()