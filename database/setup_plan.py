"""
Clear and update current plan in the database.

"""

from time import time

from numpy import genfromtxt
from sqlalchemy.orm import sessionmaker

from database import models


def Load_Data(file_name):
    data = genfromtxt(
        file_name,
        delimiter=",",
        skip_header=1,
        dtype=None,
        encoding="utf-8",
        missing_values=None,
    )
    return data.tolist()


def setupPlanTable():
    t = time()

    # Create the session
    session = sessionmaker()
    session.configure(bind=models.engine)
    s = session()
    try:
        file_name = "files/plan_data_feb.csv"
        data = Load_Data(file_name)
        s.query(models.PlanCurrent).delete()  # clean table

        for i in data:
            record = models.PlanCurrent(
                **{
                    "art_no": i[0].lower(),
                    "size": i[1].lower(),
                    "color": i[2].lower(),
                    "category": i[3].lower(),
                    "mould_no": None,
                    "pairs": i[4],
                    "plan": i[5],
                }
            )
            s.add(record)  # Add all the records

        s.commit()  # Attempt to commit all the records
    except Exception as e:
        s.rollback()  # Rollback the changes on error
        print("rollbacked\n%s" % e)
    finally:
        s.close()  # Close the connection
    print("Time elapsed: " + str(time() - t) + " s.")  # 0.091s
