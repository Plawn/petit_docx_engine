from typing import Generator, Iterable, Set


def xml_cleaner(words: Iterable) -> Generator[str, None, None]:
    """Enlève les tags XML résiduels pour une liste de mots"""
    for word in words:
        chars = list()
        in_tag = False
        for char in word:
            if char == "<":
                in_tag = True
            elif char == ">":
                in_tag = False
            elif not in_tag:
                chars.append(char)
        yield ''.join(chars)


def get_text_from_table(table) -> Generator[str, None, None]:
    for row in table.rows:
        for cell in row.cells:
            yield cell.text


def get_text_from_doc_part(doc_part) -> Set[str]:
    res: Set[str] = set()
    for p in doc_part.paragraphs:
        res.add(p.text)
    # getting all text from tables
    for table in doc_part.tables:
        for text in get_text_from_table(table):
            res.add(text)
    return res
