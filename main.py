import os
import json
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

ZONA = ZoneInfo("Europe/Madrid")
PATRON_TITULO_BOT = re.compile(r"\(J\d+ - \d{2}/\d{2}/\d{4}\)$")

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
            payload_plano = {"chat_id": chat_id, "text": mensaje}
            response = requests.post(url, json=payload_plano, timeout=10)
            if response.status_code != 200:
                print(f"[Error] El reintento sin Markdown también falló: {response.text}")
    except Exception as e:
        print(f"[Error] Excepción al conectar con Telegram: {e}")

def calcular_anio_temporada(mes, temporada_inicio=None):
    if temporada_inicio:
        inicio = int(temporada_inicio)
    else:
        hoy = datetime.now(ZONA)
        inicio = hoy.year if hoy.month >= 8 else hoy.year - 1
    return inicio if mes >= 8 else inicio + 1

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
        temporada_inicio = os.environ.get("TEMPORADA_INICIO")
        
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
                        anio = calcular_anio_temporada(mes, temporada_inicio)
                        fecha_iso = f"{anio}-{fecha_corta.split('/')[1]}-{fecha_corta.split('/')[0]}"
                        fecha_titulo = f"{fecha_corta}/{anio}"
                        
                        if local == nombre_equipo:
                            rival = visitante
                            ubicacion = f"Estadio del {nombre_equipo}"
                            titulo_evento = f"{nombre_equipo} vs {rival} (J{contador_jornada} - {fecha_titulo})"
                        else:
                            rival = local
                            ubicacion = f"Estadio del {rival}"
                            titulo_evento = f"{rival} vs {nombre_equipo} (J{contador_jornada} - {fecha_titulo})"
                        
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

def es_evento_del_bot(titulo):
    return bool(PATRON_TITULO_BOT.search(titulo))

def sincronizar_con_google_calendar(partidos):
    calendar_id = os.environ.get("GOOGLE_CALENDAR_ID")
    json_creds = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    
    if not calendar_id or not json_creds:
        print("Error: Faltan credenciales de Google en los secretos de GitHub.")
        return

    try:
        creds_dict = json.loads(json_creds)
    except json.JSONDecodeError as e:
        print(f"Error: GOOGLE_SERVICE_ACCOUNT_JSON no es un JSON válido: {e}")
        return

    scopes = ['https://www.googleapis.com/auth/calendar']
    credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    service = build('calendar', 'v3', credentials=credentials)

    print("Conexión con Google Calendar establecida. Analizando eventos existentes...")

    eventos_actuales = []
    pagina = None
    while True:
        request = service.events().list(calendarId=calendar_id, maxResults=250, singleEvents=True, pageToken=pagina)
        events_result = request.execute()
        eventos_actuales.extend(events_result.get('items', []))
        pagina = events_result.get('nextPageToken')
        if not pagina:
            break

    mapa_eventos = {evt['summary']: evt for evt in eventos_actuales if 'summary' in evt}

    # Identificar las jornadas que aún no se han jugado (con zona horaria de Madrid)
    ahora_mismo = datetime.now(ZONA)
    jornadas_futuras = set()

    for p in partidos:
        p_str = f"{p['fecha_iso']}T{p['hora']}:00"
        p_dt = datetime.strptime(p_str, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=ZONA)
        if p_dt >= ahora_mismo:
            jornadas_futuras.add(p['jornada'])

    for p in partidos:
        start_str = f"{p['fecha_iso']}T{p['hora']}:00"
        start_dt = datetime.strptime(start_str, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=ZONA)
        end_dt = start_dt + timedelta(hours=2)
        
        evento_body = {
            'summary': p['titulo'],
            'location': p['ubicacion'],
            'description': "Partido oficial de LaLiga. Sincronización automática.",
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
                
                # Envía notificación si el partido modificado aún no se ha jugado
                if p['jornada'] in jornadas_futuras:
                    msg = (
                        f"🚨 *¡Cambio de horario detectado!*\n\n"
                        f"📌 *Partido:* {p['titulo']}\n"
                        f"❌ *Antes:* {fecha_antigua_str}\n"
                        f"✅ *Ahora:* {fecha_nueva_str}\n"
                        f"🏟️ *Lugar:* {p['ubicacion']}"
                    )
                    print(f"🔄 Cambio de horario detectado en J{p['jornada']} ({p['titulo']}). Enviando Telegram...")
                    enviar_alerta_telegram(msg)
                else:
                    print(f"🔄 Cambio de horario detectado en J{p['jornada']} ({p['titulo']}), pero el partido ya se ha jugado: se ignora la notificación.")
                
                # Google Calendar se actualiza SIEMPRE para mantener el calendario al día
                service.events().update(calendarId=calendar_id, eventId=existing_event['id'], body=evento_body).execute()
        else:
            print(f"🆕 Añadiendo nuevo partido al calendario: {p['titulo']}")
            service.events().insert(calendarId=calendar_id, body=evento_body).execute()

    # Limpieza de eventos huérfanos: borra los creados por el bot que ya no aparecen en el scrape
    titulos_scrapeados = {p['titulo'] for p in partidos}
    for evt in eventos_actuales:
        titulo = evt.get('summary')
        if titulo and es_evento_del_bot(titulo) and titulo not in titulos_scrapeados:
            print(f"🗑️ Eliminando evento huérfano del calendario: {titulo}")
            service.events().delete(calendarId=calendar_id, eventId=evt['id']).execute()

    print("\nSincronización del calendario finalizada con éxito.")

if __name__ == "__main__":
    load_dotenv()

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
