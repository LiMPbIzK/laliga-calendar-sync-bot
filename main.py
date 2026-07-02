import os
import json
import requests
from bs4 import BeautifulSoup
import re
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta

def enviar_alerta_telegram(mensaje):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        print("[Aviso] Telegram no configurado o faltan variables de entorno.")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": mensaje,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code != 200:
            print(f"[Error] No se pudo enviar el mensaje a Telegram: {response.text}")
    except Exception as e:
        print(f"[Error] Excepción al conectar con Telegram: {e}")

def extraer_calendario_elmundo(url_division, nombre_equipo):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url_division, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"[Error] No se pudo acceder a la URL: {url_division}")
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        filas_partidos = soup.find_all('tr')
        partidos_estructurados = []
        contador_jornada = 1
        
        for fila in filas_partidos:
            texto = fila.get_text()
            if nombre_equipo in texto:
                texto_limpio = " ".join(texto.split()).strip()
                if len(texto_limpio) > 15:
                    match = re.search(r'^(.*?)\s+(\d{2}/\d{2})\s+(\d{2}:\d{2})\s+(.*)$', texto_limpio)
                    if match:
                        local = match.group(1).strip()
                        fecha_corta = match.group(2).strip()
                        hora = match.group(3).strip()
                        visitante = match.group(4).strip()
                        
                        mes = int(fecha_corta.split('/')[1])
                        anio = 2026 if mes >= 8 else 2027
                        fecha_iso = f"{anio}-{fecha_corta.split('/')[1]}-{fecha_corta.split('/')[0]}"
                        
                        if local == nombre_equipo:
                            rival = visitante
                            ubicacion = f"Estadio del {nombre_equipo}"
                            titulo_evento = f"{nombre_equipo} vs {rival} (J{contador_jornada})"
                        else:
                            rival = local
                            ubicacion = f"Estadio del {rival}"
                            titulo_evento = f"{rival} vs {nombre_equipo} (J{contador_jornada})"
                        
                        partidos_estructurados.append({
                            "jornada": contador_jornada,
                            "titulo": titulo_evento,
                            "fecha_iso": fecha_iso,
                            "hora": hora,
                            "ubicacion": ubicacion
                        })
                        contador_jornada += 1
        return partidos_estructurados
    except Exception as e:
        print(f"Error en extracción: {e}")
        return []

def sincronizar_con_google_calendar(partidos):
    calendar_id = os.environ.get("GOOGLE_CALENDAR_ID")
    json_creds = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    
    if not calendar_id or not json_creds:
        print("Error: Faltan credenciales de Google en los secretos de GitHub.")
        return

    scopes = ['https://www.googleapis.com/auth/calendar']
    creds_dict = json.loads(json_creds)
    credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    service = build('calendar', 'v3', credentials=credentials)

    print("Conexión con Google Calendar establecida. Analizando eventos existentes...")

    events_result = service.events().list(calendarId=calendar_id, maxResults=250, singleEvents=True).execute()
    eventos_actuales = events_result.get('items', [])
    mapa_eventos = {evt['summary']: evt for evt in eventos_actuales if 'summary' in evt}

    ahora_mismo = datetime.now()
    proximos_partidos = []
    
    for p in partidos:
        p_str = f"{p['fecha_iso']}T{p['hora']}:00"
        p_dt = datetime.strptime(p_str, "%Y-%m-%dT%H:%M:%S")
        if p_dt >= ahora_mismo:
            proximos_partidos.append((p_dt, p['jornada']))
            
    jornada_siguiente = min(proximos_partidos, key=lambda x: x[0])[1] if proximos_partidos else None

    for p in partidos:
        start_str = f"{p['fecha_iso']}T{p['hora']}:00"
        start_dt = datetime.strptime(start_str, "%Y-%m-%dT%H:%M:%S")
        end_dt = start_dt + timedelta(hours=2)
        
        evento_body = {
            'summary': p['titulo'],
            'location': p['ubicacion'],
            'description': f"Partido oficial de LaLiga. Sincronización automática.",
            'start': {'dateTime': start_dt.isoformat(), 'timeZone': 'Europe/Madrid'},
            'end': {'dateTime': end_dt.isoformat(), 'timeZone': 'Europe/Madrid'},
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': 60}
                ]
            }
        }

        if p['titulo'] in mapa_eventos:
            existing_event = mapa_eventos[p['titulo']]
            existing_start = existing_event['start'].get('dateTime', '')[:16]
            target_start = start_dt.isoformat()[:16]

            if existing_start != target_start:
                fecha_antigua_dt = datetime.fromisoformat(existing_event['start']['dateTime'][:19])
                fecha_antigua_str = fecha_antigua_dt.strftime("%d/%m a las %H:%M")
                fecha_nueva_str = start_dt.strftime("%d/%m a las %H:%M")
                
                if p['jornada'] == jornada_siguiente:
                    msg = (
                        f"🚨 *¡Cambio de horario en la próxima jornada!*\n\n"
                        f"📌 *Partido:* {p['titulo']}\n"
                        f"❌ *Antes:* {fecha_antigua_str}\n"
                        f"✅ *Ahora:* {fecha_nueva_str}\n"
                        f"🏟️ *Lugar:* {p['ubicacion']}"
                    )
                    print(f"🔄 Cambio crítico detectado en la jornada siguiente (J{p['jornada']}). Enviando Telegram...")
                    enviar_alerta_telegram(msg)
                else:
                    print(f"🔄 Cambio de horario detectado en J{p['jornada']} ({p['titulo']}), pero se ignora la notificación por no ser la jornada inmediata.")
                
                service.events().update(calendarId=calendar_id, eventId=existing_event['id'], body=evento_body).execute()
        else:
            print(f"🆕 Añadiendo nuevo partido al calendario: {p['titulo']}")
            service.events().insert(calendarId=calendar_id, body=evento_body).execute()

    print("\nSincronización del calendario finalizada con éxito.")

if __name__ == "__main__":
    EQUIPO = os.environ.get("EQUIPO_OBJETIVO")
    URL_LIGA = os.environ.get("URL_LIV_DIVISION")
    
    if not EQUIPO or not URL_LIGA:
        print("[Error] Faltan las variables de entorno EQUIPO_OBJETIVO o URL_LIV_DIVISION.")
        exit(1)
        
    print(f"Iniciando Bot de Calendario Dinámico para el: {EQUIPO}...")
    lista_partidos = extraer_calendario_elmundo(URL_LIGA, EQUIPO)
    if lista_partidos:
        sincronizar_con_google_calendar(lista_partidos)
    else:
        print("No se pudieron extraer los partidos.")
