import pandas as pd
from neo4j import GraphDatabase
import time

# --- CONFIGURATION ---
NEO4J_URI = "bolt://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "database"
CSV_FILE = "final_with_libraries.csv"
# ---------------------

# UPDATED QUERY: Now saves 'libraries' property!
import_query = """
UNWIND $batch AS row
MERGE (r:Repository {name: row.name})
SET r.stars = toInteger(row.stars),
    r.description = row.description,
    r.owner = row.owner,
    r.libraries = row.libraries  // <--- ADDED THIS LINE

WITH r, row
FOREACH (ignoreMe IN CASE WHEN row.primaryLanguage IS NOT NULL AND row.primaryLanguage <> "" THEN [1] ELSE [] END | 
    MERGE (l:ProgrammingLanguage {name: row.primaryLanguage})
    MERGE (r)-[:IS_WRITTEN_IN]->(l)
)

WITH r, row
FOREACH (topicName IN split(row.topics, ";") | 
    MERGE (t:TopicTag {name: trim(topicName)})
    MERGE (r)-[:HAS_TOPIC]->(t)
)
"""

def ingest_data():
    print(f"Connecting to {NEO4J_URI}...")
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    print("Reading CSV...")
    chunk_size = 1000
    # dtype=str ensures we read everything as text first to avoid errors
    chunks = pd.read_csv(CSV_FILE, chunksize=chunk_size, dtype=str, nrows=1000)

    total_rows = 0
    start_time = time.time()

    try:
        with driver.session() as session:
            for i, chunk in enumerate(chunks):
                # 1. CLEAN THE DATA
                chunk = chunk.fillna("")

                # 2. CONVERT TO DICTIONARY
                batch_data = chunk.to_dict('records')

                # 3. RUN QUERY
                session.run(import_query, batch=batch_data)

                total_rows += len(batch_data)
                print(f"Processed batch {i+1} ({total_rows} rows total)...", end='\r')

        print(f"\n\nSuccess! Ingested {total_rows} repositories in {round(time.time()-start_time, 2)} seconds.")

    except Exception as e:
        print(f"\n\n❌ Error: {e}")
    finally:
        driver.close()

if __name__ == "__main__":
    ingest_data()