from email import message
import logging
from collections import defaultdict
import trace
from extensions import db
from flask import Blueprint, jsonify
from flask import request
from models import DeviceEventLogthousand
from models import DeviceEventLog
from datetime import datetime, timedelta
from sqlalchemy import func
import traceback
from models import CompressedDeviceEventLog
from models import DeviceEventLogfifty
import pprint
import json
import math
from operator import attrgetter
from models import  CompressedDeviceEventLog2


# ✅ Configure logging for this module
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,  # or logging.DEBUG for more detail
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# ✅ Create a Blueprint instance for modular routing
main = Blueprint("main", __name__)


@main.route("/copy-first-1000", methods=["GET"])
def demo_insert():
    try:

        per_page = 1000

        rows = (
            db.session.query(DeviceEventLog)
            .order_by(DeviceEventLog.ts)
            .limit(per_page)
            .all()
        )

        if not rows:
            return (
                jsonify({"error": "No data found.", "message": "No data found."}),
                400,
            )

        print("insert started")
        for row in rows:
            demo_row = DeviceEventLogthousand(
                entity_id=row.entity_id,
                key=row.key,
                ts=row.ts,
                bool=row.bool,
                str_v=row.str_v,
                long_v=row.long_v,
                dbl_v=row.dbl_v,
                json_v=row.json_v,
            )

            db.session.add(demo_row)

            db.session.commit()

        print("insert finished")

        return (
            jsonify(
                {
                    "status": "success",
                }
            ),
            200,
        )

    except Exception as e:
        # Log error (you can also use logging here)
        print(f"❌ Error occurred while fetching data: {str(e)}")

        logging.error("Error occurred while fetching data.", exc_info=True)

        # Return proper error response
        return (
            jsonify(
                {
                    "error": "Something went wrong while fetching data.",
                    "details": str(e),
                }
            ),
            500,
        )




