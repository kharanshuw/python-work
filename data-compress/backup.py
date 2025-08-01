"""
✅ What the code actually does:
1. Chunked Fetch (Pagination)
It fetches 100,000 rows at a time from the DeviceEventLogDemo2 table using pagination to avoid memory overload.

2. 5-Minute Bucket Calculation
For each row, it calculates a bucket_start time using this logic:


bucket_start = dt.replace(second=0, microsecond=0, minute=(dt.minute // 5) * 5)
So:

A timestamp like 12:03 becomes 12:00

A timestamp like 14:29 becomes 14:25

This effectively groups rows into 5-minute windows.

3. Group Hierarchy
It groups the data in this order:


key → entity_id → bucket_start (5-minute bucket)
That means:

All rows with the same key, entity_id, and within the same 5-minute window are grouped together.

4. Numeric Aggregation
Inside each 5-minute bucket:

It looks for numeric values only (long_v or dbl_v)

If found:

Computes the average

Takes the latest timestamp (max(ts)) in the group

Adds one summarized row to the result (compressed row)

5. Raw Value Handling
If no numeric values exist in the bucket:

That means the data is of type bool, str, or json

These rows are preserved as-is, i.e., they are added without aggregation

6. Merging Concept

In this code, it's just creating a compressed result set in memory — not actually writing back to the database yet.

But logically, yes — multiple rows in the same 5-min bucket are reduced to one aggregated row (if numeric).

Non-numeric rows are retained individually.
"""

