from sqlalchemy import inspect
from fetusapp import db

# Debug table existence
inspector = inspect(db.engine)
tables = inspector.get_table_names()
print("Available tables:", tables)

# # Debug query
# medical_history = HistoryMedical.query
# print("SQL Query:", str(medical_history))

# # Execute and check results
# results = medical_history.all()
# print("Total records:", len(results))

# if results:
#     for record in results:
#         print(f"Record ID: {record.id}")
# else:
#     print("No records found in HistoryMedical table")