import pandas as pd

from core.kepegawaian.kepeg_cuti_approval import save_cuti_approval
from core.kepegawaian.kepeg_cuti_approval_chain import update_approval_chain
from core.smartoffice.eo_cuti_approval import fetch_cuti_approval


def main():
    df = fetch_cuti_approval()
    save_cuti_approval(df)
    update_approval_chain(df)

def cleanup(df: pd.DataFrame):
    df["created_at"]= df["created_at"].swifter.apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S'))

if __name__ == "__main__":
    main()