@main.route("/compress_table", methods=["GET"])
def group_by_dates():
    try:
        page = 1
        per_page = 10000
        compressed_data = []

        while True:

            # rows = db.session.query(DeviceEventLogDemo) \
            #     .order_by(DeviceEventLogDemo.ts) \
            #     .limit(per_page) \
            #     .offset((page - 1) * per_page) \
            #     .all()

            rows = (
                db.session.query(DeviceEventLogDemo)
                .order_by(DeviceEventLogDemo.ts)
                .limit(per_page)
                .all()
            )

            """
            What it does:
            If the database gives back no more rows, stop the while loop.

            Why it's needed:
            To avoid infinite looping once data ends.
            """
            if not rows:
                break

            """
            			This creates a 3-level nested dictionary, structured like:

            			css
            			Copy
            			Edit
            			bucketed_data[key][entity_id][bucket_start] → list of rows
            			So:

            			The first level is grouped by key

            			The second level is grouped by entity_id

            			The third level is grouped by bucket_start (5-minute time bucket)

            			The value stored at the end of this chain is a list (of rows)

            			💡 Example in action
            			After running:
            			bucketed_data[101][5012]['2025-07-12T10:00:00'].append(row)

            			The structure becomes:


            			{
            			  key-101: {
            				entity-5012: {
            				 5min-bucket-start '2025-07-12T10:00:00': [row, row, ...]
            				}
            			  }
            			}
            		"""
            # Step 2: Group by key → entity_id → 5-minute bucket
            bucketed_data = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

            """
            		🔍 What it's doing:
            		It iterates over each row in the rows list.

            		For each row, it checks if the ts (timestamp) field is missing, null, or falsy.

            		If ts is missing or invalid (like None or 0), it skips that row using continue.
            """
            for row in rows:
                if not row.ts:
                    continue

                """
                🕒 Converts the timestamp ts from milliseconds to a datetime object.
                fromtimestamp() expects seconds, so we divide by 1000.0.

                Example:
                If row.ts = 1690868072447 →
                datetime.fromtimestamp(1690868072.447) = 2023-07-31 12:14:32
                """

                dt = datetime.fromtimestamp(row.ts / 1000.0)

                """
                🧠 This line calculates the start of a 5-minute time bucket.
                🪣 How it works:
                dt.minute // 5 → floors the minute to the nearest 5-minute group.
                e.g. 12:14 → bucket = 12:10              
                e.g. 12:08 → bucket = 12:05
                .replace() resets:                
                seconds = 0
                microseconds = 0                
                minutes = floored 5-min mark               
                So 12:14:32 becomes 12:10:00.              
                The replace() method in Python's datetime module is used to create a new datetime object with specific fields replaced by new values. 
                It does not modify the original datetime object, but rather returns a new one with the changes.
                """

                bucket_start = dt.replace(
                    second=0, microsecond=0, minute=(dt.minute // 5) * 5
                )

                """
                📦 This is the core grouping logic:
                You're creating a nested dictionary structure:
                bucketed_data[key][entity_id][bucket_start] = list of rows
                It groups the rows first by:
                key → top-level
                then entity_id
                then 5-minute bucket_start
                Each bucket stores a list of rows that belong to that 5-minute time window.
                """
                bucketed_data[row.key][row.entity_id][bucket_start].append(row)

            # Step 3: Process each bucket
            """
            🔹 Loops through each `key` in the `bucketed_data` dictionary.
            Think of `key` as the top-most category (e.g. sensor type, metric type, etc.).
            """
            
            
            for key, entity_group in bucketed_data.items():
                
                
                # logging.info(f"printing key {key}")
                """
                🔹 For each `key`, loop through each `entity_id`.
                Each entity might be a device or unique source of data.
                """
                for entity_id, buckets in entity_group.items():

                    # logging.info(f"printing entity_id {entity_id}")

                    """
                    🔹 For each `entity_id`, loop through its 5-minute time buckets.
                    Each bucket contains all the rows that fall in that 5-minute window.
                    """
                    for bucket_start, bucket_rows in buckets.items():

                        """

                        ### 🎯 Now you have:

                        * `key`
                        * `entity_id`
                        * `bucket_start` (5-minute bucket)
                        * `bucket_rows`: List of rows that belong to this group

                        """

                        # logging.info(f"printing bucket_start {bucket_start}")

                        """
                        🔍 This extracts only the numeric values (`long_v` or `dbl_v`) from each row in the current bucket.
                        * If `long_v` is available, it's used (converted to float).
                        * If not, it uses `dbl_v`.
                        """
                        numeric_vals = []

                        for r in bucket_rows:
                            if r.long_v is not None:
                                numeric_vals.append(float(r.long_v))
                            elif r.dbl_v is not None:
                                numeric_vals.append(r.dbl_v)

                        """
                        🔸 If we have numeric values (i.e., some rows in the bucket had long_v or dbl_v):
                        """
                        if numeric_vals:

                            """
                            📊 Calculate the **average** of all those numeric values.
                            """
                            avg_val = sum(numeric_vals) / len(numeric_vals)

                            """
                            ⏱️ Find the **latest timestamp** among all rows in the bucket.
                            This will act as a representative timestamp for the aggregated row.
                            """
                            representative_ts = max(r.ts for r in bucket_rows)

                            """
                            ✅ Append a new "compressed" row with:

                            * The `key`, `entity_id`, and bucket
                            * The **average** value
                            * The latest `ts`
                            * Other values set to `None` (because we only care about numeric values here)
                            * A `"type"` field to say this row was `aggregated`
                            """
                            compressed_data.append(
                                {
                                    "key": key,
                                    "entity_id": entity_id,
                                    "bucket_start": bucket_start.isoformat(),
                                    "ts": representative_ts,
                                    "avg_val": avg_val,
                                    "bool_v": None,
                                    "str_v": None,
                                    "json_v": None,
                                    "type": "aggregated",
                                }
                            )
                        else:

                            """
                            🚫 If there were **no numeric values** (`long_v` and `dbl_v` are missing):
                            * These rows likely have `bool`, `str`, or `json` values.
                            * So we keep them **as-is**, just preserving their original structure.
                            * Each of these rows is added individually to `compressed_data` with `"type": "raw"`.
                            """
                            for r in bucket_rows:
                                compressed_data.append(
                                    {
                                        "key": key,
                                        "entity_id": entity_id,
                                        "bucket_start": bucket_start.isoformat(),
                                        "ts": r.ts,
                                        "avg_val": None,
                                        "bool": r.bool,
                                        "str_v": r.str_v,
                                        "json_v": r.json_v,
                                        "type": "raw",
                                    }
                                )

    except Exception as e:
        logging.error(e)
        return jsonify({"error": "Compression failed.", "details": str(e)}), 500


# logic and code for deviding the max and min time into ours buckets
from datetime import datetime, timedelta

# Example timestamps (replace with your actual values)
start_ts = datetime(2023, 8, 1, 0, 0, 0)  # 1st August 2023, 00:00:00
end_ts = datetime(2023, 8, 1, 5, 0, 0)  # 1st August 2023, 05:00:00

# Generate list of 1-hour intervals
hourly_slots = []
current = start_ts

while current < end_ts:
    next_hour = current + timedelta(hours=1)
    hourly_slots.append((current, next_hour))
    current = next_hour

# Print the slots
for start, end in hourly_slots:
    print(f"From {start} to {end}")








# def compressdatabase():
#     try:

#         page = 1
#         per_page = 1000
#         compressed_data = []
#         bucketed_data = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

#         while True:

#             rows = (
#                 db.session.query(DeviceEventLogDemo)
#                 .order_by(DeviceEventLogDemo.entity_id,DeviceEventLogDemo.key,DeviceEventLogDemo.ts)
#                 .limit(per_page)
#                 .offset((page - 1) * per_page)
#                 .all()
#             )

#             if not rows:
#                 break


#             for row in rows:


#                 """
#                 print(row)
#                 """

#                 # converting timestamp from unix system(millisecond) to readable format
#                 dt = datetime.fromtimestamp(row.ts / 1000.0)

#                 # print("printing datetime in readable format {dt}")

#                 """
#                 This line of code is modifying a datetime object dt to create a new datetime object timeline_start.

#                 Here's what it's doing:

#                 dt.replace(second=0, microsecond=0): This part is setting the seconds and microseconds of the datetime object to 0. This effectively rounds down the datetime to the nearest minute.
#                 minute=(dt.minute // 5) * 5: This part is rounding down the minute to the nearest multiple of 5. This is done by performing integer division of the minute by 5 (dt.minute // 5), which effectively rounds down to the nearest whole number, and then multiplying the result by 5.
#                 So, if the original datetime is 2022-07-15 14:23:45, the timeline_start would be 2022-07-15 14:20:00.

#                 This is being used to create a time interval of 5 minutes, where all events that occur within that 5-minute interval are grouped together. The timeline_start represents the start of that interval.

#                 """
#                 timeline_start = dt.replace(
#                     second=0, microsecond=0, minute=(dt.minute // 5) * 5
#                 )

#                 # print(f"timeline_start {timeline_start}")

#                 bucketed_data[row.entity_id][row.key][timeline_start].append(row)


#             # print(f"printing the no of keys {len(bucketed_data)}")


#             '''
#             for entity_id, entity_data in bucketed_data.items():

#                 for key, key_data in entity_data.items():

#                     # rows_list it the array of objects (it menans it contains all the rows with the same key, entity_id, and within the same 5-minute window))
#                     for timeline_start, rows_list in key_data.items():

#                         # now we are going to fetch the single single row from the array

#                         num_values_for_avg = []

#                         for row in rows_list:
#                             # logging.info(f"printing the row {row}")

#                             if row.long_v is not None:

#                                 """
#                                 logging.info(f"long_v is not null{row.long_v}")
#                                 """

#                                 num_values_for_avg.append(float(row.long_v))

#                             elif row.dbl_v is not None:

#                                 """
#                                 logging.info(f"dbl_v is not null{row.dbl_v}")
#                                 """

#                                 num_values_for_avg.append(row.dbl_v)

#                         """
#                         this if will deal with numeric values
#                         """

#                         if num_values_for_avg:
#                             sumofno = sum(num_values_for_avg)

#                             avg_value = sumofno / len(num_values_for_avg)

#                             """
#                             logging.info(f"avg value of {timeline_start} is {avg}")
#                             """

#                             representative_timestamp = timeline_start

#                             if isinstance(representative_timestamp,int):
#                                 representative_timestamp_in_unix_system = representative_timestamp
#                             else:
#                                 representative_timestamp_in_unix_system = int(representative_timestamp.timestamp() * 1000)


#                             """
#                             logging.info(f"representative_timestamp {representative_timestamp}")
#                             """

#                             logging.info(f"object creation started for row ")

#                             new_CompressedDeviceEventLog = CompressedDeviceEventLog(
#                                 entity_id=entity_id,
#                                 key=key,
#                                 ts=representative_timestamp_in_unix_system,
#                                 dbl_v=avg_value,
#                                 bool=None,
#                                 str_v=None,
#                                 long_v=None,
#                                 json_v=None,
#                             )

#                             logging.info(f"object creation started for row ")

#                             db.session.add(new_CompressedDeviceEventLog)

#                             logging.info(f"session committing.......... ")

#                             db.session.commit()

#                             logging.info(
#                                 f"Successfully inserted row with id={entity_id}"
#                             )

#                         for row in rows_list:

#                             if row.long_v is None and row.dbl_v is None:

#                                 if isinstance(row.ts,int):
#                                     representative_timestamp_in_unix_system = row.ts
#                                 else:
#                                     representative_timestamp_in_unix_system = int(
#                                         row.ts.timestamp() * 1000
#                                     )


#                                 new_CompressedDeviceEventLog = CompressedDeviceEventLog(
#                                     entity_id=row.entity_id,
#                                     key=row.key,
#                                     ts=representative_timestamp_in_unix_system,
#                                     dbl_v=None,
#                                     bool=row.bool,
#                                     str_v=row.str_v,
#                                     long_v=None,
#                                     json_v=row.json_v,
#                                 )

#                                 logging.info(f"object creation started for row ")

#                                 db.session.add(new_CompressedDeviceEventLog)

#                                 logging.info(f"session committing.......... ")

#                                 db.session.commit()

#                                 logging.info(
#                                     f"Successfully inserted row with id={entity_id}"
#                                 )
#             '''

#             page += 1
#             print(f"page {page}")


#         """
#         you can use the `.get()` method to access the elements in a more safe way, avoiding KeyError:
#         python
#         rows_list = bucketed_data.get(key, {}).get(entity_id, {}).get(timeline_start, [])
#         first_row = rows_list[0] if rows_list else None

#         if any of the intermediate dictionaries do not exist, the `.get()` method will return an empty dictionary `{}` or an empty list `[]`, respectively.


#         structure of the bucketed data

#                 bucketed_data = {
#                     'key1': {
#                             'entity_id1': {
#                                             'timeline_start1': [row1, row2],
#                                             'timeline_start2': [row3, row4]
#                                      },
#                             'entity_id2': {
#                                     'timeline_start1': [row5, row6]
#                             }
#                         },
#                     'key2': {
#                         'entity_id1': {
#                             'timeline_start1': [row7, row8]
#                         }
#                         'entity_id2': {
#                             'timeline_start1': [row5, row6],
#                             'timeline_start2': [row7, row8],
#                             'timeline_start3': [row9, row10],
#                             'timeline_start4': [row11, row12]
#                         }
#                     }
#                 }

#         """

#         """

#             for entity_id, entity_data in bucketed_data.items():

#         logging.info(f"key:{entity_id} :  ")
#         logging.info(" ")
#         logging.info(" ")

#         for key, bucketed_rows in entity_data.items():

#             logging.info(f"entity_id:{key}")

#             logging.info(" ")
#             logging.info(" ")
#             for timeline_start, rows_list in bucketed_rows.items():
#                 logging.info(f"timeline_start:{timeline_start}")

#                 logging.info(" ")
#                 logging.info(" ")

#                 if rows_list:
#                     logging.info(rows_list)

#         """

#         # logging.info(f"printing the size of the compressed data {len(compressed_data)}")


#           # print(f"printing the no of keys {len(bucketed_data)}")

#         for entity_id, entity_data in bucketed_data.items():

#                 for key, key_data in entity_data.items():

#                     # rows_list it the array of objects (it menans it contains all the rows with the same key, entity_id, and within the same 5-minute window))
#                     for timeline_start, rows_list in key_data.items():

#                         # now we are going to fetch the single single row from the array

#                         num_values_for_avg = []

#                         for row in rows_list:
#                             # logging.info(f"printing the row {row}")

#                             if row.long_v is not None:

#                                 """
#                                 logging.info(f"long_v is not null{row.long_v}")
#                                 """

#                                 num_values_for_avg.append(float(row.long_v))

#                             elif row.dbl_v is not None:

#                                 """
#                                 logging.info(f"dbl_v is not null{row.dbl_v}")
#                                 """

#                                 num_values_for_avg.append(row.dbl_v)

#                         """
#                         this if will deal with numeric values
#                         """

#                         if num_values_for_avg:
#                             sumofno = sum(num_values_for_avg)

#                             avg_value = sumofno / len(num_values_for_avg)

#                             """
#                             logging.info(f"avg value of {timeline_start} is {avg}")
#                             """

#                             representative_timestamp = timeline_start

#                             if isinstance(representative_timestamp,int):
#                                 representative_timestamp_in_unix_system = representative_timestamp
#                             else:
#                                 representative_timestamp_in_unix_system = int(representative_timestamp.timestamp() * 1000)


#                             """
#                             logging.info(f"representative_timestamp {representative_timestamp}")
#                             """

#                             logging.info(f"object creation started for row ")

#                             new_CompressedDeviceEventLog = CompressedDeviceEventLog(
#                                 entity_id=entity_id,
#                                 key=key,
#                                 ts=representative_timestamp_in_unix_system,
#                                 dbl_v=avg_value,
#                                 bool=None,
#                                 str_v=None,
#                                 long_v=None,
#                                 json_v=None,
#                             )

#                             logging.info(f"object creation started for row ")

#                             db.session.add(new_CompressedDeviceEventLog)

#                             logging.info(f"session committing.......... ")

#                             db.session.commit()

#                             logging.info(
#                                 f"Successfully inserted row with id={entity_id}"
#                             )

#                         for row in rows_list:

#                             if row.long_v is None and row.dbl_v is None:

#                                 if isinstance(row.ts,int):
#                                     representative_timestamp_in_unix_system = row.ts
#                                 else:
#                                     representative_timestamp_in_unix_system = int(
#                                         row.ts.timestamp() * 1000
#                                     )


#                                 new_CompressedDeviceEventLog = CompressedDeviceEventLog(
#                                     entity_id=row.entity_id,
#                                     key=row.key,
#                                     ts=representative_timestamp_in_unix_system,
#                                     dbl_v=None,
#                                     bool=row.bool,
#                                     str_v=row.str_v,
#                                     long_v=None,
#                                     json_v=row.json_v,
#                                 )

#                                 logging.info(f"object creation started for row ")

#                                 db.session.add(new_CompressedDeviceEventLog)

#                                 logging.info(f"session committing.......... ")

#                                 db.session.commit()

#                                 logging.info(
#                                     f"Successfully inserted row with id={entity_id}"
#                                 )


#         return (
#             jsonify(
#                 {
#                     "message": "successfully done",
#                     "status": 200,
#                     "bucketed_data": "data bucked successfully",
#                 }
#             ),
#             200,
#         )

#     except Exception as e:

#         # Log error (you can also use logging here)
#         logging.error(f"❌ Error occurred while fetching data: {str(e)}")

#         taceback_str = traceback.format_exc()

#         logging.error(f"Traceback: {taceback_str}")

#         # Return proper error response
#     return (
#         jsonify(
#             {
#                 "error": "Something went wrong while fetching data.",
#                 "details": str(e),
#             }
#         ),
#         500,
#     )
