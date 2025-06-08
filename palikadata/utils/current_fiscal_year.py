import nepali_datetime


def get_current_bs_year():
    """
    Returns the current year in Bikram Sambat (BS) using nepali_datetime library.
    """
    today_bs = nepali_datetime.date.today()
    year = today_bs.year
    month = today_bs.month

    if month > 3:
        start_year = year
        end_year = year + 1
    else:
        start_year = year - 1
        end_year = year

    fiscal_year_str = f"{start_year}/{str(end_year)[-2:]}"
    return fiscal_year_str
