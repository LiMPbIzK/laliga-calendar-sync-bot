# ⚽ LaLiga Dynamic Calendar Sync Bot

Sistema automatizado, parametrizable y *serverless* para la sincronización de horarios y notificación de partidos de fútbol de Primera y Segunda División española en tiempo real. 

A diferencia de las soluciones estáticas, este repositorio permite a cualquier usuario configurar el equipo de su elección mediante variables de entorno. El script raspa el calendario oficial, actualiza un calendario dedicado en **Google Calendar** y despacha alertas inmediatas a **Telegram** únicamente si se detectan modificaciones críticas en el horario de la jornada más cercana.

---

## 🛠️ Arquitectura y Tecnologías

El sistema está diseñado bajo un modelo asíncrono de consumo cero (sin servidores *always-on*), aprovechando entornos virtuales temporales:

* **Lenguaje:** Python 3.11+
* **Web Scraping:** Beautiful Soup 4 & Requests (Estructuración dinámica de tablas HTML).
* **Integración de Calendario:** Google Calendar API v3 (Autenticación robusta mediante OAuth2 Service Account).
* **Notificaciones:** Telegram Bot API (Envío de alertas asíncronas vía HTTP POST).
* **Automatización (CI/CD):** GitHub Actions (Planificador de tareas Cron cada 4 horas).

---

## 🔄 Flujo de Trabajo (Workflow)

El ciclo de ejecución sigue una lógica estructurada de cuatro pasos:

1. **Activación:** GitHub Actions levanta el entorno en la nube de forma automatizada cada 4 horas.
2. **Extracción Dinámica:** El script consume la URL de la división configurada, localiza las filas correspondientes al equipo objetivo y parsea las cadenas de texto para extraer rivales, fechas (ISO), horas y campos de ubicación.
3. **Evaluación de Delta:** Compara minuciosamente la marca de tiempo (timestamp) de la web con el evento agendado en Google Calendar.
   * *Si no hay cambios:* El proceso termina limpiamente ahorrando operaciones de escritura.
   * *Si hay desfase horario:* Actualiza la API de Google Calendar y calcula el impacto temporal del cambio.
4. **Filtrado Inteligente de Alertas:**
   * *Partido Lejano:* Si el partido modificado pertenece a jornadas lejanas, se sincroniza en silencio en el calendario para evitar saturación.
   * *Jornada Inmediata:* Si el cambio afecta al próximo partido cronológico del equipo a partir de la fecha actual, se dispara una alerta estructurada al bot de Telegram.

---

## ⚙️ Variables de Entorno y Secretos (GitHub Secrets)

Para desplegar este bot, es necesario configurar las siguientes llaves secretas en `Settings > Secrets and variables > Actions`.

> ⚠️ **IMPORTANTE:** El valor de `EQUIPO_OBJETIVO` debe coincidir exactamente con el nombre que utiliza la web emisora. Copia y pega el nombre de tu equipo directamente desde los siguientes desplegables:

<details>
<summary>📋 Ver nombres exactos de PRIMERA DIVISIÓN</summary>

* Alavés
* Athletic Club
* Atlético de Madrid
* Barcelona
* Celta de Vigo
* Deportivo de A Coruña
* Elche
* Espanyol
* Getafe
* Levante
* Málaga
* Osasuna
* Racing de Santander
* Rayo Vallecano
* Real Betis
* Real Madrid
* Real Sociedad
* Sevilla
* Valencia
* Villarreal

</details>

<details>
<summary>📋 Ver nombres exactos de SEGUNDA DIVISIÓN</summary>

* Albacete
* Almería
* Andorra
* Burgos
* Cádiz
* Castellón
* Celta Fortuna
* Ceuta
* Córdoba
* Eibar
* Eldense
* Girona
* Granada
* Las Palmas
* Leganés
* Mallorca
* Real Oviedo
* Real Sociedad "B"
* Real Valladolid
* Sabadell
* Sporting de Gijón
* Tenerife

</details>

### Tabla de Configuración de Secretos

| Secreto | Tipo / Formato | Descripción |
| :--- | :--- | :--- |
| `EQUIPO_OBJETIVO` | Texto plano | El nombre exacto de tu equipo (Ej: Real Madrid, Eldense). |
| `URL_LIV_DIVISION` | URL | URL del calendario de El Mundo (Primera o Segunda división). |
| `GOOGLE_CALENDAR_ID` | Texto plano | Identificador del calendario dedicado de Google. |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | JSON | Bloque de credenciales completo de la cuenta de servicio de Google Cloud. |
| `TELEGRAM_BOT_TOKEN` | Texto plano | Llave de autenticación del bot de @BotFather. |
| `TELEGRAM_CHAT_ID` | Numérico | ID de tu chat personal de Telegram. |

---

## 📋 Formato de las Alertas (Telegram)

Las alertas utilizan la pasarela oficial de Telegram con formato `Markdown`, entregando notificaciones compactas y legibles en dispositivos móviles:

🚨 ¡Cambio de horario en la próxima jornada!

📌 Partido: [Tu Equipo] vs [Rival] (Jornada X)
❌ Antes: DD/MM a las HH:MM
✅ Ahora: DD/MM a las HH:MM
🏟️ Lugar: Estadio del encuentro

---

## 🚀 Despliegue Local (Desarrollo)

Para realizar pruebas de desarrollo o depuración en local:

1. Clonar el repositorio:
   git clone https://github.com/tu-usuario/laliga-calendar-sync-bot.git
   cd laliga-calendar-sync-bot

2. Instalar dependencias:
   pip install -r requirements.txt

3. Exportar las variables de entorno en tu entorno local y ejecutar el punto de entrada:
   python main.py
