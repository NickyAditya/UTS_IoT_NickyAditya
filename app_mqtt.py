from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import mysql.connector
import paho.mqtt.client as mqtt
import json
import threading
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# Konfigurasi Database
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Ganti dengan password MySQL Anda
    'database': 'uts_iot'
}

# Konfigurasi MQTT
MQTT_BROKER = "test.mosquitto.org"  # Atau broker MQTT lainnya
MQTT_PORT = 1883
MQTT_TOPIC_DATA = "iot/sensor/data"
MQTT_TOPIC_RELAY = "iot/relay/control"

# Variabel global untuk data sensor terbaru
latest_sensor_data = {
    'suhu': 0,
    'humidity': 0,
    'lux': 0,
    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
}

def get_db_connection():
    """Membuat koneksi ke database MySQL"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None

def insert_sensor_data(suhu, humidity, lux):
    """Insert data sensor ke database"""
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            query = "INSERT INTO data_sensor (suhu, humidity, lux) VALUES (%s, %s, %s)"
            cursor.execute(query, (suhu, humidity, lux))
            connection.commit()
            cursor.close()
            connection.close()
            print(f"Data inserted: Suhu={suhu}, Humidity={humidity}, Lux={lux}")
    except Exception as e:
        print(f"Error inserting data: {e}")

def on_connect(client, userdata, flags, rc):
    """Callback saat MQTT client terhubung"""
    if rc == 0:
        print("Connected to MQTT Broker!")
        client.subscribe(MQTT_TOPIC_DATA)
    else:
        print(f"Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    """Callback saat menerima pesan MQTT"""
    try:
        # Decode pesan JSON
        data = json.loads(msg.payload.decode())
        print(f"Received data: {data}")
        
        # Update data global
        global latest_sensor_data
        latest_sensor_data = {
            'suhu': data.get('suhu', 0),
            'humidity': data.get('humidity', 0),
            'lux': data.get('lux', 0),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Simpan ke database
        insert_sensor_data(
            data.get('suhu', 0),
            data.get('humidity', 0),
            data.get('lux', 0)
        )
        
    except Exception as e:
        print(f"Error processing message: {e}")

# Setup MQTT Client
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

def start_mqtt():
    """Memulai MQTT client"""
    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        mqtt_client.loop_forever()
    except Exception as e:
        print(f"MQTT connection error: {e}")

# Routes
@app.route('/')
def index():
    """Halaman utama"""
    return render_template('index.html')

@app.route('/api/sensor/latest')
def get_latest_sensor_data():
    """API untuk mendapatkan data sensor terbaru"""
    return jsonify(latest_sensor_data)

@app.route('/api/sensor/history')
def get_sensor_history():
    """API untuk mendapatkan riwayat data sensor"""
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM data_sensor ORDER BY timestamp DESC"
            cursor.execute(query)
            data = cursor.fetchall()
            cursor.close()
            connection.close()
            
            # Format timestamp untuk JSON
            for item in data:
                item['timestamp'] = item['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            
            return jsonify(data)
    except Exception as e:
        print(f"Error getting history: {e}")
        return jsonify([])

@app.route('/api/sensor/statistics')
def get_sensor_statistics():
    """API untuk mendapatkan statistik data sensor"""
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            
            # Statistik suhu
            cursor.execute("SELECT AVG(suhu) as avg_temp, MIN(suhu) as min_temp, MAX(suhu) as max_temp FROM data_sensor")
            temp_stats = cursor.fetchone()
            
            # Statistik humidity
            cursor.execute("SELECT AVG(humidity) as avg_humidity, MIN(humidity) as min_humidity, MAX(humidity) as max_humidity FROM data_sensor")
            humidity_stats = cursor.fetchone()
            
            # Statistik lux
            cursor.execute("SELECT AVG(lux) as avg_lux, MIN(lux) as min_lux, MAX(lux) as max_lux FROM data_sensor")
            lux_stats = cursor.fetchone()
            
            # Total data
            cursor.execute("SELECT COUNT(*) as total_records FROM data_sensor")
            count_result = cursor.fetchone()
            
            cursor.close()
            connection.close()
            
            statistics = {
                'temperature': {
                    'average': round(temp_stats['avg_temp'] or 0, 2),
                    'minimum': temp_stats['min_temp'] or 0,
                    'maximum': temp_stats['max_temp'] or 0
                },
                'humidity': {
                    'average': round(humidity_stats['avg_humidity'] or 0, 2),
                    'minimum': humidity_stats['min_humidity'] or 0,
                    'maximum': humidity_stats['max_humidity'] or 0
                },
                'light': {
                    'average': round(lux_stats['avg_lux'] or 0, 2),
                    'minimum': lux_stats['min_lux'] or 0,
                    'maximum': lux_stats['max_lux'] or 0
                },
                'total_records': count_result['total_records']
            }
            
            return jsonify(statistics)
    except Exception as e:
        print(f"Error getting statistics: {e}")
        return jsonify({'error': 'Failed to get statistics'})

@app.route('/api/sensor/statistik_data')
def get_statistik_data():
    """API untuk mendapatkan statistik data dalam format khusus"""
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            
            # Statistik dasar suhu
            cursor.execute("SELECT AVG(suhu) as suhurata, MIN(suhu) as suhumin, MAX(suhu) as suhumax FROM data_sensor")
            temp_stats = cursor.fetchone()
            
            # PERBAIKAN 1: Data dengan nilai suhu maksimum ATAU humidity maksimum
            # Ambil data dengan suhu maksimum
            cursor.execute("""
                SELECT id as idx, suhu as suhun, humidity as humid, lux as kecerahan, timestamp 
                FROM data_sensor 
                WHERE suhu = (SELECT MAX(suhu) FROM data_sensor)
                ORDER BY timestamp DESC
                LIMIT 10
            """)
            suhu_max_data = cursor.fetchall()
            
            # Ambil data dengan humidity maksimum
            cursor.execute("""
                SELECT id as idx, suhu as suhun, humidity as humid, lux as kecerahan, timestamp 
                FROM data_sensor 
                WHERE humidity = (SELECT MAX(humidity) FROM data_sensor)
                ORDER BY timestamp DESC
                LIMIT 10
            """)
            humid_max_data = cursor.fetchall()
            
            # Gabungkan data dan hapus duplikasi
            max_values = []
            all_data = suhu_max_data + humid_max_data
            seen_ids = set()
            
            for item in all_data:
                if item['idx'] not in seen_ids:
                    seen_ids.add(item['idx'])
                    max_values.append(item)
            
            # Jika masih kosong, ambil 5 data dengan suhu tertinggi
            if not max_values:
                cursor.execute("""
                    SELECT id as idx, suhu as suhun, humidity as humid, lux as kecerahan, timestamp 
                    FROM data_sensor 
                    ORDER BY suhu DESC
                    LIMIT 5
                """)
                max_values = cursor.fetchall()
            
            # Format timestamp dan extract month-year
            month_year_max = []
            month_years_seen = set()
            
            for item in max_values:
                item['timestamp'] = item['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
                # Extract month-year
                timestamp_obj = datetime.strptime(item['timestamp'], '%Y-%m-%d %H:%M:%S')
                month_year = f"{timestamp_obj.month}-{timestamp_obj.year}"
                
                # Hindari duplikasi
                if month_year not in month_years_seen:
                    month_years_seen.add(month_year)
                    month_year_max.append({'month_year': month_year})
            
            # PERBAIKAN 2: Jika month_year_max masih kosong, ambil dari semua data
            if not month_year_max:
                cursor.execute("""
                    SELECT DISTINCT MONTH(timestamp) as month, YEAR(timestamp) as year
                    FROM data_sensor 
                    ORDER BY year DESC, month DESC
                    LIMIT 5
                """)
                date_data = cursor.fetchall()
                
                for date_item in date_data:
                    month_year = f"{date_item['month']}-{date_item['year']}"
                    month_year_max.append({'month_year': month_year})
            
            cursor.close()
            connection.close()
            
            # Format response sesuai permintaan
            statistik_data = {
                'suhumax': temp_stats['suhumax'] or 0,
                'suhumin': temp_stats['suhumin'] or 0,
                'suhurata': round(temp_stats['suhurata'] or 0, 2),
                'nilai_suhu_max_humid_max': max_values,
                'month_year_max': month_year_max
            }
            
            return jsonify(statistik_data)
    except Exception as e:
        print(f"Error getting statistik data: {e}")
        return jsonify({'error': 'Failed to get statistik data'})

@app.route('/api/relay/control', methods=['POST'])
def control_relay():
    """API untuk mengontrol relay"""
    try:
        data = request.get_json()
        relay_state = data.get('state', 'OFF')
        
        # Kirim perintah ke ESP32 via MQTT
        message = json.dumps({'relay': relay_state})
        mqtt_client.publish(MQTT_TOPIC_RELAY, message)
        
        return jsonify({'status': 'success', 'relay_state': relay_state})
    except Exception as e:
        print(f"Error controlling relay: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    # Mulai MQTT client di thread terpisah
    mqtt_thread = threading.Thread(target=start_mqtt)
    mqtt_thread.daemon = True
    mqtt_thread.start()
    
    # Jalankan Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)