import pandas as pd

from core.config import fetch_smartoffice


def fetch_salary_non_taxable_income()->pd.DataFrame:
    query="""
          SELECT id                            AS id,
                 `code`                        AS kode,
                 `value`                       AS nominal,
                 IF(`status` = 1, FALSE, TRUE) AS is_deleted
          FROM salary_non_taxable_income
          """
    return fetch_smartoffice(query)