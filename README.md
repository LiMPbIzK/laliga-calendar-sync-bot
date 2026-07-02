---

## ⚙️ Variables de Entorno y Secretos (GitHub Secrets)

Para desplegar este bot, es necesario configurar las siguientes llaves secretas en "Settings > Secrets and variables > Actions".

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