@main.route("/compress-database", methods=["GET"])
def compress_data_by_period():   
    try:

        hourly_bucket = []

        max_time = db.session.query(func.max(DeviceEventLog.ts)).scalar()

        # print("max_time in unix", max_time)

        min_time = db.session.query(func.min(DeviceEventLog.ts)).scalar()

        # print("min_time in unix", min_time)

        max_time = datetime.fromtimestamp(max_time / 1000.0)

        min_time = datetime.fromtimestamp(min_time / 1000.0)

        # print("max_time", max_time)

        # print("min_time", min_time)

        # this is the floor of min time that means if time is 5:30:05
        # then it will be 5:00:00
        min_dt_floor = min_time.replace(minute=0, second=0, microsecond=0)

        # this is the ceil of max time that means if time is 5:30:05
        # then it will be 6:00:00 why we are checking if is becasue if it is 5:30:05
        # then it will be 6:00:00
        # otherwise if min sec and minisec is 0 then it will be 5:00:00 let it be as it is
        if max_time.minute > 0 or max_time.second > 0 or max_time.microsecond > 0:
            max_dt_ceil = (max_time + timedelta(hours=1)).replace(
                minute=0, second=0, microsecond=0
            )

        else:
            max_dt_ceil = max_time.replace(minute=0, second=0, microsecond=0)

        """
            logging.info(f"min datetime after floor {min_dt_floor}")

            logging.info(f"max datetime after ceil {max_dt_ceil}")
            
            """

        current = min_dt_floor

        # this while loop is generating filling hourly bucket list
        while current < max_dt_ceil:
            # logging.info(f"current datetime {current}")
            bucket_start = current
            bucket_end = current + timedelta(hours=1)
            hourly_bucket.append((bucket_start, bucket_end))
            # logging.info(f"hourly bucket {hourly_bucket}")
            current = bucket_end

        # logging.info(f"size of hourly bucket {len(hourly_bucket)}")
        
        
        

        for start_dt, end_dt in hourly_bucket:

            # logging.info(f"bucket start {bucket_start}")

            # logging.info(f"bucket end {bucket_end}")

            start_dt_unix = int(start_dt.timestamp() * 1000)

            end_dt_unix = int(end_dt.timestamp() * 1000)

            #logging.info(f"start ts {start_dt_unix}")

            #logging.info(f"end ts {end_dt_unix}")

            rows = (
                db.session.query(DeviceEventLog)
                .filter(
                    DeviceEventLog.ts >= start_dt_unix,
                    DeviceEventLog.ts < end_dt_unix,
                )
                .order_by(
                    DeviceEventLog.entity_id.asc(),
                    DeviceEventLog.key.asc(),
                    DeviceEventLog.ts.asc(),
                )
                .all()
            )
            """
            for row in rows:
                logging.info(f"printing the device event log for {start_dt} and {end_dt} is --------{row}")
                """

            #this is used to sort the rows based on entity_id , key ,and ts
            rows.sort(key=attrgetter("entity_id", "key", "ts"))

            # grouped = {
            #   ('device_1', "key_1","5min_start_ts"): [row1, row2, ...],
            #   ('device_2', "key_2","5min_start_ts"): [row3, row4, ...],
            # }

            bucketed_5min = defaultdict(list)

            bucketed_duration_ms = 5 * 60 * 1000  #5 min in milliseconds

            for row in rows:
                bucket_start_ts = (row.ts // bucketed_duration_ms) * bucketed_duration_ms

                #logging.info(f"bucket start ts {bucket_start_ts}")


                bucketed_5min[(row.entity_id,row.key,bucket_start_ts)].append(row)



            for (entity_id,key,bucket_start_ts), rows in bucketed_5min.items():


                long_values = []
                dbl_values = []


                # logging.info(f"entity_id {entity_id} key {key} bucket_start_ts {bucket_start_ts} count of rows {len(rows)}")

                for row in rows:
                    if row.long_v is not None:
                        long_values.append(row.long_v)
                    if row.dbl_v is not None:
                        dbl_values.append(row.dbl_v)


                #logging.info(f"bucket start in human readable format {datetime.fromtimestamp(bucket_start_ts / 1000.0)}")

                if len(long_values) > 0:
                    #logging.info(f"long values count {len(long_values)}")  
                    avg_long = sum(long_values) / len(long_values)
                    #logging.info(f"avg long value {avg_long}")
                    compressedDeviceEventLog = CompressedDeviceEventLog2(
                        entity_id=entity_id,
                        key = key,
                        ts = bucket_start_ts,
                        long_v = avg_long,
                    )

                    db.session.add(compressedDeviceEventLog)

                if len(dbl_values) > 0:
                    #logging.info(f"dbl values count {len(dbl_values)}")  
                    avg_dbl = sum(dbl_values) / len(dbl_values)
                    #logging.info(f"avg dbl value {avg_dbl}")

                    compressedDeviceEventLog = CompressedDeviceEventLog2(
                        entity_id=entity_id,
                        key = key,
                        ts = bucket_start_ts,
                        dbl_v = avg_dbl,
                    )

                    db.session.add(compressedDeviceEventLog)

                #dealing with non numeric values
                for row in rows:
                    if row.long_v is None and row.dbl_v is None:
                        compressed_row = CompressedDeviceEventLog2(
                                entity_id=entity_id,
                                key=key,
                                ts=bucket_start_ts,
                                bool_v=row.bool_v,
                                str_v=row.str_v,
                                json_v=row.json_v,
                                long_v = None,
                                dbl_v = None
                            )
                        db.session.add(compressed_row)


            db.session.commit()

            logging.info(f"hourly bucket {hourly_bucket}")

            logging.info(f"commiting data for {start_dt} to {end_dt}")

        
        
        
        
        
        
                    
                    
                
                 
         
                
                    

                


           



        
        
        
        return (
            jsonify(
                {
                    "message": "success",
                }
            ),
            200,
        )

    except Exception as e:
        # Log error (you can also use logging here)
        logging.error(f"❌ Error occurred while fetching data: {str(e)}")

        # Return proper error response
        return (
            jsonify(
                {
                    "error": "Something went wrong while fetching data.",
                    "details": str(e),
                }
            ),
            500,
        )





@main.route("/compress_database_from_DeviceEventLogfifty2", methods=["GET"])
def compress_data_by_period2():
    try:

        hourly_bucket = []

        max_time = db.session.query(func.max(DeviceEventLogfifty.ts)).scalar()

        # print("max_time in unix", max_time)

        min_time = db.session.query(func.min(DeviceEventLogfifty.ts)).scalar()

        # print("min_time in unix", min_time)

        max_time = datetime.fromtimestamp(max_time / 1000.0)

        min_time = datetime.fromtimestamp(min_time / 1000.0)

        # print("max_time", max_time)

        # print("min_time", min_time)

        # this is the floor of min time that means if time is 5:30:05
        # then it will be 5:00:00
        min_dt_floor = min_time.replace(minute=0, second=0, microsecond=0)

        # this is the ceil of max time that means if time is 5:30:05
        # then it will be 6:00:00 why we are checking if is becasue if it is 5:30:05
        # then it will be 6:00:00
        # otherwise if min sec and minisec is 0 then it will be 5:00:00 let it be as it is
        if max_time.minute > 0 or max_time.second > 0 or max_time.microsecond > 0:
            max_dt_ceil = (max_time + timedelta(hours=1)).replace(
                minute=0, second=0, microsecond=0
            )

        else:
            max_dt_ceil = max_time.replace(minute=0, second=0, microsecond=0)

        """
            logging.info(f"min datetime after floor {min_dt_floor}")

            logging.info(f"max datetime after ceil {max_dt_ceil}")

            """

        current = min_dt_floor

        # this while loop is generating filling hourly bucket list
        while current < max_dt_ceil:
            # logging.info(f"current datetime {current}")
            bucket_start = current
            bucket_end = current + timedelta(hours=1)
            hourly_bucket.append((bucket_start, bucket_end))
            # logging.info(f"hourly bucket {hourly_bucket}")
            current = bucket_end

        # logging.info(f"size of hourly bucket {len(hourly_bucket)}")

        for start_dt, end_dt in hourly_bucket:

            # logging.info(f"bucket start {bucket_start}")

            # logging.info(f"bucket end {bucket_end}")

            start_dt_unix = int(start_dt.timestamp() * 1000)

            end_dt_unix = int(end_dt.timestamp() * 1000)

            # logging.info(f"start ts {start_dt_unix}")

            # logging.info(f"end ts {end_dt_unix}")

            rows = (
                db.session.query(DeviceEventLogfifty)
                .filter(
                    DeviceEventLogfifty.ts >= start_dt_unix,
                    DeviceEventLogfifty.ts < end_dt_unix,
                )
                .order_by(
                    DeviceEventLogfifty.entity_id.asc(),
                    DeviceEventLogfifty.key.asc(),
                    DeviceEventLogfifty.ts.asc(),
                )
                .all()
            )
            """
            for row in rows:
                logging.info(f"printing the device event log for {start_dt} and {end_dt} is --------{row}")
                """

            # this is used to sort the rows based on entity_id , key ,and ts
            rows.sort(key=attrgetter("entity_id", "key", "ts"))

            # grouped = {
            #   ('device_1', "key_1","5min_start_ts"): [row1, row2, ...],
            #   ('device_2', "key_2","5min_start_ts"): [row3, row4, ...],
            # }

            bucketed_5min = defaultdict(list)

            bucketed_duration_ms = 5 * 60 * 1000  # 5 min in milliseconds

            for row in rows:
                bucket_start_ts = (row.ts // bucketed_duration_ms) * bucketed_duration_ms

                # logging.info(f"bucket start ts {bucket_start_ts}")

                bucketed_5min[(row.entity_id, row.key, bucket_start_ts)].append(row)

            for (entity_id, key, bucket_start_ts), rows in bucketed_5min.items():

                long_values = []
                dbl_values = []

                # logging.info(f"entity_id {entity_id} key {key} bucket_start_ts {bucket_start_ts} count of rows {len(rows)}")

                for row in rows:
                    if row.long_v is not None:
                        long_values.append(row.long_v)
                    if row.dbl_v is not None:
                        dbl_values.append(row.dbl_v)

                # logging.info(f"bucket start in human readable format {datetime.fromtimestamp(bucket_start_ts / 1000.0)}")

                if len(long_values) > 0:
                    # logging.info(f"long values count {len(long_values)}")  
                    avg_long = sum(long_values) / len(long_values)
                    # logging.info(f"avg long value {avg_long}")
                    compressedDeviceEventLog = CompressedDeviceEventLog2(
                        entity_id=entity_id,
                        key=key,
                        ts=bucket_start_ts,
                        long_v=avg_long,

                    )

                    db.session.add(compressedDeviceEventLog)

                if len(dbl_values) > 0:
                    # logging.info(f"dbl values count {len(dbl_values)}")  
                    avg_dbl = sum(dbl_values) / len(dbl_values)
                    # logging.info(f"avg dbl value {avg_dbl}")

                    compressedDeviceEventLog = CompressedDeviceEventLog2(
                        entity_id=entity_id,
                        key=key,
                        ts=bucket_start_ts,
                        dbl_v=avg_dbl,
                    )

                    db.session.add(compressedDeviceEventLog)

                # dealing with non numeric values
                for row in rows:
                    if row.long_v is None and row.dbl_v is None:
                        compressed_row = CompressedDeviceEventLog2(
                            entity_id=entity_id,
                            key=key,
                            ts=bucket_start_ts,
                            bool_v=row.bool_v,
                            str_v=row.str_v,
                            json_v=row.json_v,
                            long_v=None,
                            dbl_v=None
                        )
                        db.session.add(compressed_row)

            db.session.commit()

            logging.info(f"hourly bucket {hourly_bucket}")

            logging.info(f"commiting data for {start_dt} to {end_dt}")

        return (
            jsonify(
                {
                    "message": "success",
                }
            ),
            200,
        )

    except Exception as e:
        # Log error (you can also use logging here)
        logging.error(f"❌ Error occurred while fetching data: {str(e)}")

        # Return proper error response
        return (
            jsonify(
                {
                    "error": "Something went wrong while fetching data.",
                    "details": str(e),
                }
            ),
            500,
        )


@main.route("/compress_database_from_DeviceEventLogfifty", methods=["GET"])
def compress_data_by_period_for_fifty():
    try:

        hourly_bucket = []

        max_time = db.session.query(func.max(DeviceEventLogfifty.ts)).scalar()

        # print("max_time in unix", max_time)

        min_time = db.session.query(func.min(DeviceEventLogfifty.ts)).scalar()

        # print("min_time in unix", min_time)

        max_time = datetime.fromtimestamp(max_time / 1000.0)

        min_time = datetime.fromtimestamp(min_time / 1000.0)

        # print("max_time", max_time)

        # print("min_time", min_time)

        # this is the floor of min time that means if time is 5:30:05
        # then it will be 5:00:00
        min_dt_floor = min_time.replace(minute=0, second=0, microsecond=0)

        # this is the ceil of max time that means if time is 5:30:05
        # then it will be 6:00:00 why we are checking if is becasue if it is 5:30:05
        # then it will be 6:00:00
        # otherwise if min sec and minisec is 0 then it will be 5:00:00 let it be as it is
        if max_time.minute > 0 or max_time.second > 0 or max_time.microsecond > 0:
            max_dt_ceil = (max_time + timedelta(hours=1)).replace(
                minute=0, second=0, microsecond=0
            )

        else:
            max_dt_ceil = max_time.replace(minute=0, second=0, microsecond=0)

        """
            logging.info(f"min datetime after floor {min_dt_floor}")

            logging.info(f"max datetime after ceil {max_dt_ceil}")

            """

        current = min_dt_floor

        # this while loop is generating filling hourly bucket list
        while current < max_dt_ceil:
            # logging.info(f"current datetime {current}")
            bucket_start = current
            bucket_end = current + timedelta(hours=1)
            hourly_bucket.append((bucket_start, bucket_end))
            # logging.info(f"hourly bucket {hourly_bucket}")
            current = bucket_end

        # logging.info(f"size of hourly bucket {len(hourly_bucket)}")

        for start_dt, end_dt in hourly_bucket:

            # logging.info(f"bucket start {bucket_start}")

            # logging.info(f"bucket end {bucket_end}")

            start_dt_unix = int(start_dt.timestamp() * 1000)

            end_dt_unix = int(end_dt.timestamp() * 1000)

            # logging.info(f"start ts {start_dt_unix}")

            # logging.info(f"end ts {end_dt_unix}")

            rows = (
                db.session.query(DeviceEventLogfifty)
                .filter(
                    DeviceEventLogfifty.ts >= start_dt_unix,
                    DeviceEventLogfifty.ts < end_dt_unix,
                )
                .order_by(
                    DeviceEventLogfifty.entity_id.asc(),
                    DeviceEventLogfifty.key.asc(),
                    DeviceEventLogfifty.ts.asc(),
                )
                .all()
            )
            """
            for row in rows:
                logging.info(f"printing the device event log for {start_dt} and {end_dt} is --------{row}")
                """

            # this is used to sort the rows based on entity_id , key ,and ts
            rows.sort(key=attrgetter("entity_id", "key", "ts"))

            # grouped = {
            #   ('device_1', "key_1","5min_start_ts"): [row1, row2, ...],
            #   ('device_2', "key_2","5min_start_ts"): [row3, row4, ...],
            # }

            bucketed_5min = defaultdict(list)

            bucketed_duration_ms = 5 * 60 * 1000  # 5 min in milliseconds

            for row in rows:
                bucket_start_ts = (row.ts // bucketed_duration_ms) * bucketed_duration_ms

                # logging.info(f"bucket start ts {bucket_start_ts}")

                bucketed_5min[(row.entity_id, row.key, bucket_start_ts)].append(row)

            for (entity_id, key, bucket_start_ts), rows in bucketed_5min.items():

                long_values = []
                dbl_values = []

                # logging.info(f"entity_id {entity_id} key {key} bucket_start_ts {bucket_start_ts} count of rows {len(rows)}")

                for row in rows:
                    if row.long_v is not None:
                        long_values.append(row.long_v)
                    if row.dbl_v is not None:
                        dbl_values.append(row.dbl_v)

                # logging.info(f"bucket start in human readable format {datetime.fromtimestamp(bucket_start_ts / 1000.0)}")

                if len(long_values) > 0:
                    # logging.info(f"long values count {len(long_values)}")  
                    avg_long = sum(long_values) / len(long_values)
                    # logging.info(f"avg long value {avg_long}")
                    compressedDeviceEventLog = CompressedDeviceEventLog(
                        entity_id=entity_id,
                        key=key,
                        ts=bucket_start_ts,
                        long_v=avg_long,

                    )

                    db.session.add(compressedDeviceEventLog)

                if len(dbl_values) > 0:
                    # logging.info(f"dbl values count {len(dbl_values)}")  
                    avg_dbl = sum(dbl_values) / len(dbl_values)
                    # logging.info(f"avg dbl value {avg_dbl}")

                    compressedDeviceEventLog = CompressedDeviceEventLog(
                        entity_id=entity_id,
                        key=key,
                        ts=bucket_start_ts,
                        dbl_v=avg_dbl,
                    )

                    db.session.add(compressedDeviceEventLog)

                # dealing with non numeric values
                for row in rows:
                    if row.long_v is None and row.dbl_v is None:
                        compressed_row = CompressedDeviceEventLog(
                            entity_id=entity_id,
                            key=key,
                            ts=bucket_start_ts,
                            bool_v=row.bool_v,
                            str_v=row.str_v,
                            json_v=row.json_v,
                            long_v=None,
                            dbl_v=None
                        )
                        db.session.add(compressed_row)

            db.session.commit()

            logging.info(f"hourly bucket {hourly_bucket}")

            logging.info(f"commiting data for {start_dt} to {end_dt}")

        return (
            jsonify(
                {
                    "message": "success",
                }
            ),
            200,
        )

    except Exception as e:
        # Log error (you can also use logging here)
        logging.error(f"❌ Error occurred while fetching data: {str(e)}")

        # Return proper error response
        return (
            jsonify(
                {
                    "error": "Something went wrong while fetching data.",
                    "details": str(e),
                }
            ),
            500,
        )


# ============================== #
# 🚀 Route: Add new data to DB   #
# ============================== #
@main.route("/add")
def add_data():
    # Create a new row using SQLAlchemy model
    new_data = DeviceEventLogDemo(
        entity_id=11111111111, key=111111, ts=1690868072447, bool=False
    )

    # Add and commit to DB
    db.session.add(new_data)

    db.session.commit()

    return jsonify({"message": "Sample data added "})


# ================================= #
# 📦 Route: Fetch all rows from DB  #
# ================================= #
@main.route("/getall")
def getall():
    try:

        logging.info("Fetching all rows from DeviceEventLogDemo table...")

        # Fetch rows with a limit to avoid memory overload
        All_DeviceEventLogDemo_rows = (
            db.session.query(DeviceEventLogDemo).limit(15735).all()
        )

        logging.info(f"length of the list is {len(All_DeviceEventLogDemo_rows)}")

        result_list = []

        # Convert each SQLAlchemy object to a dictionary
        for row in All_DeviceEventLogDemo_rows:
            result_list.append(row.to_dict())

        logging.info(f"Successfully fetched {len(result_list)} rows.")

        # Return JSON response
        return jsonify(result_list), 200

    except Exception as e:
        # Log error (you can also use logging here)
        print(f"❌ Error occurred while fetching data: {str(e)}")

        logging.error("Error occurred while fetching data.", exc_info=True)

        # Return proper error response
        return (
            jsonify(
                {
                    "error": "Something went wrong while fetching data.",
                    "details": str(e),
                }
            ),
            500,
        )


# ======================================= #
# ✏️ Route: Update a row by ID in DB  #
# ======================================= #
@main.route("/update/<int:id>", methods=["PUT"])
def update_by_id(id):
    try:
        logging.info(f"Updating row with id={id}")
        data = request.json

        # Find the row to update
        row = db.session.query(DeviceEventLogDemo).get(id)
        if row is None:
            return jsonify({"error": "Record not found"}), 404

        # Update the row with the new data
        for key, value in data.items():
            if hasattr(row, key):
                setattr(row, key, value)

        db.session.commit()
        logging.info(f"Successfully updated row with id={id}")
        return jsonify(row.to_dict()), 200

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating row with id={id}: {str(e)}", exc_info=True)
        return (
            jsonify(
                {"error": "Something went wrong while updating data", "details": str(e)}
            ),
            500,
        )


# ======================================= #
# 🔍 Route: Fetch a single row by ID from DB  #
# ======================================= #
@main.route("/get/<int:id>", methods=["GET"])
def get_by_id(id):
    try:
        logging.info(f"Fetching row with id={id} from DeviceEventLogDemo table...")

        # Query the database for the row with the given id
        row = db.session.query(DeviceEventLogDemo).get(id)

        if row is None:
            logging.warning(f"No row found with id={id}")
            return jsonify({"error": "Record not found"}), 404

        # Convert the row to a dictionary
        result = row.to_dict()
        logging.info(f"Successfully fetched row with id={id}")

        return jsonify(result), 200

    except Exception as e:
        logging.error(f"Error occurred while fetching data for id={id}", exc_info=True)
        return (
            jsonify(
                {"error": "Something went wrong while fetching data", "details": str(e)}
            ),
            500,
        )


# ======================================= #
# 🗑️ Route: Delete a row by ID from DB  #
# ======================================= #
@main.route("/delete/<int:id>", methods=["DELETE"])
def delete_by_id(id):
    try:
        logging.info(f"Deleting row with id={id}")

        row = db.session.query(DeviceEventLogDemo).get(id)
        if row is None:
            return jsonify({"error": "Record not found"}), 404

        db.session.delete(row)
        db.session.commit()
        logging.info(f"Successfully deleted row with id={id}")
        return jsonify({"message": "Record deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting row with id={id}: {str(e)}", exc_info=True)
        return (
            jsonify(
                {"error": "Something went wrong while deleting data", "details": str(e)}
            ),
            500,
        )


# ============================ #
# ⚙️ Route: Test if API is up   #
# ============================ #
@main.route("/")
def testapi():
    return jsonify({"message": "working properly"})
