import re
import docx
import json
from . import utils
from . import config

class DocumentHandler:
	def __init__(self, file_path):
		self.file_path = file_path
		self.file_name = file_path.split("/")[-1][:-5]
		self.document = docx.Document(self.file_path)
		
	def init_index(self):
		self.index = {
			"document" : []
        }
		for para in self.document.paragraphs:
			if para.text != '\xa0':
				self.index["document"].append({
					"index" : "0.0.0.0",
					"text" : para.text
				})
    
	def index_document(self):
		self.init_index()
		document_data = self.index["document"]
		document_data_len = len(document_data)

		for i in range(1, document_data_len):
			previous_element_index_list = document_data[i-1]["index"].split(".")

			previous_element_chapter_number = int(previous_element_index_list[0])
			previous_element_section_number = int(previous_element_index_list[1])
			previous_element_subsection_number = int(previous_element_index_list[2])
			previous_element_point_number = previous_element_index_list[3]
			element = document_data[i]
			# if element["text"] starts with "Chương" then it is a chapter, update the index
			if element["text"].startswith("Chương"):
				second_element = element["text"].split()[1]
				if (second_element[0] in ['I', 'V', 'X', 'L', 'C', 'D', 'M']):
					# if first character is a number then it is a chapter
				# chapter number is the first word right after "Chương"
					chapter_number = element["text"].split()[1]
					# right now the chapter number is roman numeral, convert it to arabic numeral
					chapter_number = utils.roman_to_int(chapter_number)
					# update the index
					index_list = element["index"].split(".")
					index_list[0] = str(chapter_number)
					element["index"] = ".".join(index_list)
			elif element["text"].startswith("Điều") and element["text"].split()[1][0].isdigit():
				# section number is the first word right after "Điều", remove the dot at the end
				section_number = element["text"].split()[1][:-1]
				# update the index
				index_list = element["index"].split(".")
				index_list[0] = str(previous_element_chapter_number)
				index_list[1] = section_number
				element["index"] = ".".join(index_list)
			# else if element["text"] starts with a number and a dot then it is a subsection, update the index
			elif re.match(r"^\d+\.", element["text"]):
				# subsection number is the first word, remove the dot at the end
				subsection_number = element["text"].split(".")[0]
				# update the index
				index_list = element["index"].split(".")
				index_list[2] = subsection_number
				index_list[1] = str(previous_element_section_number)
				index_list[0] = str(previous_element_chapter_number)
				element["index"] = ".".join(index_list)
			# else if element["text"] starts with a character and a ) then it is a point, update the index
			elif re.match(r"^[a-zđê]\)", element["text"], re.IGNORECASE):
				# point number is the first character, remove the bracket at the end
				point_number = element["text"].split(")")[0]
				# update the index
				index_list = element["index"].split(".")
				index_list[3] = point_number
				index_list[2] = str(previous_element_subsection_number)
				index_list[1] = str(previous_element_section_number)
				index_list[0] = str(previous_element_chapter_number)
				element["index"] = ".".join(index_list)
			else:
				index_list = element["index"].split(".")
				index_list[0] = str(previous_element_chapter_number)
				index_list[1] = str(previous_element_section_number)
				if previous_element_section_number != 0 and previous_element_subsection_number == 0:
					index_list[2] = "1"
				elif previous_element_subsection_number != 0 and previous_element_point_number == 0:
					index_list[2] = str(previous_element_subsection_number)
					index_list[3] = str(previous_element_point_number)
				elif previous_element_point_number != 0:
					index_list[2] = str(previous_element_subsection_number)
					index_list[3] = str(previous_element_point_number)
				element["index"] = ".".join(index_list)
		# merge values of the same index
		for i in range(1, document_data_len):
			if document_data[i]["index"] == document_data[i-1]["index"]:
				document_data[i-1]["text"] += "\n" + document_data[i]["text"]
				document_data[i]["text"] = ""
		# remove empty elements
		document_data = [element for element in document_data if element["text"] != ""]

		self.index["document"] = document_data
		index_dict = {}
		for element in document_data:
			if element["index"] not in index_dict:
				index_dict[element["index"]] = element["text"]
			else:
				index_dict[element["index"]] += "\n" + element["text"]
		self.index["document"] = index_dict

	def save_index(self):
		# save document_data to json file
		self.index_document()
		with open(config.OUTPUT_INDEX_PATH + self.file_name + '_indexed.json', 'w', encoding="utf-8") as json_file:
			# json.dump(document_json, json_file, indent=4, ensure_ascii=False)
			json.dump(self.index, json_file, indent = 4, ensure_ascii = False)