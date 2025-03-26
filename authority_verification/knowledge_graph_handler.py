import json
from . import docx_handler
from authority_verification import config

def table_extraction(document_path: str):
    dochandler = docx_handler.DocxHandler(document_path)
    dochandler.read_docx()
    document = dochandler.document
    table = document.tables[10]
    # print(table)
    data = []

    keys = None
    for i, row in enumerate(table.rows):
        text = (cell.text for cell in row.cells)

        # Establish the mapping based on the first row
        # headers; these will become the keys of our dictionary
        if i == 0:
            keys = tuple(text)
            continue

        # Construct a dictionary for this row, mapping
        # keys to values for this row
        row_data = dict(zip(keys, text))
        data.append(row_data)
    return data

def knowledge_graph_construction(document_path: str):
    data = {"Ngành, nghề đầu tư kinh doanh có điều kiện" : []}
    table_datas = table_extraction(document_path)
    for table_data in table_datas:
        print(table_data)
        data["Ngành, nghề đầu tư kinh doanh có điều kiện"].append(table_data["NGÀNH, NGHỀ"])
    with open(config.KNOWLEDGE_GRAPH_PATH + 'knowledge_graph_conditional.json', 'w', encoding="utf-8") as json_file:
        json.dump(data, json_file, indent = 4, ensure_ascii = False)