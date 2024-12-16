import os
import re
import json
from . import config
from tqdm import tqdm
from typing import Dict, List
from docx import Document
from unidecode import unidecode
from docx.enum.text import WD_COLOR_INDEX

def is_roman(s: str):
	roman = ['I', 'V', 'X', 'L', 'C', 'D', 'M']
	for char in s:
		if char not in roman:
			return False
	return True

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

def get_higher_level_index(index, ref_data):
	index_list = index.split(".")
	if index_list[2] != "0":
		return ref_data[f"{index_list[0]}.{index_list[1]}.0"]
	elif index_list[2] == "0" and index_list[1] != "0":
		return ref_data[f"{index_list[0]}.0.0"]

def extract_reference_point(input_paragraph: str, input_index: str, start_index: int):
	output = []
	index_list = input_index.split(".")
	input_words = input_paragraph.split()
	input_length = len(input_words)
	for i in range(start_index, input_length):
		# điểm ...
		if input_words[i].lower() == "điểm":
			# if i + 1 not out of range
			if i + 1 < input_length:
				# điểm này
				if input_words[i + 1] == "này":
					output.append(f"0.{index_list[1]}.{index_list[2]}.{index_list[3]}")
					return output, i + 1
				# điểm a ...
				elif input_words[i + 1].isalpha():
					# điểm a khoản ...
					if input_words[i + 2] == "khoản":
						# điểm a khoản này
						if input_words[i + 3] == "này":
							output.append(f"0.{index_list[1]}.{index_list[2]}.{input_words[i + 1]}")
							return output, i + 3
						# điểm a khoản 1 ...
						elif input_words[i + 3].isnumeric():
							# điểm a khoản 1 Điều ...
							if input_words[i + 4] == "Điều":
								# điểm a khoản 1 Điều này
								if input_words[i + 5] == "này":
									output.append(f"0.{index_list[1]}.{input_words[i + 3]}.{input_words[i + 1]}")
									return output, i + 5
								# điểm a khoản 1 Điều 1 ...
								elif input_words[i + 5].isnumeric():
									# điểm a khoản 1 Điều 1 Chương ...
									if input_words[i + 6] == "Chương":
										# điểm a khoản 1 Điều 1 Chương này
										if input_words[i + 7] == "này":
											output.append(f"0.{input_words[i + 5]}.{input_words[i + 3]}.{input_words[i + 1]}")
											return output, i + 7
										# điểm a khoản 1 Điều 1 Chương 1
										elif input_words[i + 7].isnumeric():
											output.append(f"{input_words[i + 7]}.{input_words[i + 5]}.{input_words[i + 3]}.{input_words[i + 1]}")
											return output, i + 7
										# điểm a khoản 1 Điều 1 Chương I
										elif is_roman(input_words[i + 7]) and input_words[i + 7].isupper():
											output.append(f"{roman_to_int(input_words[i + 7])}.{input_words[i + 5]}.{input_words[i + 3]}.{input_words[i + 1]}")
											return output, i + 7
									# điển a khoản 1 Điều 1 abcxyz ...
									elif input_words[i + 6] != "Chương":
										output.append(f"0.{input_words[i + 5]}.{input_words[i + 3]}.{input_words[i + 1]}")
										return output, i + 6
								# điểm a khoản 1 Điều 1,
								elif input_words[i + 5][-1] == "," and input_words[i + 5][:-1].isnumeric():
									output.append(f"0.{input_words[i + 5][:-1]}.{input_words[i + 3]}.{input_words[i + 1]}")
									return output, i + 5
					# điểm a và điểm ...
					elif input_words[i + 2] == "và" and input_words[i + 3] == "điểm":
						# điểm a và điểm b ...
						if input_words[i + 4].isalpha():
							# điểm a và điểm b khoản ...
							if input_words[i + 5] == "khoản":
								# điểm a và điểm b khoản này
								if input_words[i + 6] == "này":
									output.append(f"0.{index_list[1]}.{index_list[2]}.{input_words[i + 1]}")
									output.append(f"0.{index_list[1]}.{index_list[2]}.{input_words[i + 4]}")
									return output, i + 6
								# điểm a và điểm b khoản 1 ...
								elif input_words[i + 6].isnumeric():
									# điểm a và điểm b khoản 1 Điều ...
									if input_words[i + 7] == "Điều":
										# điểm a và điểm b khoản 1 Điều này
										if input_words[i + 8] == "này":
											output.append(f"0.{index_list[1]}.{input_words[i + 6]}.{input_words[i + 1]}")
											output.append(f"0.{index_list[1]}.{input_words[i + 6]}.{input_words[i + 4]}")
											return output, i + 8
										# điểm a và điểm b khoản 1 Điều 1 ...
										elif input_words[i + 8].isnumeric():
											# điểm a và điểm b khoản 1 Điều 1 Chương ...
											if input_words[i + 9] == "Chương":
												# điểm a và điểm b khoản 1 Điều 1 Chương này
												if input_words[i + 10] == "này":
													output.append(f"0.{input_words[i + 8]}.{input_words[i + 6]}.{input_words[i + 1]}")
													output.append(f"0.{input_words[i + 8]}.{input_words[i + 6]}.{input_words[i + 4]}")
													return output, i + 10
												# điểm a và điểm b khoản 1 Điều 1 Chương 1
												elif input_words[i + 10].isnumeric():
													output.append(f"{input_words[i + 10]}.{input_words[i + 8]}.{input_words[i + 6]}.{input_words[i + 1]}")
													output.append(f"{input_words[i + 10]}.{input_words[i + 8]}.{input_words[i + 6]}.{input_words[i + 4]}")
													return output, i + 10
												# điểm a và điểm b khoản 1 Điều 1 Chương I
												elif is_roman(input_words[i + 10]) and input_words[i + 10].isupper():
													output.append(f"{roman_to_int(input_words[i + 10])}.{input_words[i + 8]}.{input_words[i + 6]}.{input_words[i + 1]}")
													output.append(f"{roman_to_int(input_words[i + 10])}.{input_words[i + 8]}.{input_words[i + 6]}.{input_words[i + 4]}")
													return output, i + 10
											# điểm a và điểm b khoản 1 Điều 1 abcxyz ...
											elif input_words[i + 9] != "Chương":
												output.append(f"0.{input_words[i + 8]}.{input_words[i + 6]}.{input_words[i + 1]}")
												output.append(f"0.{input_words[i + 8]}.{input_words[i + 6]}.{input_words[i + 4]}")
												return output, i + 9
					# điểm a abcxyz ...
					elif len(input_words[i + 1]) == 1 and input_words[i + 2] != "và" and input_words[i + 2] != "khoản":
						output.append(f"0.{index_list[1]}.{index_list[2]}.{input_words[i + 1]}")
						return output, i + 2
				
				# điểm a, ...
				elif input_words[i + 1][0].isalpha() and input_words[i + 1][-1] == ",":
					point_list = []
					j = 0
					while input_words[i + j + 1][-1] == "," and input_words[i + j + 1][0].isalpha():
						point_list.append(input_words[i + j + 1][0])
						j += 1
					# điểm a, b, c ...
					if input_words[i + j + 1].isalpha():
						point_list.append(input_words[i + j + 1])
						# điểm a, b, c và ...
						if input_words[i + j + 2] == "và":
							# điểm a, b, c và đ ...
							if input_words[i + j + 3].isalpha():
								point_list.append(input_words[i + j + 3])
								# điểm a, b, c và đ khoản ...
								if input_words[i + j + 4] == "khoản":
									# điểm a, b, c và đ khoản này
									if input_words[i + j + 5] == "này":
										for point in point_list:
											output.append(f"0.{index_list[1]}.{index_list[2]}.{point}")
										return output, i + j + 5
									# điểm a, b, c và đ khoản 1 ...
									elif input_words[i + j + 5].isnumeric():
										# điểm a, b, c và đ khoản 1 Điều ...
										if input_words[i + j + 6] == "Điều":
											# điểm a, b, c và đ khoản 1 Điều này
											if input_words[i + j + 7] == "này":
												for point in point_list:
													output.append(f"0.{index_list[1]}.{input_words[i + j + 5]}.{point}")
												return output, i + j + 7
											# điểm a, b, c và đ khoản 1 Điều 1 ...
											elif input_words[i + j + 7].isnumeric():
												# điểm a, b, c và đ khoản 1 Điều 1 Chương ...
												if input_words[i + j + 8] == "Chương":
													# điểm a, b, c và đ khoản 1 Điều 1 Chương này
													if input_words[i + j + 9] == "này":
														for point in point_list:
															output.append(f"0.{input_words[i + j + 7]}.{input_words[i + j + 5]}.{point}")
														return output, i + j + 9
													# điểm a, b, c và đ khoản 1 Điều 1 Chương 1
													elif input_words[i + j + 9].isnumeric():
														for point in point_list:
															output.append(f"{input_words[i + j + 9]}.{input_words[i + j + 7]}.{input_words[i + j + 5]}.{point}")
														return output, i + j + 9
													# điểm a, b, c và đ khoản 1 Điều 1 Chương I
													elif is_roman(input_words[i + j + 9]) and input_words[i + j + 9].isupper():
														for point in point_list:
															output.append(f"{roman_to_int(input_words[i + j + 9])}.{input_words[i + j + 7]}.{input_words[i + j + 5]}.{point}")
														return output, i + j + 9
												# điểm a, b, c và đ khoản 1 Điều 1 abcxyz ...
												elif input_words[i + j + 8] != "Chương":
													for point in point_list:
														output.append(f"0.{input_words[i + j + 7]}.{input_words[i + j + 5]}.{point}")
													return output, i + j + 8

		# điểm ...
		if input_words[i].lower() == "điểm":
			# if i + 1 not out of range
			if i + 1 < input_length:
				# điểm này
				if input_words[i + 1] == "này":
					output.append(f"0.{index_list[1]}.{index_list[2]}.{index_list[3]}")
					return output, i + 1
				# điểm 1 ...
				elif input_words[i + 1].isnumeric():
					# điểm 1 khoản ...
					if input_words[i + 2] == "khoản":
						# điểm 1 khoản này
						if input_words[i + 3] == "này":
							output.append(f"0.{index_list[1]}.{index_list[2]}.{input_words[i + 1]}")
							return output, i + 3
						# điểm 1 khoản 1 ...
						elif input_words[i + 3].isnumeric():
							# điểm 1 khoản 1 Điều ...
							if input_words[i + 4] == "Điều":
								# điểm 1 khoản 1 Điều này
								if input_words[i + 5] == "này":
									output.append(f"0.{index_list[1]}.{input_words[i + 3]}.{input_words[i + 1]}")
									return output, i + 5
								# điểm 1 khoản 1 Điều 1 ...
								elif input_words[i + 5].isnumeric():
									# điểm 1 khoản 1 Điều 1 Chương ...
									if input_words[i + 6] == "Chương":
										# điểm 1 khoản 1 Điều 1 Chương này
										if input_words[i + 7] == "này":
											output.append(f"0.{input_words[i + 5]}.{input_words[i + 3]}.{input_words[i + 1]}")
											return output, i + 7
										# điểm 1 khoản 1 Điều 1 Chương 1
										elif input_words[i + 7].isnumeric():
											output.append(f"{input_words[i + 7]}.{input_words[i + 5]}.{input_words[i + 3]}.{input_words[i + 1]}")
											return output, i + 7
										# điểm 1 khoản 1 Điều 1 Chương I
										elif is_roman(input_words[i + 7]) and input_words[i + 7].isupper():
											output.append(f"{roman_to_int(input_words[i + 7])}.{input_words[i + 5]}.{input_words[i + 3]}.{input_words[i + 1]}")
											return output, i + 7
									# điểm 1 khoản 1 Điều 1 abcxyz ...
									elif input_words[i + 6] != "Chương":
										output.append(f"0.{input_words[i + 5]}.{input_words[i + 3]}.{input_words[i + 1]}")
										return output, i + 6
								# điểm 1 khoản 1 Điều 1,
								elif input_words[i + 5][-1] == "," and input_words[i + 5][:-1].isnumeric():
									output.append(f"0.{input_words[i + 5][:-1]}.{input_words[i + 3]}.{input_words[i + 1]}")
									return output, i + 5
					# điểm 1 và điểm ...
					elif input_words[i + 2] == "và" and input_words[i + 3] == "điểm":
						# điểm 1 và điểm 2 ...
						if input_words[i + 4].isnumeric():
							# điểm 1 và điểm 2 khoản ...
							if input_words[i + 5] == "khoản":
								# điểm 1 và điểm 2 khoản này
								if input_words[i + 6] == "này":
									output.append(f"0.{index_list[1]}.{index_list[2]}.{input_words[i + 1]}")
									output.append(f"0.{index_list[1]}.{index_list[2]}.{input_words[i + 4]}")
									return output, i + 6
								# điểm 1 và điểm 2 khoản 1 ...
								elif input_words[i + 6].isnumeric():
									# điểm 1 và điểm 2 khoản 1 Điều ...
									if input_words[i + 7] == "Điều":
										# điểm 1 và điểm 2 khoản 1 Điều này
										if input_words[i + 8] == "này":
											output.append(f"0.{index_list[1]}.{input_words[i + 6]}.{input_words[i + 1]}")
											output.append(f"0.{index_list[1]}.{input_words[i + 6]}.{input_words[i + 4]}")
											return output, i + 8
										# điểm 1 và điểm 2 khoản 1 Điều 1 ...
										elif input_words[i + 8].isnumeric():
											# điểm 1 và điểm 2 khoản 1 Điều 1 Chương ...
											if input_words[i + 9] == "Chương":
												# điểm 1 và điểm 2 khoản 1 Điều 1 Chương này
												if input_words[i + 10] == "này":
													output.append(f"0.{input_words[i + 8]}.{input_words[i + 6]}.{input_words[i + 1]}")
													output.append(f"0.{input_words[i + 8]}.{input_words[i + 6]}.{input_words[i + 4]}")
													return output, i + 10
												# điểm 1 và điểm 2 khoản 1 Điều 1 Chương 1
												elif input_words[i + 10].isnumeric():
													output.append(f"{input_words[i + 10]}.{input_words[i + 8]}.{input_words[i + 6]}.{input_words[i + 1]}")
													output.append(f"{input_words[i + 10]}.{input_words[i + 8]}.{input_words[i + 6]}.{input_words[i + 4]}")
													return output, i + 10
												# điểm 1 và điểm 2 khoản 1 Điều 1 Chương I
												elif is_roman(input_words[i + 10]) and input_words[i + 10].isupper():
													output.append(f"{roman_to_int(input_words[i + 10])}.{input_words[i + 8]}.{input_words[i + 6]}.{input_words[i + 1]}")
													output.append(f"{roman_to_int(input_words[i + 10])}.{input_words[i + 8]}.{input_words[i + 6]}.{input_words[i + 4]}")
													return output, i + 10
											# điểm 1 và điểm 2 khoản 1 Điều 1 abcxyz ...
											elif input_words[i + 9] != "Chương":
												output.append(f"0.{input_words[i + 8]}.{input_words[i + 6]}.{input_words[i + 1]}")
												output.append(f"0.{input_words[i + 8]}.{input_words[i + 6]}.{input_words[i + 4]}")
												return output, i + 9
					# điểm 1 abcxyz ...
					elif input_words[i + 2] != "và" and input_words[i + 2] != "khoản":
						output.append(f"0.{index_list[1]}.{index_list[2]}.{input_words[i + 1]}")
						return output, i + 2
					
				# điểm 1, ...
				elif input_words[i + 1][0].isnumeric() and input_words[i + 1][-1] == ",":
					point_list = []
					j = 0
					while input_words[i + j + 1][-1] == "," and input_words[i + j + 1][:-1].isnumeric():
						point_list.append(input_words[i + j + 1][:-1])
						j += 1
					# điểm 1, 2, 3 ...
					if input_words[i + j + 1].isnumeric():
						point_list.append(input_words[i + j + 1])
						# điểm 1, 2, 3 và ...
						if input_words[i + j + 2] == "và":
							# điểm 1, 2, 3 và 4 ...
							if input_words[i + j + 3].isnumeric():
								point_list.append(input_words[i + j + 3])
								# điểm 1, 2, 3 và 4 khoản ...
								if input_words[i + j + 4] == "khoản":
									# điểm 1, 2, 3 và 4 khoản này
									if input_words[i + j + 5] == "này":
										for point in point_list:
											output.append(f"0.{index_list[1]}.{index_list[2]}.{point}")
										return output, i + j + 5
									# điểm 1, 2, 3 và 4 khoản 1 ...
									elif input_words[i + j + 5].isnumeric():
										# điểm 1, 2, 3 và 4 khoản 1 Điều ...
										if input_words[i + j + 6] == "Điều":
											# điểm 1, 2, 3 và 4 khoản 1 Điều này
											if input_words[i + j + 7] == "này":
												for point in point_list:
													output.append(f"0.{index_list[1]}.{input_words[i + j + 5]}.{point}")
												return output, i + j + 7
											# điểm 1, 2, 3 và 4 khoản 1 Điều 1 ...
											elif input_words[i + j + 7].isnumeric():
												# điểm 1, 2, 3 và 4 khoản 1 Điều 1 Chương ...
												if input_words[i + j + 8] == "Chương":
													# điểm 1, 2, 3 và 4 khoản 1 Điều 1 Chương này
													if input_words[i + j + 9] == "này":
														for point in point_list:
															output.append(f"0.{input_words[i + j + 7]}.{input_words[i + j + 5]}.{point}")
														return output, i + j + 9
													# điểm 1, 2, 3 và 4 khoản 1 Điều 1 Chương 1
													elif input_words[i + j + 9].isnumeric():
														for point in point_list:
															output.append(f"{input_words[i + j + 10]}.{input_words[i + j + 7]}.{input_words[i + j + 5]}.{point}")
														return output, i + j + 9
													# điểm 1, 2, 3 và 4 khoản 1 Điều 1 Chương I
													elif is_roman(input_words[i + j + 9]) and input_words[i + j + 9].isupper():
														for point in point_list:
															output.append(f"{roman_to_int(input_words[i + j + 9])}.{input_words[i + j + 7]}.{input_words[i + j + 5]}.{point}")
														return output, i + j + 9
												# điểm 1, 2, 3 và 4 khoản 1 Điều 1 abcxyz ...
												elif input_words[i + j + 8] != "Chương":
													for point in point_list:
														output.append(f"0.{input_words[i + j + 7]}.{input_words[i + j + 5]}.{point}")
													return output, i + j + 8
												
		# khoản ...
		elif input_words[i].lower() == "khoản":
			# if i + 1 not out of range
			if i + 1 < input_length:
				# khoản này
				if input_words[i + 1] == "này":
					output.append(f"0.{index_list[1]}.{index_list[2]}.0")
					return output, i + 1
				
				# khoản 1 ...
				elif input_words[i + 1].isnumeric():
					# khoản 1 Điều ...
					if input_words[i + 2] == "Điều":
						# khoản 1 Điều này
						if input_words[i + 3] == "này":
							output.append(f"0.{index_list[1]}.{input_words[i + 1]}.0")
							return output, i + 3
						# khoản 1 Điều 1 ...
						elif input_words[i + 3].isnumeric():
							# khoản 1 Điều 1 Chương ...
							if input_words[i + 4] == "Chương":
								# khoản 1 Điều 1 Chương này
								if input_words[i + 5] == "này":
									output.append(f"0.{input_words[i + 3]}.{input_words[i + 1]}.0")
									return output, i + 5
								# khoản 1 Điều 1 Chương 1
								elif input_words[i + 5].isnumeric():
									output.append(f"{input_words[i + 5]}.{input_words[i + 3]}.{input_words[i + 1]}.0")
									return output, i + 5
								# khoản 1 Điều 1 Chương I
								elif is_roman(input_words[i + 5]) and input_words[i + 5].isupper():
									output.append(f"{roman_to_int(input_words[i + 5])}.{input_words[i + 3]}.{input_words[i + 1]}.0")
									return output, i + 5
							# khoản 1 Điều 1 abcxyz ...
							elif input_words[i + 4] != "Chương":
								output.append(f"0.{input_words[i + 3]}.{input_words[i + 1]}.0")
								return output, i + 4
						# khoản 1 Điều 1,/. ...
						elif not input_words[i + 3][-1].isdigit() and input_words[i + 3][:-1].isnumeric():
							output.append(f"0.{input_words[i + 3][:-1]}.{input_words[i + 1]}.0")
							return output, i + 3
					# khoản 1 và điểm ...
					elif input_words[i + 2] == "và" and input_words[i + 3] == "điểm":
						for j in range(i + 4, input_length - 1):
							# khoản 1 và điểm ... Điều này ...
							if input_words[j] == "Điều" and input_words[j + 1] == "này":
								output.append(f"0.{index_list[1]}.{input_words[i + 1]}.0")
								return output, i + 1
							# khoản 1 và điểm ... Điều 1 ...
							elif input_words[j] == "Điều" and input_words[j + 1].isnumeric():
								# khoản 1 và điểm ... Điều 1 Chương ...
								if input_words[j + 2] == "Chương":
									# khoản 1 và điểm ... Điều 1 Chương này
									if input_words[j + 3] == "này":
										output.append(f"0.{input_words[j + 1]}.{input_words[i + 1]}.0")
										return output, i + 1
									# khoản 1 và điểm ... Điều 1 Chương 1
									elif input_words[j + 3].isnumeric():
										output.append(f"{input_words[j + 3]}.{input_words[j + 1]}.{input_words[i + 1]}.0")
										return output, i + 1
									# khoản 1 và điểm ... Điều 1 Chương I
									elif is_roman(input_words[j + 3]) and input_words[j + 3].isupper():
										output.append(f"{roman_to_int(input_words[j + 3])}.{input_words[j + 1]}.{input_words[i + 1]}.0")
										return output, i + 1
								# khoản 1 và điểm ... Điều 1 abcxyz ...
								elif input_words[j + 2] != "Chương":
									output.append(f"0.{input_words[j + 1]}.{input_words[i + 1]}.0")
									return output, i + 1
					# khoản 1 và khoản 2 ...
					elif input_words[i + 2] == "và" and input_words[i + 3] == "khoản":
						# khoản 1 và khoản 2 ...
						if input_words[i + 4].isnumeric():
							# khoản 1 và khoản 2 Điều ...
							if input_words[i + 5] == "Điều":
								# khoản 1 và khoản 2 Điều này
								if input_words[i + 6] == "này":
									output.append(f"0.{index_list[1]}.{input_words[i + 1]}.0")
									output.append(f"0.{index_list[1]}.{input_words[i + 4]}.0")
									return output, i + 6
								# khoản 1 và khoản 2 Điều 1 ...
								elif input_words[i + 6].isnumeric():
									# khoản 1 và khoản 2 Điều 1 Chương ...
									if input_words[i + 7] == "Chương":
										# khoản 1 và khoản 2 Điều 1 Chương này
										if input_words[i + 8] == "này":
											output.append(f"0.{input_words[i + 6]}.{input_words[i + 1]}.0")
											output.append(f"0.{input_words[i + 6]}.{input_words[i + 4]}.0")
											return output, i + 8
										# khoản 1 và khoản 2 Điều 1 Chương 1
										elif input_words[i + 8].isnumeric():
											output.append(f"{input_words[i + 8]}.{input_words[i + 6]}.{input_words[i + 1]}.0")
											output.append(f"{input_words[i + 8]}.{input_words[i + 6]}.{input_words[i + 4]}.0")
											return output, i + 8
										# khoản 1 và khoản 2 Điều 1 Chương I
										elif is_roman(input_words[i + 8]) and input_words[i + 8].isupper():
											output.append(f"{roman_to_int(input_words[i + 8])}.{input_words[i + 6]}.{input_words[i + 1]}.0")
											output.append(f"{roman_to_int(input_words[i + 8])}.{input_words[i + 6]}.{input_words[i + 4]}.0")
											return output, i + 8
									# khoản 1 và khoản 2 Điều 1 abcxyz ...
									elif input_words[i + 7] != "Chương":
										output.append(f"0.{input_words[i + 6]}.{input_words[i + 1]}.0")
										output.append(f"0.{input_words[i + 6]}.{input_words[i + 4]}.0")
										return output, i + 7
								# khoản 1 và khoản 2 Điều 1, ...
								elif input_words[i + 6][-1] == "," and input_words[i + 6][:-1].isnumeric():
									output.append(f"0.{input_words[i + 6][:-1]}.{input_words[i + 1]}.0")
									output.append(f"0.{input_words[i + 6][:-1]}.{input_words[i + 4]}.0")
									return output, i + 6						
					# khoản 1 abcxyz ...
					elif input_words[i + 2] != "và" and input_words[i + 2] != "khoản":
						output.append(f"0.{index_list[1]}.{input_words[i + 1]}.0")
						return output, i + 2
					
				# khoản 1, ...
				elif input_words[i + 1][:-1].isnumeric() and input_words[i + 1][-1] == ",":
					point_list = []
					j = 0
					while input_words[i + j + 1][-1] == "," and input_words[i + j + 1][:-1].isnumeric():
						point_list.append(input_words[i + j + 1][:-1])
						j += 1
					# khoản 1, 2, 3 ...
					if input_words[i + j + 1].isnumeric():
						point_list.append(input_words[i + j + 1])
						# khoản 1, 2, 3 và ...
						if input_words[i + j + 2] == "và":
							# khoản 1, 2, 3 và 4 ...
							if input_words[i + j + 3].isnumeric():
								point_list.append(input_words[i + j + 3])
								# khoản 1, 2, 3 và 4 Điều ...
								if input_words[i + j + 4] == "Điều":
									# khoản 1, 2, 3 và 4 Điều này
									if input_words[i + j + 5] == "này":
										for point in point_list:
											output.append(f"0.{index_list[1]}.{point}.0")
										return output, i + j + 5
									# khoản 1, 2, 3 và 4 Điều 1 ...
									elif input_words[i + j + 5].isnumeric():
										# khoản 1, 2, 3 và 4 Điều 1 Chương ...
										if input_words[i + j + 6] == "Chương":
											# khoản 1, 2, 3 và 4 Điều 1 Chương này
											if input_words[i + j + 7] == "này":
												for point in point_list:
													output.append(f"0.{input_words[i + j + 5]}.{point}.0")
												return output, i + j + 7
											# khoản 1, 2, 3 và 4 Điều 1 Chương 1
											elif input_words[i + j + 7].isnumeric():
												for point in point_list:
													output.append(f"{input_words[i + j + 7]}.{input_words[i + j + 5]}.{point}.0")
												return output, i + j + 7
											# khoản 1, 2, 3 và 4 Điều 1 Chương I
											elif is_roman(input_words[i + j + 7]) and input_words[i + j + 7].isupper():
												for point in point_list:
													output.append(f"{roman_to_int(input_words[i + j + 7])}.{input_words[i + j + 5]}.{point}.0")
												return output, i + j + 7
										# khoản 1, 2, 3 và 4 Điều 1 abcxyz ...
										elif input_words[i + j + 6] != "Chương":
											for point in point_list:
												output.append(f"0.{input_words[i + j + 5]}.{point}.0")
											return output, i + j + 6
							# khoản 1, 2, 3 và điểm ...
							if input_words[i + j + 3] == "điểm":
								for k in range(i + j + 4, input_length - 1):
									# khoản 1, 2, 3 và điểm ... Điều này ...
									if input_words[k] == "Điều" and input_words[k + 1] == "này":
										for point in point_list:
											output.append(f"0.{index_list[1]}.{point}.0")
										return output, i + j + 1
									# khoản 1, 2, 3 và điểm ... Điều 1 ...
									elif input_words[k] == "Điều" and input_words[k + 1].isnumeric():
										# khoản 1, 2, 3 và điểm ... Điều 1 Chương ...
										if input_words[k + 2] == "Chương":
											# khoản 1, 2, 3 và điểm ... Điều 1 Chương này
											if input_words[k + 3] == "này":
												for point in point_list:
													output.append(f"0.{input_words[k + 1]}.{point}.0")
												return output, i + j + 1
											# khoản 1, 2, 3 và điểm ... Điều 1 Chương 1
											elif input_words[k + 3].isnumeric():
												for point in point_list:
													output.append(f"{input_words[k + 3]}.{input_words[k + 1]}.{point}.0")
												return output, i + j + 1
											# khoản 1, 2, 3 và điểm ... Điều 1 Chương I
											elif is_roman(input_words[k + 3]) and input_words[k + 3].isupper():
												for point in point_list:
													output.append(f"{roman_to_int(input_words[k + 3])}.{input_words[k + 1]}.{point}.0")
												return output, i + j + 1
										# khoản 1, 2, 3 và điểm ... Điều 1 abcxyz ...
										elif input_words[k + 2] != "Chương":
											for point in point_list:
												output.append(f"0.{input_words[k + 1]}.{point}.0")
											return output, i + j + 1
										
		# điều ...
		elif input_words[i].lower() == "điều":
			# if i + 1 not out of range
			if i + 1 < input_length:
				# điều này
				if input_words[i + 1] == "này":
					output.append(f"0.{index_list[1]}.0.0")
					return output, i + 1
				
				# điều 1 ...
				elif input_words[i + 1].isnumeric():
					# if i + 2 not out of range
					if i + 2 < input_length:
						# điều 1 Chương ...
						if input_words[i + 2] == "Chương":
							# điều 1 Chương này
							if input_words[i + 3] == "này":
								output.append(f"0.{input_words[i + 1]}.0.0")
								return output, i + 3
							# điều 1 Chương 1
							elif input_words[i + 3].isnumeric():
								output.append(f"{input_words[i + 3]}.{input_words[i + 1]}.0.0")
								return output, i + 3
							# điều 1 Chương I
							elif is_roman(input_words[i + 3]) and input_words[i + 3].isupper():
								output.append(f"{roman_to_int(input_words[i + 3])}.{input_words[i + 1]}.0.0")
								return output, i + 3
						# điều 1 abcxyz ...
						elif input_words[i + 2] != "Chương":
							output.append(f"0.{input_words[i + 1]}.0.0")
							return output, i + 2
					# if i + 2 out of range
					else:
						output.append(f"0.{input_words[i + 1]}.0.0")
						return output, i + 1
				
				# điều 1, ...
				elif input_words[i + 1][:-1].isnumeric() and input_words[i + 1][-1] == ",":
					point_list = []
					j = 0
					while input_words[i + j + 1][-1] == "," and input_words[i + j + 1][:-1].isnumeric():
						point_list.append(input_words[i + j + 1][:-1])
						j += 1
					# điều 1, 2, 3 ...
					if input_words[i + j + 1].isnumeric():
						point_list.append(input_words[i + j + 1])
						# điều 1, 2, 3 và ...
						if input_words[i + j + 2] == "và":
							# điều 1, 2, 3 và 4 ...
							if input_words[i + j + 3].isnumeric():
								point_list.append(input_words[i + j + 3])
								# điều 1, 2, 3 và 4 Chương ...
								if input_words[i + j + 4] == "Chương":
									# điều 1, 2, 3 và 4 Chương này
									if input_words[i + j + 5] == "này":
										for point in point_list:
											output.append(f"0.{point}.0.0")
										return output, i + j + 5
									# điều 1, 2, 3 và 4 Chương 1
									elif input_words[i + j + 5].isnumeric():
										for point in point_list:
											output.append(f"{input_words[i + j + 5]}.{point}.0.0")
										return output, i + j + 5
									# điều 1, 2, 3 và 4 Chương I
									elif is_roman(input_words[i + j + 5]) and input_words[i + j + 5].isupper():
										for point in point_list:
											output.append(f"{roman_to_int(input_words[i + j + 5])}.{point}.0.0")
										return output, i + j + 5
								# điều 1, 2, 3 và 4 abcxyz ...
								elif input_words[i + j + 4] != "Chương":
									for point in point_list:
										output.append(f"0.{point}.0.0")
									return output, i + j + 4
							# điều 1, 2, 3 và 4, ...
							if input_words[i + j + 3][-1] == "," and input_words[i + j + 3][:-1].isnumeric():
								point_list.append(input_words[i + j + 3][:-1])
								for point in point_list:
									output.append(f"0.{point}.0.0")
								return output, i + j + 3
		
		# chương ...
		elif input_words[i].lower() == "chương":
			# if i + 1 not out of range
			if i + 1 < input_length:
				# chương này
				if input_words[i + 1] == "này":
					output.append(f"0.0.0.0")
					return output, i + 1
				
				# chương 1 ...
				elif input_words[i + 1].isnumeric():
					output.append(f"{input_words[i + 1]}.0.0.0")
					return output, i + 1
				
				# chương I ...
				elif is_roman(input_words[i + 1]) and input_words[i + 1].isupper():
					output.append(f"{roman_to_int(input_words[i + 1])}.0.0.0")
					return output, i + 1
	
	return output, input_length

def extract_reference_from_txt(input_paragraph: str, cur_index: str) -> List:
	res = []
	start_index = 0
	while True:
		reference, start_index = extract_reference_point(input_paragraph, cur_index, start_index)
		if len(reference) == 0:
			break
		res += reference
		start_index += 1
	return res
		
if __name__ == "__main__":
	pattern = [
		"2. Bổ sung điểm 11 và điểm 12 Điều 3 như sau: \"11. Người điều hành là tổ chức, cá nhân đại diện cho các bên tham gia hợp đồng dầu khí, điều hành các hoạt động trong phạm vi được uỷ quyền.  2. Đối tượng của hợp đồng; 2. Nhà thầu là tổ chức, cá nhân nước ngoài được mở tài khoản tại Việt Nam và nước ngoài; được chuyển thu nhập từ việc bán dầu khí thuộc phần thu hồi chi phí, lợi nhuận và các thu nhập hợp pháp khác thu được trong quá trình hoạt động dầu khí ra nước ngoài.  2. Thực hiện các cam kết ghi trong hợp đồng dầu khí;"
	]
	for text in pattern:
		print(extract_reference_from_txt(text, "0.1.2.0"))