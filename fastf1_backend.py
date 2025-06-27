# scripts/live_bridge.py
import asyncio
import time
import base64
import zlib
import json
import math
import os
import websockets
import requests
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading


# 🗂 Rutas
BASE_PATH = r"C:\Users\Aaron\AppData\Local\undercut-f1\data"
LIVE_TXT = None
SUBSCRIBE_TXT = None
avoid = 0
WIDTH = 800
HEIGHT = 600
ROTATION = 108
MIRROR_Y = True
driver_info_map = {}
clients = set()
bounds = None
car_data_store = {}
track_data = []
HARDCODED_DRIVERLIST = {"Type":"DriverList","Json":{"1":{"RacingNumber":"1","BroadcastName":"M VERSTAPPEN","FullName":"Max VERSTAPPEN","Tla":"VER","Line":1,"TeamName":"Red Bull Racing","TeamColour":"4781D7","FirstName":"Max","LastName":"Verstappen","Reference":"MAXVER01","HeadshotUrl":"https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/M/MAXVER01_Max_Verstappen/maxver01.png.transform/1col/image.png","PublicIdRight":"common/f1/2025/redbullracing/maxver01/2025redbullracingmaxver01right"},"4":{"RacingNumber":"4","BroadcastName":"L NORRIS","FullName":"Lando NORRIS","Tla":"NOR","Line":2,"TeamName":"McLaren","TeamColour":"F47600","FirstName":"Lando","LastName":"Norris","Reference":"LANNOR01","HeadshotUrl":"https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/L/LANNOR01_Lando_Norris/lannor01.png.transform/1col/image.png","PublicIdRight":"common/f1/2025/mclaren/lannor01/2025mclarenlannor01right"},"5":{"RacingNumber":"5","BroadcastName":"G BORTOLETO","FullName":"Gabriel BORTOLETO","Tla":"BOR","Line":3,"TeamName":"Kick Sauber","TeamColour":"01C00E","FirstName":"Gabriel","LastName":"Bortoleto","Reference":"GABBOR01","HeadshotUrl":"https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/G/GABBOR01_Gabriel_Bortoleto/gabbor01.png.transform/1col/image.png","PublicIdRight":"common/f1/2025/kicksauber/gabbor01/2025kicksaubergabbor01right"},"6":{"RacingNumber":"6","BroadcastName":"I HADJAR","FullName":"Isack HADJAR","Tla":"HAD","Line":4,"TeamName":"Racing Bulls","TeamColour":"6C98FF","FirstName":"Isack","LastName":"Hadjar","Reference":"ISAHAD01","HeadshotUrl":"https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/I/ISAHAD01_Isack_Hadjar/isahad01.png.transform/1col/image.png","PublicIdRight":"common/f1/2025/racingbulls/isahad01/2025racingbullsisahad01right"},"10":{"RacingNumber":"10","BroadcastName":"P GASLY","FullName":"Pierre GASLY","Tla":"GAS","Line":5,"TeamName":"Alpine","TeamColour":"00A1E8","FirstName":"Pierre","LastName":"Gasly","Reference":"PIEGAS01","HeadshotUrl":"https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/P/PIEGAS01_Pierre_Gasly/piegas01.png.transform/1col/image.png","PublicIdRight":"common/f1/2025/alpine/piegas01/2025alpinepiegas01right"},"12":{"RacingNumber":"12","BroadcastName":"K ANTONELLI","FullName":"Kimi ANTONELLI","Tla":"ANT","Line":6,"TeamName":"Mercedes","TeamColour":"00D7B6","FirstName":"Kimi","LastName":"Antonelli","Reference":"ANDANT01","HeadshotUrl":"https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/A/ANDANT01_Andrea%20Kimi_Antonelli/andant01.png.transform/1col/image.png","PublicIdRight":"common/f1/2025/mercedes/andant01/2025mercedesandant01right"},"14":{"RacingNumber":"14","BroadcastName":"F ALONSO","FullName":"Fernando ALONSO","Tla":"ALO","Line":7,"TeamName":"Aston Martin","TeamColour":"229971","FirstName":"Fernando","LastName":"Alonso","Reference":"FERALO01","HeadshotUrl":"https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/F/FERALO01_Fernando_Alonso/feralo01.png.transform/1col/image.png","PublicIdRight":"common/f1/2025/astonmartin/feralo01/2025astonmartinferalo01right"},"16":{"RacingNumber":"16","BroadcastName":"C LECLERC","FullName":"Charles LECLERC","Tla":"LEC","Line":8,"TeamName":"Ferrari","TeamColour":"ED1131","FirstName":"Charles","LastName":"Leclerc","Reference":"CHALEC01","HeadshotUrl":"https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/C/CHALEC01_Charles_Leclerc/chalec01.png.transform/1col/image.png","PublicIdRight":"common/f1/2025/ferrari/chalec01/2025ferrarichalec01right"},"18":{"RacingNumber":"18","BroadcastName":"L STROLL","FullName":"Lance STROLL","Tla":"STR","Line":9,"TeamName":"Aston Martin","TeamColour":"229971","FirstName":"Lance","LastName":"Stroll","Reference":"LANSTR01","HeadshotUrl":"https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/L/LANSTR01_Lance_Stroll/lanstr01.png.transform/1col/image.png","PublicIdRight":"common/f1/2025/astonmartin/lanstr01/2025astonmartinlanstr01right"},"22":{"RacingNumber":"22","BroadcastName":"Y TSUNODA","FullName":"Yuki TSUNODA","Tla":"TSU","Line":10,"TeamName":"Red Bull Racing","TeamColour":"4781D7","FirstName":"Yuki","LastName":"Tsunoda","Reference":"YUKTSU01","HeadshotUrl":"https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/Y/YUKTSU01_Yuki_Tsunoda/yuktsu01.png.transform/1col/image.png","PublicIdRight":"common/f1/2025/redbullracing/yuktsu01/2025redbullracingyuktsu01right"},"23":{"RacingNumber":"23","BroadcastName":"A ALBON","FullName":"Alexander ALBON","Tla":"ALB","Line":11,"TeamName":"Williams","TeamColour":"1868DB","FirstName":"Alexander","LastName":"Albon","Reference":"ALEALB01","HeadshotUrl":"https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/A/ALEALB01_Alexander_Albon/alealb01.png.transform/1col/image.png","PublicIdRight":"common/f1/2025/williams/alealb01/2025williamsalealb01right"},"27":{"RacingNumber":"27","BroadcastName":"N HULKENBERG","FullName":"Nico HULKENBERG","Tla":"HUL","Line":12,"TeamName":"Kick Sauber","TeamColour":"01C00E","FirstName":"Nico","LastName":"Hulkenberg","Reference":"NICHUL01","HeadshotUrl":"https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/N/NICHUL01_Nico_Hulkenberg/nichul01.png.transform/1col/image.png","PublicIdRight":"common/f1/2025/kicksauber/nichul01/2025kicksaubernichul01right"},"30":{"RacingNumber":"30","BroadcastName":"L LAWSON","FullName":"Liam LAWSON","Tla":"LAW","Line":13,"TeamName":"Racing Bulls","TeamColour":"6C98FF","FirstName":"Liam","LastName":"Lawson","Reference":"LIALAW01","HeadshotUrl":"https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/L/LIALAW01_Liam_Lawson/lialaw01.png.transform/1col/image.png","PublicIdRight":"common/f1/2025/racingbulls/lialaw01/2025racingbullslialaw01right"},"31":{"RacingNumber":"31","BroadcastName":"E OCON","FullName":"Esteban OCON","Tla":"OCO","Line":14,"TeamName":"Haas F1 Team","TeamColour":"9C9FA2","FirstName":"Esteban","LastName":"Ocon","Reference":"ESTOCO01","HeadshotUrl":"https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/E/ESTOCO01_Esteban_Ocon/estoco01.png.transform/1col/image.png","PublicIdRight":"common/f1/2025/haas/estoco01/2025haasestoco01right"},"43":{"RacingNumber":"43","BroadcastName":"F COLAPINTO","FullName":"Franco COLAPINTO","Tla":"COL","Line":15,"TeamName":"Alpine","TeamColour":"00A1E8","FirstName":"Franco","LastName":"Colapinto","Reference":"FRACOL01","PublicIdRight":"common/f1/2025/alpine/fracol01/2025alpinefracol01right"},"44":{"RacingNumber":"44","BroadcastName":"L HAMILTON","FullName":"Lewis HAMILTON","Tla":"HAM","Line":16,"TeamName":"Ferrari","TeamColour":"ED1131","FirstName":"Lewis","LastName":"Hamilton","Reference":"LEWHAM01","HeadshotUrl":"https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/L/LEWHAM01_Lewis_Hamilton/lewham01.png.transform/1col/image.png","PublicIdRight":"common/f1/2025/ferrari/lewham01/2025ferrarilewham01right"},"55":{"RacingNumber":"55","BroadcastName":"C SAINZ","FullName":"Carlos SAINZ","Tla":"SAI","Line":17,"TeamName":"Williams","TeamColour":"1868DB","FirstName":"Carlos","LastName":"Sainz","Reference":"CARSAI01","HeadshotUrl":"https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/C/CARSAI01_Carlos_Sainz/carsai01.png.transform/1col/image.png","PublicIdRight":"common/f1/2025/williams/carsai01/2025williamscarsai01right"},"63":{"RacingNumber":"63","BroadcastName":"G RUSSELL","FullName":"George RUSSELL","Tla":"RUS","Line":18,"TeamName":"Mercedes","TeamColour":"00D7B6","FirstName":"George","LastName":"Russell","Reference":"GEORUS01","HeadshotUrl":"https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/G/GEORUS01_George_Russell/georus01.png.transform/1col/image.png","PublicIdRight":"common/f1/2025/mercedes/georus01/2025mercedesgeorus01right"},"81":{"RacingNumber":"81","BroadcastName":"O PIASTRI","FullName":"Oscar PIASTRI","Tla":"PIA","Line":19,"TeamName":"McLaren","TeamColour":"F47600","FirstName":"Oscar","LastName":"Piastri","Reference":"OSCPIA01","HeadshotUrl":"https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/O/OSCPIA01_Oscar_Piastri/oscpia01.png.transform/1col/image.png","PublicIdRight":"common/f1/2025/mclaren/oscpia01/2025mclarenoscpia01right"},"87":{"RacingNumber":"87","BroadcastName":"O BEARMAN","FullName":"Oliver BEARMAN","Tla":"BEA","Line":20,"TeamName":"Haas F1 Team","TeamColour":"9C9FA2","FirstName":"Oliver","LastName":"Bearman","Reference":"OLIBEA01","HeadshotUrl":"https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/O/OLIBEA01_Oliver_Bearman/olibea01.png.transform/1col/image.png","PublicIdRight":"common/f1/2025/haas/olibea01/2025haasolibea01right"}},"DateTime":"2025-06-13T17:16:04.2952839+00:00"}



