from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String,insert
from sqlalchemy.exc import SQLAlchemyError
import logging


# -------------------------------
# ✅ Setup Logging
# -------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s -%(message)s'
)



# -------------------------------
# 🔌 Connect to PostgreSQL
# -------------------------------
try:
    logging.info("Connecting to PostgreSQL database...") 
    

    # Replace with your actual PostgreSQL connection string
    engine = create_engine('postgresql+psycopg2://postgres:root@localhost:5432/Test_sqlalchemy', 
                           echo=True  )
    
     # echo = true Logs SQL statements to the terminal


    # Create a MetaData instance to hold table definitions
    meta = MetaData()


 # -------------------------------
    # 🧱 Define the 'people' table
    # -------------------------------
    people = Table(
        "people",
        meta,
        Column('id', Integer, primary_key=True),
        Column("name", String, nullable=False),
        Column("age", Integer)
    )

    # Create the table in the database if it doesn't exist
    #meta.create_all(engine)

    logging.info("Connected successfully. Preparing to execute UPDATE statement...")
 

     # -------------------------------
    # ✏️ Perform the UPDATE operation
    # with is context manager
    # -------------------------------
    with engine.connect() as conn:

        logging.info("Starting transaction...")


        # 🔄 Build the UPDATE statement to change 'age' where name is 'mike'
        # 🟢 Build SELECT query
        delete_statement = people.delete().where(people.c.name == 'mike')



        logging.info("Executing delete for user 'mike'...")



        # 🚀 Execute the update
        result = conn.execute(delete_statement)

        # 💾 Commit the transaction
        conn.commit()

        logging.info("Update committed successfully.")


       # 🔍 Log affected row count
        logging.info("Rows affected: %d", result.rowcount)
        print(result)


except SQLAlchemyError as e:
    print("❌ SQLAlchemy error occurred:", str(e))
except Exception as ex:
    print("❌ General error:", str(ex))