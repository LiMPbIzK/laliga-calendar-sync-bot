# ⚽ LaLiga Dynamic Calendar Sync Bot

Sistema automatizado, parametrizable y *serverless* para la sincronización de horarios y notificación de partidos de fútbol de Primera y Segunda División española en tiempo real. 

A diferencia de las soluciones estáticas, este repositorio permite a cualquier usuario configurar el equipo de su elección mediante variables de entorno. El script raspa el calendario oficial, actualiza un calendario dedicado en **Google Calendar** y despacha alertas inmediatas a **Telegram** únicamente si se detectan modificaciones críticas en el horario de la jornada más cercana.

---

## 🛠️ Arquitectura y Tecnologías

El sistema está diseñado bajo un modelo asíncrono de consumo cero (sin servidores *always-on*), aprovechando entornos virtuales temporales:

* **Lenguaje:** Python 3.11+
* **Web Scraping:** Beautiful Soup 4 & Requests (Estructuración dinámica de tablas HTML).``
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
* Athletic
* Atlético
* Barcelona
* Betis
* Celta
* Deportivo
* Elche
* Espanyol
* Getafe
* Levante
* Málaga
* Osasuna
* Racing
* Rayo
* Real Madrid
* R. Sociedad
* Sevilla
* Valencia
* Villarreal

</details>

<details>
<summary>📋 Ver nombres exactos de SEGUNDA DIVISIÓN</summary>

* Albacete
* Almería
* Burgos
* Cádiz
* Castellón
* Celta de Vigo B
* Ceuta
* Córdoba
* Eibar
* Eldense
* FC Andorra
* Girona
* Granada
* Las Palmas
* Leganés
* Mallorca
* Oviedo
* Real Sociedad B
* Sabadell
* Sporting
* Tenerife
* Valladolid

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

3. Configurar variables de entorno locales (VS Code):
   Crea un archivo llamado .env en la raíz del proyecto (protege este archivo mediante .gitignore para no exponer tus credenciales de forma pública).
   Añade tus datos con el siguiente formato:

   EQUIPO_OBJETIVO="tu_equipo_aqui"
   URL_LIV_DIVISION="https://www.elmundo.es/deportes/futbol/segunda-division/calendario.html"
   TELEGRAM_BOT_TOKEN="tu_token_aqui"
   TELEGRAM_CHAT_ID="tu_chat_id_aqui"
   GOOGLE_CALENDAR_ID="tu_calendar_id_aqui"
   GOOGLE_SERVICE_ACCOUNT_JSON='{"type": "service_account", ...}'

5. Ejecutar el punto de entrada:
   python main.py

## 🔑 Obtención de Credenciales de Google

Si necesitas generar las credenciales de Google desde cero, sigue estos pasos para obtener los valores requeridos:

### 1. Para el `GOOGLE_SERVICE_ACCOUNT_JSON`
Este archivo se genera creando un proyecto y una cuenta de servicio en la consola de desarrolladores de Google.

* **URL de la plataforma:** [Google Cloud Console](https://console.cloud.google.com/)
* **Pasos a seguir:**
  1. Crea un proyecto nuevo.
  2. Busca la **API de Google Calendar** en el buscador superior y haz clic en **Habilitar**.
  3. Ve al menú lateral izquierdo: **IAM y administración** > **Cuentas de servicio**.
  4. Crea una cuenta de servicio (puedes llamarla `bot-futbol`).
  5. Entra en la cuenta de servicio recién creada, ve a la pestaña **Claves (Keys)** > **Agregar clave** > **Crear clave nueva** en formato **JSON**. Al pulsar ahí, se descargará automáticamente el archivo de texto que debes pegar en tu secreto.

### 2. Para el `GOOGLE_CALENDAR_ID`
Este identificador se extrae de la interfaz normal de tu cuenta de Google Calendar, tras crear el calendario dedicado para los partidos.

* **URL de la plataforma:** [Google Calendar](https://calendar.google.com/)
* **Pasos a seguir:**
  1. En el menú de la izquierda, junto a "Otros calendarios", haz clic en el botón **+** > **Crear un calendario** (ej: *Partidos de Fútbol*).
  2. Una vez creado, entra en la **Configuración** de ese calendario específico.
  3. Baja hasta la sección llamada **Integrar el calendario**.
  4. Ahí verás un campo que dice **ID del calendario** (suele tener un formato como `cadena_aleatoria@group.calendar.google.com`). Ese texto es tu ID.

> ⚠️ **Paso obligatorio de vinculación:** Para que la cuenta de servicio pueda escribir en tu calendario, debes ir a la sección **Compartir con personas específicas o grupos** de la configuración de tu calendario, añadir el email largo de la cuenta de servicio (lo encontrarás dentro del archivo JSON) y asignarle el permiso de **Hacer cambios y administrar la compartición**.