# 🧩 Utilidades de compresión
def decode_payload(payload: str) -> dict:
    raw = base64.b64decode(payload)
    decompressed = zlib.decompress(raw, -zlib.MAX_WBITS)
    return json.loads(decompressed)

# 📐 Coordenadas
def calculate_transform_factors(track_points, svg_width=800, svg_height=600, padding=50,rotation=108):
    """Calcula los factores de escala y desplazamiento para el circuito."""
    # 1. Encontrar los límites del circuito
    min_x = min(p["x"] for p in track_points)
    max_x = max(p["x"] for p in track_points)
    min_y = min(p["y"] for p in track_points)
    max_y = max(p["y"] for p in track_points)
    
    # 2. Calcular dimensiones originales
    original_width = max_x - min_x
    original_height = max_y - min_y
    
    # 3. Calcular escala manteniendo aspect ratio
    available_width = svg_width - 2 * padding
    available_height = svg_height - 2 * padding
    
    scale_x = available_width / original_width
    scale_y = available_height / original_height
    scale = min(scale_x, scale_y)  # Para no distorsionar
    
    # 4. Devolver estructura con factores
    return {
        "scale": scale,
        "min_x": min_x,
        "min_y": min_y,
        "padding": padding,
        "rotation": rotation,
        "svg_width": svg_width,
        "svg_height": svg_height
    }

