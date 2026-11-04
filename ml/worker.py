import logging
import os
import sys
import time

import numpy as np
import pandas as pd
import xgboost as xgb
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

logger = logging.getLogger("worker")

load_dotenv()

warning_rul = int(os.getenv("RUL_WARNING"))
critical_rul = int(os.getenv("RUL_CRITICAL"))

engine = create_engine(os.getenv("DATABASE_URL"))

def get_model() -> xgb.XGBRegressor:
    model = xgb.XGBRegressor()
    model.load_model(os.getenv("MODEL_PATH"))

    return model

def get_data_from_simulator() -> tuple[pd.DataFrame, pd.DataFrame] | tuple[None, None]:
    with engine.connect() as connection:
        query = text("""
                    SELECT sensor_readings.*
                    FROM sensor_readings
                    LEFT JOIN ml_predictions
                    ON sensor_readings.equipment_id = ml_predictions.equipment_id
                    AND sensor_readings.cycle = ml_predictions.cycle
                    WHERE ml_predictions.id IS NULL
                    """)
        result = connection.execute(query)

        if (result.rowcount == 0):
            return None, None

        df = pd.DataFrame(result)
        df_for_pred = df.drop(columns=['id', 'equipment_id', 'cycle', 'rul', 'created_at'])
        df_for_pred['s17'] = df_for_pred['s17'].astype(int)

    return df_for_pred, df

def model_predict(df: pd.DataFrame, model: xgb.XGBRegressor) -> np.ndarray:
    arr = model.predict(df)

    return arr

def write_to_tables():
    model = get_model()

    last_id = 0

    query_second = text("""
                    INSERT INTO ml_predictions (equipment_id, cycle, predicted_rul, defect_probability, residual, model_version)
                    VALUES (:eq_id, :cycle, :rul, 0, 0, :model)
                    ON CONFLICT DO NOTHING
                    """)

    try:
        while True:
            df_pred, df = get_data_from_simulator()

            if df_pred is None or df is None:
                logger.info("ml_predictions: all processed")
                time.sleep(int(os.getenv("WORKER_POLL_INTERVAL")))
            else:
                t0 = time.perf_counter()
                arr = model_predict(df_pred, model)
                with engine.connect() as connection:

                    for i in range (arr.size):
                        df_row = df.iloc[i]
                        connection.execute(query_second, {'eq_id': df_row['equipment_id'], 'cycle': df_row['cycle'], 'rul':arr[i], 'model': 'first_xgboost_model'})

                    connection.commit()

                elapsed_ms = (time.perf_counter() - t0) * 1000
                logger.info("inserted %d rows in %.2f ms", arr.size, elapsed_ms)

            flag, last_id = write_to_alerts_table(last_id)

            if flag:
                logger.info("alerts: all processed")

    except KeyboardInterrupt:
        logger.warning("interrupted by user")

def write_to_alerts_table(last_id):
    query_third = text("""
                      SELECT ml_predictions.id, ml_predictions.equipment_id, ml_predictions.cycle, ml_predictions.predicted_rul FROM ml_predictions
                      WHERE (ml_predictions.predicted_rul <= :warning_rul AND ml_predictions.id > :last_id)
                      """)

    query_fourth = text("""
                    SELECT equipment.name FROM equipment WHERE (id = :eq_id)
                    """)


    query_fifth = text("""
                    INSERT INTO alerts (equipment_id, ml_prediction_id, cycle, severity, message)
                    VALUES (:equipment_id, :ml_prediction_id, :cycle, :severity, :message)
                    ON CONFLICT DO NOTHING
                    """)

    query_sixth = text("""
                    SELECT equipment_id, severity FROM alerts WHERE (severity = :severity AND equipment_id = :eq_id)
                    """)

    with engine.connect() as connection:
        res = connection.execute(query_third, {'warning_rul': warning_rul, 'last_id': last_id})

        if (res.rowcount == 0):
            return True, last_id

        data_ml_pred = res.fetchall()

        t0 = time.perf_counter()
        counter = 0

        for i in range (len(data_ml_pred)):
            last_id = max(last_id, data_ml_pred[i][0])

            eq_name = connection.execute(query_fourth, {'eq_id':data_ml_pred[i][1]})

            if (eq_name.rowcount == 0):
                continue

            eq_name = eq_name.fetchall()

            if data_ml_pred[i][3] > critical_rul:
                severity = "warning"

                find_sev_in_alerts = connection.execute(query_sixth, {'severity':severity, 'eq_id': data_ml_pred[i][1]})

                if find_sev_in_alerts.rowcount == 0:
                    message = f"warning alert on equipment name {eq_name[0][0]}"

                    connection.execute(query_fifth, {'equipment_id': data_ml_pred[i][1], 'ml_prediction_id': data_ml_pred[i][0], 'cycle': data_ml_pred[i][2], 'severity': severity, 'message': message})
                    connection.commit()
                    counter += 1

                else: pass

            else:
                severity = "critical"

                find_sev_in_alerts = connection.execute(query_sixth, {'severity':severity, 'eq_id': data_ml_pred[i][1]})

                if find_sev_in_alerts.rowcount == 0:
                    message = f"critical alert on equipment name {eq_name[0][0]}"

                    connection.execute(query_fifth, {'equipment_id': data_ml_pred[i][1], 'ml_prediction_id': data_ml_pred[i][0], 'cycle': data_ml_pred[i][2], 'severity': severity, 'message': message})
                    connection.commit()
                    counter += 1

                else: pass

        elapsed_ms = (time.perf_counter() - t0) * 1000
        logger.info("inserted %d rows in alerts in %.2f ms", counter, elapsed_ms)

        return False, last_id

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        stream=sys.stdout,
    )
    write_to_tables()


