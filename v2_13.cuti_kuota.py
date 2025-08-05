from core.kepegawaian.kepeg_cuti_kuota import save_cuti_kuota
from core.smartoffice.eo_cuti_kuota import fetch_cuti_kuota
#noqa
import swifter


def main():
    ck_df = fetch_cuti_kuota()
    ck_df = cleanup(ck_df)
    save_cuti_kuota(ck_df)
    pass


def cleanup(df):
    df["expired"] = df["expired"].swifter.apply(lambda x: x.strftime('%Y-%m-%d'))
    return df


if __name__ == "__main__":
    main()