def transform_coords(x, y, transform):
    x_scaled = x * transform["scale"] + transform["padding"]
    y_scaled = y * transform["scale"] + transform["padding"]
    if MIRROR_Y:
        y_scaled = transform["svg_height"] - y_scaled

    cx = WIDTH  / 2
    cy = HEIGHT  / 2
    angle_rad = math.radians(transform["rotation"])
    x_rot = math.cos(angle_rad) * (x_scaled - cx) - math.sin(angle_rad) * (y_scaled - cy) + cx
    y_rot = math.sin(angle_rad) * (x_scaled - cx) + math.cos(angle_rad) * (y_scaled - cy) + cy
    return x_rot, y_rot

def update_bounds(entries):
    global bounds
    xs = [e["Long"] for e in entries if "Long" in e]
    ys = [e["Lat"] for e in entries if "Lat" in e]
    if not xs or not ys:
        return
    bounds = {
        'min_x': min(xs), 'max_x': max(xs),
        'min_y': min(ys), 'max_y': max(ys),
        'x_range': max(xs) - min(xs),
        'y_range': max(ys) - min(ys)
    }

# 📡 Obtener trazado del circuito
def load_track_from_api(subscribe_path):
    global track_data, bounds, transform_factors
    try:
        with open(subscribe_path, "r", encoding="utf-8-sig") as f:
            info = json.load(f)
            circuit_key = info["SessionInfo"]["Meeting"]["Circuit"]["Key"]
            year = info["SessionInfo"]["Meeting"]["Number"]
    except Exception as e:
        print("❌ No se pudo leer subscribe.txt:", e)
        return

    url = f"https://api.multiviewer.app/api/v1/circuits/{circuit_key}/2025"
    print("🌐 Descargando trazado desde:", url)
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        data = r.json()
        corners = data.get("corners", [])
        raw_points = [{"x": pt["trackPosition"]["x"], "y": pt["trackPosition"]["y"]} for pt in corners]
        if not raw_points:
            return

        # Bounds artificiales para SVG (basado en x/y del trazado)
        xs = [p["x"] for p in raw_points]
        ys = [p["y"] for p in raw_points]
        bounds = {
            'min_x': min(xs), 'max_x': max(xs),
            'min_y': min(ys), 'max_y': max(ys),
            'x_range': max(xs) - min(xs),
            'y_range': max(ys) - min(ys)
        }
        transform_factors = calculate_transform_factors(
        [{"x": p["x"], "y": p["y"]} for p in raw_points]
    )

        track_data = [ { "x": transform_coords(p["x"], p["y"], transform_factors)[0],
                         "y": transform_coords(p["x"], p["y"], transform_factors)[1] }
                       for p in raw_points ]
        print(f"✅ Trazado cargado: {len(track_data)} puntos.")
    except Exception as e:
        print("❌ Error al obtener el circuito:", e)

