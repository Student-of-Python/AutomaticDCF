from difflib import SequenceMatcher

def most_similiar(keyword: str, list_: list) -> str:
    """
    :param keyword: Keyword
    :param list_: List of possible Matches
    :return: Word from List_ that matches keyword the most
    """
    ratios = [SequenceMatcher(None, keyword,word).ratio() for word in list_]
    index = ratios.index(max(ratios))
    return list_[index]


