import asyncio
import logging
import os
import sys
import time

from app.integrations.telegram import Alert, send_telegram_alert
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

logger = logging.getLogger("telegram alerts")


load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL"))

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
INTERVAL_SEC = int(os.getenv("SIMULATOR_WAIT_TIME", "30"))

def get_rows_without_alert():
    query_first = text("""
        SELECT severity, message, id FROM alerts WHERE (sent_at IS NULL)
    """)

    query_second = text("""
        UPDATE alerts SET sent_at = LOCALTIMESTAMP WHERE id = :id
    """)

    while True:
        with engine.connect() as connection:
            res = connection.execute(query_first)
            if (res.rowcount == 0):
                logger.info("telegram alerts: all processed")
            else:
                res_str = res.fetchall()

                for i in range(len(res_str)):
                    title = f"{res_str[i][0]} message"
                    message = f"{res_str[i][1]}"
                    severity = f"{res_str[i][0]}"

                    alert = Alert(title, message, severity)
                    flag = asyncio.run(send_telegram_alert(BOT_TOKEN, CHAT_ID, alert))

                    if flag:
                        connection.execute(query_second, {'id': res_str[i][2]})
                        connection.commit()

            time.sleep(INTERVAL_SEC)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        stream=sys.stdout,
    )

    get_rows_without_alert()
