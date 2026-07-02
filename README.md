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

Para desplegar este bot, es necesario clonar el repositorio y configurar las siguientes llaves secretas en `Settings > Secrets and variables > Actions`:

| Secreto | Tipo / Formato | Descripción |
| :--- | :--- | :--- |
| `EQUIPO_OBJETIVO` | Texto plano | Nombre exacto del equipo tal y como aparece en la web (ej: `Real Madrid`, `Zaragoza`, `Castellón`). |
| `URL_LIV_DIVISION` | URL | Enlace al calendario de El Mundo (`/primera-division/calendario.html` o `/segunda-division/calendario.html`). |
| `GOOGLE_CALENDAR_ID` | String / Email | Identificador del calendario dedicado de Google creado para el equipo. |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | JSON | Bloque de credenciales completo de la cuenta de servicio de Google Cloud. |
| `TELEGRAM_BOT_TOKEN` | Token numérico | Llave de autenticación del bot proporcionada por `@BotFather`. |
| `TELEGRAM_CHAT_ID` | Numérico | ID de tu chat personal de Telegram (obtenido vía `@userinfobot`). |

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
