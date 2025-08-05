from core.kepegawaian.kepeg_cuti_approval_chain import save_approval_chain
from core.smartoffice.eo_cuti_aproval_chain import fetch_cuti_approval_chain


def main():
    cac_df = fetch_cuti_approval_chain()
    save_approval_chain(cac_df)

if __name__ == "__main__":
    main()
