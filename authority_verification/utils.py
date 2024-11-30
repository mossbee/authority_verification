import os
import json
import config
from tqdm import tqdm
from typing import Dict
from docx import Document
from unidecode import unidecode
from docx.enum.text import WD_COLOR_INDEX

def roman_to_int(s):
	"""
		Convert a Roman numeral to an integer.

		Parameters:
			s (str): The Roman numeral to be converted.
		
		Returns:
			int: The integer equivalent of the input Roman numeral.

		Example:
			>>> roman_to_int('III')
			3
	"""
	rom_val = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
	int_val = 0
	for i in range(len(s)):
		if i > 0 and rom_val[s[i]] > rom_val[s[i - 1]]:
			int_val += rom_val[s[i]] - 2 * rom_val[s[i - 1]]
		else:
			int_val += rom_val[s[i]]
	return int_val

def get_name_from_path(file_path:str):
	"""
		Get the name of the file from the file path.

		Parameters:
			file_path (str): The path of the file.
		
		Returns:
			str: The name of the file.

		Example:
			>>> get_name_from_path('data/legal_cases/65/219_2013_TT-BTC_220761.docx')
			'219_2013_TT-BTC_220761'
	"""
	return file_path.split("/")[-1][:-5]

def json_dumper(input_dict: Dict, file_path: str, purpose: str):
	"""
		Write a dictionary to a JSON file.

		Parameters:
			input_dict (Dict): The dictionary to be written to the JSON file.
			file_path (str): The path of the file.
			purpose (str): The purpose of the JSON file.
		
		Returns:
			None
	"""
	with open(config.OUTPUT_PATH + get_name_from_path(file_path) + purpose, 'w', encoding="utf-8") as json_file:
		# json.dump(document_json, json_file, indent=4, ensure_ascii=False)
		json.dump(input_dict, json_file, indent = 4, ensure_ascii = False)

def return_paragraphs():
	"""
		Return the paragraphs of a document.

		Parameters:
			None
		
		Returns:
			None
	"""
	document = Document(config.CASE_DOCUMENT_PATH)
	paragraph = {}
	for i in range(len(document.paragraphs)):
		paragraph[i] = document.paragraphs[i].text
	json_dumper(paragraph, config.CASE_DOCUMENT_PATH, "_paragraphs.json")

def rename_docx_file():
	"""
		Rename the docx files in the legal documents folder.

		Parameters:
			None
		
		Returns:
			None
	"""
	folder_list = config.LEGAL_DOCS_PATH
	for file in os.listdir(folder_list):
		if file.endswith(".docx"):
			temp_name = file.split("_")
			temp = temp_name[0]
			temp_name[0] = temp_name[1]
			temp_name[1] = temp
			# os.rename(file, "_".join(temp_name))
			os.rename(os.path.join(folder_list, file), os.path.join(folder_list, "_".join(temp_name)))

def get_agencies_list():
	"""
		Get the list of agencies from the JSON file.

		Parameters:
			None
		
		Returns:
			list: The list of agencies.
	"""
	with open(config.VIETNAM_AGENCIES_LIST_PATH, 'r', encoding='utf-8') as f:
		vietnam_agencies = json.load(f)
	return vietnam_agencies["vietnam_agencies"]

def finding_sentences_contain_keyword():
	"""
		Find the sentences that contain the agencies from the legal documents.

		Parameters:
			None
		
		Returns:
			None
	"""
	vietnam_agencies = get_agencies_list()
	matching = []
	for file in tqdm(os.listdir(config.LEGAL_DOCS_PATH)[:20]):
		if file.endswith(".docx"):
			doc = Document(os.path.join(config.LEGAL_DOCS_PATH, file))
			for paragraph in doc.paragraphs:
				for agency in vietnam_agencies:
					if agency in paragraph.text:
						matching.append({
							"file": file,
							"agency": agency,
							"sentence": paragraph.text
						})
						break

	json_dumper(matching, config.OUTPUT_PATH + "legal_docs", "_matching.json")

def highlight_agencies(file: str):
	"""
		Highlight the agencies in a document.

		Parameters:
			file (str): The path of the document.
		
		Returns:
			None
	"""
	doc = Document(file)
	vietnam_agencies = get_agencies_list()
	# Iterate through paragraphs and runs to find and highlight the agencies
	for agency in vietnam_agencies:
		for paragraph in doc.paragraphs:
			for run in paragraph.runs:
				original_text = run.text
				normalized_text = unidecode(original_text).lower()
				if unidecode(agency).lower() in normalized_text:
					start = normalized_text.find(unidecode(agency).lower())
					end = start + len(unidecode(agency).lower())
					run.text = original_text[:start] + original_text[start:end] + original_text[end:]
					run.font.highlight_color = WD_COLOR_INDEX.YELLOW  # Highlight with yellow color
	
	# Save the modified document with the new name
	new_file_name = file.replace('.docx', '_highlighted.docx')
	doc.save(new_file_name)

if __name__ == "__main__":
	# return_paragraphs()
	# rename_docx_file()
	finding_sentences_contain_keyword()