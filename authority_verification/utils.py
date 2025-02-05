import os
import re
import json
from tqdm import tqdm
from docx import Document
from typing import Dict, List
from unidecode import unidecode
from docx.enum.text import WD_COLOR_INDEX
from . import config, doc_utils, docx_handler

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
		json.dump(input_dict, json_file, indent = 4, ensure_ascii = False)

def load_json(file_path: str) -> Dict:
	"""
		Load a JSON file.

		Parameters:
			file_path (str): The path of the file.
		
		Returns:
			Dict: The dictionary loaded from the JSON file.
	"""
	with open(file_path, 'r', encoding='utf-8') as f:
		data = json.load(f)
	return data

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

def index_one_documents(document_path: str):
    dochandler = docx_handler.DocxHandler(document_path)
    dochandler.read_docx()
    dochandler.index_document()
    dochandler.save_indexed_paragraphs_to_json()

def find_ref_one_document(file_path: str):
	doc = docx_handler.DocxHandler(file_path)
	doc.read_docx()
	doc.index_document()
	doc.save_indexed_paragraphs_to_json()
	doc_dict = doc.paragraphs_index
	output = {}
	for key, value in doc_dict.items():
		ref_list = doc_utils.extract_reference_from_txt(value, key)
		if ref_list:
			output[key] = ref_list
		else:
			output[key] = []
	with open(config.OUTPUT_PATH + get_name_from_path(file_path) + '_ref.json', 'w', encoding="utf-8") as json_file:
		json_file.write(json.dumps(output, indent = 4, ensure_ascii = False))

def find_ref_all_legal_docs():
	for root, dirs, files in os.walk(config.LEGAL_DOCS_PATH):
		for file in tqdm(files):
			file_path = os.path.join(config.LEGAL_DOCS_PATH, file)
			print(file_path)
			find_ref_one_document(file_path)
			print("Done processing " + file_path)

def remove_unwanted_docs(file_path: str):
	output = {}
	doc = docx_handler.DocxHandler(file_path)
	doc.read_docx()
	doc.index_document()
	doc.save_indexed_paragraphs_to_json()
	doc_dict = doc.paragraphs_index
	agencies_list = load_json(config.VIETNAM_AGENCIES_LIST_PATH)["vietnam_agencies"]
	for key, value in doc_dict.items():
		for agency in agencies_list:
			if agency in value:
				output[key] = value
	
	with open(config.OUTPUT_PATH + get_name_from_path(file_path) + '_filtered.json', 'w', encoding="utf-8") as json_file:
		json_file.write(json.dumps(output, indent = 4, ensure_ascii = False))

def find_match_key(input_dict: Dict, input_key: str):
	output = []
	input_key_list = input_key.split('.')
	if input_key_list[3] != '0':
		for key in input_dict.keys():
			if key[2:] == input_key[2:]:
				output.append(key)
				break
	if input_key_list[3] == '0' and input_key_list[2] != '0':
		for key in input_dict.keys():
			if key[2:-2] == input_key[2:-2]:
				output.append(key)
	if input_key_list[3] == '0' and input_key_list[2] == '0' and input_key_list[1] != '0':
		for key in input_dict.keys():
			if key[1:-2] == input_key[2:-4]:
				output.append(key)
	return output

def document_augmentation(file_path: str, is_save_index: bool, is_save_ref: bool, is_save_filtered: bool):
	doc_filtered = {}
	doc_ref = {}
	doc = docx_handler.DocxHandler(file_path)
	doc.read_docx()
	doc.index_document()
	if is_save_index:
		doc.save_indexed_paragraphs_to_json()
	doc_dict = doc.paragraphs_index
	agencies_list = load_json(config.VIETNAM_AGENCIES_LIST_PATH)["vietnam_agencies"]
	for key, value in doc_dict.items():
		for agency in agencies_list:
			if agency in value:
				doc_filtered[key] = value
	
	if is_save_filtered:
		with open(config.OUTPUT_PATH + get_name_from_path(file_path) + '_filtered.json', 'w', encoding="utf-8") as json_file:
			json_file.write(json.dumps(doc_filtered, indent = 4, ensure_ascii = False))
	
	for key, value in doc_filtered.items():
		ref_list = doc_utils.extract_reference_from_txt(value, key)
		if ref_list:
			doc_ref[key] = ref_list
			for reference in ref_list:
				matched_keys = find_match_key(doc_dict, reference)
				if matched_keys:
					for matched_key in matched_keys:
						doc_filtered[key] += ' ' + doc_dict[matched_key]
		else:
			doc_ref[key] = []
	
	if is_save_ref:
		with open(config.OUTPUT_PATH + get_name_from_path(file_path) + '_ref.json', 'w', encoding="utf-8") as json_file:
			json_file.write(json.dumps(doc_ref, indent = 4, ensure_ascii = False))
	
	with open(config.OUTPUT_PATH + get_name_from_path(file_path) + '_augmented.json', 'w', encoding="utf-8") as json_file:
		json_file.write(json.dumps(doc_filtered, indent = 4, ensure_ascii = False))
	
if __name__ == "__main__":
	# find_ref_one_document(config.PURSUANT_DOCUMENT_PATH)
	find_ref_all_legal_docs()