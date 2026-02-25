""""
Responsibility:

Extracts CAGR phrases from content
(NO SEARCHING)
Expects:
Links
"""
from bs4 import BeautifulSoup
from typing import Optional, List
import re



class ProcessCagr:
    def __init__(self):
        pass

    def get_match_phrases(self, contents: Optional[List[str]]) -> Optional[List[str]]:
        phrases = []

        for content in contents:
            if not content:
                continue

            phrase = self._find_phrase(content)

            if phrase:
                phrases.append(phrase)

        #TODO: Deal with Nest Phrases ?

        phrases = sum(phrases, [])

        return phrases


    def _find_phrase(self, content: str) -> Optional[List[str]]:
        soup = BeautifulSoup(content, 'html.parser')

        for element in soup(['script', 'style', 'meta', 'noscript', 'iframe']):
            element.decompose()

        text = soup.get_text(strip=True) #seperator = " "

        keyword = "CAGR"

        keyword_regex = r'\\b\\d+\\.?\\d+?[%]'

        detected_phrases = re.findall(
        rf'[^.?!]*\b{re.escape(keyword)}\b[^.?!]*{keyword_regex}',
               text,
               flags=re.IGNORECASE)

        return detected_phrases

