"""
Initialize data in master tables.

Required only to re-setup database from start.
"""
from time import time

from numpy import genfromtxt
from sqlalchemy.orm import sessionmaker

from database import models


def Load_Data(file_name):
    # skip_header=1,
    data = genfromtxt(
        file_name,
        delimiter="\t",
        skip_header=1,
        dtype=None,
        encoding="utf-8",
        missing_values=None,
    )
    return data.tolist()


def rec_cat(i):
    return models.Category(**{"name": i[2].lower(), "sap_code": i[1].lower()})


def rec_col(i):
    return models.Color(**{"name": i[1].lower(), "sap_code": i[2].lower()})


def rec_sole(i):
    return models.SoleColor(
        **{"name": i[1].lower(), "color_outer": i[2].lower(), "color_mid": i[3].lower()}
    )


def rec_mac(i):
    return models.Machine(
        **{
            "name": i[1].lower(),
            "machine_type": i[2].lower(),
            "stations": i[3],
            "rotation_time": i[4],
            "specification": i[5].lower(),
            "made_in": i[6],
            "manufacturer": i[7],
        }
    )


def rec_mldmod(i):
    return models.MouldModel(
        **{
            "mould_no": i[1].lower(),
            "alt_name": i[2],
            "model": i[3].lower(),
            "style": i[4].lower(),
            "notes": i[5],
        }
    )


def rec_mldset(i):
    return models.MouldSet(
        **{
            "mould_model": i[1],
            "mould_type": i[2].lower(),
            "category": i[4],
            "machines": i[3],
        }
    )


def rec_mld(i):
    return models.Mould(**{"mould_set": i[1], "size": i[2], "quantity": i[3]})


def rec_artm(i):
    return models.ArticleModel(
        **{
            "art_no": i[1].lower(),
            "article_type": i[2].lower(),
            "brand": i[3].lower(),
            "licensed": i[4],
        }
    )


def rec_art(i):
    return models.Article(
        **{
            "article": i[1],
            "color": i[2],
            "category": i[3],
            "mould": i[4],
            "sole_color": i[5],
            "sole_type": i[6].lower(),
        }
    )


def rec_pcks(i):
    return models.PackingStyle(
        **{"category": i[1], "size_matrix": i[2].lower(), "pairs": i[3]}
    )


def rec_pcko(i):
    return models.PackingOrder(**{"packing": i[1], "size": i[2], "quantity": i[3]})


def setupInitializeAllTables():
    """Initialize data in all main tables"""

    t = time()

    table_list = {
        "files/category.txt": rec_cat,
        "files/color.txt": rec_col,
        "files/sole_color.txt": rec_sole,
        "files/machine.txt": rec_mac,
        "files/mould_model.txt": rec_mldmod,
        "files/mould_set.txt": rec_mldset,
        "files/mould.txt": rec_mld,
        "files/article_model.txt": rec_artm,
        "files/article.txt": rec_art,
        "files/packing_style.txt": rec_pcks,
        "files/packing_order.txt": rec_pcko,
    }

    # Create the session
    session = sessionmaker()
    session.configure(bind=models.engine)
    for tbl in table_list.keys():
        s = session()
        try:
            file_name = tbl
            data = Load_Data(file_name)

            for i in data:
                record = table_list[tbl](i)
                s.add(record)  # Add all the records

            s.commit()  # Attempt to commit all the records
        except Exception as e:
            s.rollback()  # Rollback the changes on error
            print(f"Error: {tbl}\n{e}")
        finally:
            s.close()  # Close the connection
            print("______________________")
        print("Time elapsed: " + str(time() - t) + " s.")  # 0.091s