async def broadcast(msg):
    to_remove = []
    for client in clients:
        try:
            await client.send(json.dumps(msg))
        except websockets.exceptions.ConnectionClosed:
            to_remove.append(client)
    
    for client in to_remove:
        clients.remove(client)

def load_drivers ():
    try:
        json_field = HARDCODED_DRIVERLIST["Json"]
        for drv_num, info in json_field.items():
            team_color = info.get("TeamColour")
            team_name = info.get("TeamName")
            if not team_color or not team_name:
                continue
            driver_info_map[drv_num] = {
                "acronym": info.get("Tla"),
                "team_name": info.get("TeamName"),
                "team_color": "#" + info.get("TeamColour"),
                "racing_number": drv_num
            }
    except Exception as e:
        print("❌ No se pudo cargar los pilotos:", e)
        return    
# 🔁 Loop principal
async def send_loop():
    seen = set()
    positions = {}

    print("🌀 Iniciando bucle de envío...")
    while True:
        if not os.path.exists(LIVE_TXT):
            await asyncio.sleep(1)
            continue

        try:
            with open(LIVE_TXT, "r", encoding="utf-8-sig") as f:
                for line in f:
                    if line in seen or not line.strip():
                        continue
                    seen.add(line)

                    try:
                        data = json.loads(line)

                        # Soporte para líneas tipo SignalR
                        if "H" in data and data["H"] == "Streaming" and "A" in data:
                            a = data["A"]
                            if isinstance(a, list) and len(a) >= 2 and isinstance(a[0], str):
                                
                                typ = a[0]
                                payload = a[1]
                                timestamp = a[2] if len(a) > 2 else None
                                    
                                        

                                if typ == "Position.z":
                                    decoded = decode_payload(payload)
                                    position_block = decoded.get("Position", [{}])[0]
                                    entries = position_block.get("Entries", {})

                                    update_bounds(entries)
                                    positions = {}

                                    for drv_num, e in entries.items():
                                        if "X" not in e or "Y" not in e:
                                            continue
                                        x, y = transform_coords(e["X"], e["Y"], transform_factors)
                                        driver_info = driver_info_map.get(drv_num, {})
                                        positions[drv_num] = {
                                            "driver_code": drv_num,
                                            "position": e.get("Position", 0),
                                            "x": x,
                                            "y": y,
                                            "status": e.get("Status", "N"),
                                            "speed": e.get("Spd"),
                                            "drs": e.get("Drs"),
                                            "acronym": driver_info.get("acronym", ""),
                                            "team_color": driver_info.get("team_color", "#666666"),
                                            "team_name": driver_info.get("team_name", "")
                                        }
                                        

                                    if positions:
                                        await broadcast({
                                            "type": "positions_update",
                                            "data": positions,
                                            "lap": decoded.get("R", 0),
                                            "timestamp": datetime.utcnow().isoformat()
                                        })

                    except Exception as e:
                        print("⚠️ Error procesando línea:", e)

        except Exception as e:
            print("❌ Error abriendo live.txt:", e)

        await asyncio.sleep(0.25)  # 💤 espera pequeña para no saturar CPU




async def handler(websocket):
    clients.add(websocket)
    
    if track_data:
        await websocket.send(json.dumps({ "type": "track_data", "data": track_data }))
    try:
        await websocket.wait_closed()
    finally:
        clients.remove(websocket)


async def main():

    print("🚀 Servidor WebSocket en ws://localhost:8765")
    async with websockets.serve(handler, "localhost", 8765):
        load_track_from_api(SUBSCRIBE_TXT)
        load_drivers()
        await send_loop()

if __name__ == "__main__":
    folders = sorted([f for f in os.listdir(BASE_PATH) if os.path.isdir(os.path.join(BASE_PATH, f))], reverse=True)
    if folders:
        session_path = os.path.join(BASE_PATH, folders[0])
        print(f"Session path: {session_path}")
        
        LIVE_TXT = os.path.join(session_path, "live.txt")
        SUBSCRIBE_TXT = os.path.join(session_path, "subscribe.txt")
        
        if os.path.exists(SUBSCRIBE_TXT):
            load_track_from_api(SUBSCRIBE_TXT)
else:
    print("subscribe.txt NO encontrado")

asyncio.run(main())
