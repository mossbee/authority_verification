import os
import re
import json
import config
from tqdm import tqdm
from typing import Dict, List
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

def extract_numbers(text, start, end):
	"""
		Extract numbers from a text.

		Parameters:
			text (str): The text to extract numbers from.
			start (int): The start index of the text.
			end (int): The end index of the text.

		Returns:
			list: The list of numbers extracted from the text.
		
		Example:
			>>> extract_numbers("The price is $1000.", 15, 20)
			[1000]
	"""
    # Slicing the text from start to end index
	sliced_text = text[start:end+1]
    # Using regular expression to find all numbers in the sliced text
	numbers = re.findall(r'\b\d+\b', sliced_text)
    # Converting found numbers from strings to integers
	return [number for number in numbers]

def extract_characters(text, start_index, end_index):
    # Extract the substring based on the provided indices
    substring = text[start_index:end_index + 1]

    # Use regular expression to find all standalone characters
    # \b is a word boundary, \w is any word character, and {1} specifies exactly one occurrence of a word character
    pattern = r'\b\w{1}\b'
    alone_characters = re.findall(pattern, substring)

    return alone_characters

def extract_reference(index, text):
	dieu_list = []
	khoan_list = []
	diem_list = []
	index_list = index.split(".")
	text_lower = text.lower()
	if "điều này" in text_lower:
        # Get first appear of "Điều này"
		dieu_nay_index = text_lower.find("điều này")
		if "khoản" in text_lower and text_lower.find("khoản") < dieu_nay_index:
			khoan_index = text_lower.find("khoản")
			if "điểm" in text_lower and text_lower.find("điểm") < khoan_index:
				# Get first appear Điểm index
				diem_index = text_lower.find("điểm")
				diem_list = extract_characters(text_lower, diem_index, khoan_index)
			khoan_list = extract_numbers(text_lower, khoan_index, dieu_nay_index)
			dieu_list.append(index_list[0])
		else:
			dieu_list.append(index_list[0])
	else:
		if "điều" in text_lower:
            # Get first appear of "Điều"
			dieu_index = text_lower.find("điều")
			if "khoản" in text_lower and text_lower.find("khoản") < dieu_index:
                # Get first appear Khoản index
				khoan_index = text_lower.find("khoản")
				if "điểm" in text_lower and text_lower.find("điểm") < khoan_index:
					# Get first appear Điểm index
					diem_index = text_lower.find("điểm")
					diem_list = extract_characters(text_lower, diem_index, khoan_index)
                # for character in text from khoan_index to dieu_index
				khoan_list = extract_numbers(text_lower, khoan_index, dieu_index)
				dieu_list = extract_numbers(text_lower, dieu_index, dieu_index+10)
			else:
				dieu_list = extract_numbers(text_lower, dieu_index, len(text_lower)-1)
				if len(index_list) > 10:
					dieu_list = dieu_list[:10]
		else:
			if "khoản" in text_lower:
                # Get first appear Khoản index
				khoan_index = text_lower.find("khoản")
				if "điểm" in text_lower and text_lower.find("điểm") < khoan_index:
					# Get first appear Điểm index
					diem_index = text_lower.find("điểm")
					diem_list = extract_characters(text_lower, diem_index, khoan_index)
                # for character in text from khoan_index to end of text
				khoan_list = extract_numbers(text_lower, khoan_index, len(text_lower)-1)
				if len(index_list) > 10:
					khoan_list = khoan_list[:10]
				dieu_list.append(index_list[0])
			else:
				if "điểm" in text_lower:
					# Get first appear Điểm index
					diem_index = text_lower.find("điểm")
					diem_list = extract_numbers(text_lower, diem_index, len(text_lower)-1)
					if len(index_list) > 10:
						diem_list = diem_list[:10]
					khoan_list.append(index_list[1])
					dieu_list.append(index_list[0])
	return dieu_list, khoan_list, diem_list

def get_reference(index, text, ref_data):
	dieu_list, khoan_list, diem_list = extract_reference(index, text)
	if len(dieu_list) == 1:
		if len(khoan_list) > 1:
			for khoan in khoan_list:
				ref_index = f"{dieu_list[0]}.{khoan}.0"
				return ref_data[ref_index] if ref_index in ref_data else ""
		else:
			for diem in diem_list:
				ref_index = f"{dieu_list[0]}.{khoan_list[0]}.{diem}"
				return ref_data[ref_index] if ref_index in ref_data else ""
	else:
		for dieu in dieu_list:
			ref_index = f"{dieu}.0.0"
			return ref_data[ref_index] if ref_index in ref_data else ""

def get_higher_level_index(index, ref_data):
	index_list = index.split(".")
	if index_list[2] != "0":
		return ref_data[f"{index_list[0]}.{index_list[1]}.0"]
	elif index_list[2] == "0" and index_list[1] != "0":
		return ref_data[f"{index_list[0]}.0.0"]

def extract_point_clause_article(input: str) -> :
	input_words = input.split()
	for i in range(len(input_words)):
		if input_words[i].lower() == "điểm":
			if input_words[i + 1] == "này":
				return [0, 0, 0]
			# if input_words[i + 1] is a character a-z
			elif input_words[i + 1].isalpha():
				if input_words[i + 2] == "khoản":
					pass

def handle_clause(given_list: List[str], cur_index: int):
	if given_list[cur_index + 1].isnumeric():
		if given_list[cur_index + 2] == "điểm":
			handle_article()
		if given_list[cur_index + 2] == "khoản":
			pass
			
def handle_article(given_list: List[str], cur_index: int):
	pass

if __name__ == "__main__":
	# return_paragraphs()
	# rename_docx_file()
	# Ví dụ sử dụng
	text = """
	) Diện tích giao đất, cho phép chuyển mục đích sử dụng đất quy định tại điểm a và điểm b khoản này được tính cho tổng diện tích đất được Nhà nước giao, cho phép chuyển mục đích sử dụng đất trong quá trình thực hiện các chính sách về đất đai đối với đồng bào dân tộc thiểu số. 
	"""
	references = extract_legal_references(text)
	print(references)