from unidecode import unidecode
from typing import List
from . import utils, config

def is_roman(s: str):
	"""
		Check if the input string is a Roman numeral.

		Parameters:
			s (str): The input string.

		Returns:
			bool: True if the input string is a Roman numeral, False otherwise.
		
		Example:
			>>> is_roman('III')
			True
	"""
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

def valid_article(s: str) -> bool:
	"""
		Check whether the input string is a valid article.
	"""
	if s[0].isalpha():
		return False
	elif any(not char.isalnum() for char in s):
		return False
	else:
		return True

def extract_reference_point(input_paragraph: str, input_index: str, start_index: int):
	"""
		Extract the reference point from a paragraph.

		Parameters:
			input_paragraph (str): The input paragraph.
			input_index (str): The input index.
			start_index (int): The start index.
		
		Returns:
			list: The list of reference points extracted from the paragraph.
			int: The end index.

		Example:
			>>> extract_reference_point("Chính phủ quy định điểm a khoản 1 Điều 1 Chương 1")
			(['1.1.1.a'])
			>>> extract_reference_point("Chính phủ quy định điểm a khoản 1 Điều 1")
			(['0.1.1.a'])
	"""
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
				if "này" in input_words[i + 1]:
					output.append(f"0.{index_list[1]}.{index_list[2]}.{index_list[3]}")
					return output, i + 1
				# điểm a/1 ...
				elif input_words[i + 1].isalnum() and len(input_words[i + 1]) == 1:
					# điểm a/1 khoản ...
					if input_words[i + 2].lower() == "khoản":
						# điểm a/1 khoản này
						if "này" in input_words[i + 3]:
							output.append(f"0.{index_list[1]}.{index_list[2]}.{input_words[i + 1]}")
							return output, i + 3
						# điểm a/1 khoản a/1 ...
						elif input_words[i + 3].isalnum():
							# if i + 4 not out of range
							if i + 4 < input_length:
								# điểm a/1 khoản a/1 Điều ...
								if input_words[i + 4].lower() == "điều":
									# điểm a/1 khoản a/1 Điều này
									if "này" in input_words[i + 5]:
										output.append(f"0.{index_list[1]}.{input_words[i + 3]}.{input_words[i + 1]}")
										return output, i + 5
									# điểm a/1 khoản a/1 Điều a/1 ...
									elif input_words[i + 5].isalnum():
										# if i + 6 not out of range
										if i + 6 < input_length:
											# điểm a/1 khoản a/1 Điều a/1 Chương ...
											if input_words[i + 6].lower() == "chương":
												# điểm a/1 khoản a/1 Điều a/1 Chương này
												if "này" in input_words[i + 7]:
													output.append(f"0.{input_words[i + 5]}.{input_words[i + 3]}.{input_words[i + 1]}")
													return output, i + 7
												# điểm a/1 khoản a/1 Điều a/1 Chương 1
												elif input_words[i + 7].isnumeric():
													output.append(f"{input_words[i + 7]}.{input_words[i + 5]}.{input_words[i + 3]}.{input_words[i + 1]}")
													return output, i + 7
												# điểm a/1 khoản a/1 Điều a/1 Chương 1./,
												elif input_words[i + 7][0].isnumeric() and not input_words[i + 7][-1].isalnum():
													output.append(f"{input_words[i + 7][:-1]}.{input_words[i + 5]}.{input_words[i + 3]}.{input_words[i + 1]}")
													return output, i + 7
												# điểm a/1 khoản a/1 Điều a/1 Chương I
												elif is_roman(input_words[i + 7]):
													output.append(f"{roman_to_int(input_words[i + 7])}.{input_words[i + 5]}.{input_words[i + 3]}.{input_words[i + 1]}")
													return output, i + 7
												# điểm a/1 khoản a/1 Điều a/1 Chương I./,
												elif is_roman(input_words[i + 7][0]) and not input_words[i + 7][-1].isalnum():
													output.append(f"{roman_to_int(input_words[i + 7][:-1])}.{input_words[i + 5]}.{input_words[i + 3]}.{input_words[i + 1]}")
													return output, i + 7
											# điểm a/1 khoản a/1 Điều a/1 abcxyz ...
											elif input_words[i + 6].lower() != "chương":
												output.append(f"0.{input_words[i + 5]}.{input_words[i + 3]}.{input_words[i + 1]}")
												return output, i + 5
										# if i + 6 out of range
										else:
											output.append(f"0.{input_words[i + 5]}.{input_words[i + 3]}.{input_words[i + 1]}")
											return output, i + 5
									# điểm a/1 khoản a/1 Điều a/1,
									elif not valid_article(input_words[i + 5]) and valid_article(input_words[i + 5][:-1]):
										output.append(f"0.{input_words[i + 5][:-1]}.{input_words[i + 3]}.{input_words[i + 1]}")
										return output, i + 5
								# điểm a/1 khoản a/1 abcxyz
								elif input_words[i + 4].lower() != "điều":
									output.append(f"0.{index_list[1]}.{input_words[i + 3]}.{input_words[i + 1]}")
									return output, i + 3
							# if i + 4 out of range
							else:
								output.append(f"0.{index_list[1]}.{input_words[i + 3]}.{input_words[i + 1]}")
								return output, i + 3
						# điểm a/1 khoản a/1, ...
						elif not input_words[i + 3][-1].isalnum() and input_words[i + 3][:-1].isalnum():
							# điểm a/1 khoản a/1, ... Điều ...
							for j in range(i + 3, input_length - 1):
								if input_words[j].lower() == "điều":
									# điểm a/1 khoản a/1, ... Điều này ...
									if "này" in input_words[j + 1]:
										output.append(f"0.{index_list[1]}.{input_words[i + 3]}.{input_words[i + 1]}")
										return output, i + 3
									# điểm a/1 khoản a/1, ... Điều a/1 ...
									elif valid_article(input_words[j + 1]):
										# điểm a/1 khoản a/1, ... Điều a/1 Chương
										if input_words[j + 2].lower() == "chương":
											# điểm a/1 khoản a/1, ... Điều a/1 Chương 1
											if input_words[j + 3].isnumeric():
												output.append(f"{input_words[j + 3]}.{input_words[j + 1]}.{input_words[i + 3]}.{input_words[i + 1]}")
												return output, i + 3
											# điểm a/1 khoản a/1, ... Điều a/1 Chương 1./,
											if input_words[j + 3][0].isnumeric() and not input_words[j + 3][-1].isalnum():
												output.append(f"{input_words[j + 3][:-1]}.{input_words[j + 1]}.{input_words[i + 3]}.{input_words[i + 1]}")
												return output, i + 3
											# điểm a/1 khoản a/1, ... Điều a/1 Chương I
											if is_roman(input_words[j + 3]):
												output.append(f"{roman_to_int(input_words[j + 3])}.{input_words[j + 1]}.{input_words[i + 3]}.{input_words[i + 1]}")
												return output, i + 3
											# điểm a/1 khoản a/1, ... Điều a/1 Chương I./,
											if is_roman(input_words[j + 3][0]) and not input_words[j + 3][-1].isalnum():
												output.append(f"{roman_to_int(input_words[j + 3][:-1])}.{input_words[j + 1]}.{input_words[i + 3]}.{input_words[i + 1]}")
												return output, i + 3
										# điểm a/1 khoản a/1, ... Điều a/1 abcxyz
										elif input_words[j + 2].lower() != "chương":
											output.append(f"0.{input_words[j + 1]}.{input_words[i + 3]}.{input_words[i + 1]}")
											return output, i + 3
									# điểm a/1 khoản a/1, ... Điều a/1, ...
									elif not valid_article(input_words[j + 1]) and valid_article(input_words[j + 1][:-1]):
										output.append(f"0.{input_words[j + 1][:-1]}.{input_words[i + 3]}.{input_words[i + 1]}")
										return output, i + 3
							# điểm a/1 khoản a/1, ... abcxyz ...
							output.append(f"0.{index_list[1]}.{input_words[i + 3]}.{input_words[i + 1]}")
							return output, i + 3
					# điểm a/1 và điểm ...
					elif input_words[i + 2] == "và" and input_words[i + 3] == "điểm":
						# điểm a/1 và điểm b/2 ...
						if input_words[i + 4].isalnum():
							# điểm a/1 và điểm b/2 khoản ...
							if input_words[i + 5].lower() == "khoản":
								# điểm a/1 và điểm b/2 khoản này
								if "này" in input_words[i + 6]:
									output.append(f"0.{index_list[1]}.{index_list[2]}.{input_words[i + 1]}")
									output.append(f"0.{index_list[1]}.{index_list[2]}.{input_words[i + 4]}")
									return output, i + 6
								# điểm a/1 và điểm b/2 khoản a/1 ...
								elif input_words[i + 6].isalnum():
									# điểm a/1 và điểm b/2 khoản a/1 Điều ...
									if input_words[i + 7].lower() == "điều":
										# điểm a/1 và điểm b/2 khoản a/1 Điều này
										if "này" in input_words[i + 8]:
											output.append(f"0.{index_list[1]}.{input_words[i + 6]}.{input_words[i + 1]}")
											output.append(f"0.{index_list[1]}.{input_words[i + 6]}.{input_words[i + 4]}")
											return output, i + 8
										# điểm a/1 và điểm b/2 khoản a/1 Điều a/1 ...
										elif valid_article(input_words[i + 8]):
											# if i + 9 not out of range
											if i + 9 < input_length:
												# điểm a/1 và điểm b/2 khoản a/1 Điều a/1 Chương ...
												if input_words[i + 9].lower() == "chương":
													# điểm a/1 và điểm b/2 khoản a/1 Điều a/1 Chương này
													if "này" in input_words[i + 10]:
														output.append(f"0.{input_words[i + 8]}.{input_words[i + 6]}.{input_words[i + 1]}")
														output.append(f"0.{input_words[i + 8]}.{input_words[i + 6]}.{input_words[i + 4]}")
														return output, i + 10
													# điểm a/1 và điểm b/2 khoản a/1 Điều a/1 Chương 1
													elif input_words[i + 10].isnumeric():
														output.append(f"{input_words[i + 10]}.{input_words[i + 8]}.{input_words[i + 6]}.{input_words[i + 1]}")
														output.append(f"{input_words[i + 10]}.{input_words[i + 8]}.{input_words[i + 6]}.{input_words[i + 4]}")
														return output, i + 10
													# điểm a/1 và điểm b/2 khoản a/1 Điều a/1 Chương 1./,
													elif input_words[i + 10][0].isnumeric() and not input_words[i + 10][-1].isalnum():
														output.append(f"{input_words[i + 10][:-1]}.{input_words[i + 8]}.{input_words[i + 6]}.{input_words[i + 1]}")
														output.append(f"{input_words[i + 10][:-1]}.{input_words[i + 8]}.{input_words[i + 6]}.{input_words[i + 4]}")
														return output, i + 10												
													# điểm a/1 và điểm b/2 khoản a/1 Điều a/1 Chương I
													elif is_roman(input_words[i + 10]):
														output.append(f"{roman_to_int(input_words[i + 10])}.{input_words[i + 8]}.{input_words[i + 6]}.{input_words[i + 1]}")
														output.append(f"{roman_to_int(input_words[i + 10])}.{input_words[i + 8]}.{input_words[i + 6]}.{input_words[i + 4]}")
														return output, i + 10
													# điểm a/1 và điểm b/2 khoản a/1 Điều a/1 Chương I./,
													elif is_roman(input_words[i + 10][0]) and not input_words[i + 10][-1].isalnum():
														output.append(f"{roman_to_int(input_words[i + 10][:-1])}.{input_words[i + 8]}.{input_words[i + 6]}.{input_words[i + 1]}")
														output.append(f"{roman_to_int(input_words[i + 10][:-1])}.{input_words[i + 8]}.{input_words[i + 6]}.{input_words[i + 4]}")
														return output, i + 10
												# điểm a/1 và điểm b/2 khoản a/1 Điều a/1 abcxyz ...
												elif input_words[i + 9].lower() != "chương":
													output.append(f"0.{input_words[i + 8]}.{input_words[i + 6]}.{input_words[i + 1]}")
													output.append(f"0.{input_words[i + 8]}.{input_words[i + 6]}.{input_words[i + 4]}")
													return output, i + 8
											# elif i + 9 out of range
											else:
												output.append(f"0.{input_words[i + 8]}.{input_words[i + 6]}.{input_words[i + 1]}")
												output.append(f"0.{input_words[i + 8]}.{input_words[i + 6]}.{input_words[i + 4]}")
												return output, i + 8
										# điểm a/1 và điểm b/2 khoản a/1 Điều a/1./,
										elif not valid_article(input_words[i + 8]) and valid_article(input_words[i + 8][:-1]):
											output.append(f"0.{input_words[i + 8][:-1]}.{input_words[i + 6]}.{input_words[i + 1]}")
											output.append(f"0.{input_words[i + 8][:-1]}.{input_words[i + 6]}.{input_words[i + 4]}")
											return output, i + 8
								# điểm a/1 và điểm b/2 khoản a/1.\,
								elif not input_words[i + 6][-1].isalnum() and input_words[i + 6][:-1].isalnum():
									output.append(f"0.{index_list[1]}.{input_words[i + 6][:-1]}.{input_words[i + 1]}")
									output.append(f"0.{index_list[1]}.{input_words[i + 6][:-1]}.{input_words[i + 4]}")
									return output, i + 6
					# điểm a/1 abcxyz ...
					elif len(input_words[i + 1]) <= 2 and input_words[i + 2] != "và" and input_words[i + 2].lower() != "khoản":
						output.append(f"0.{index_list[1]}.{index_list[2]}.{input_words[i + 1]}")
						return output, i + 2
				
				# điểm a/1, ...
				elif valid_article(input_words[i + 1][:-1]) and input_words[i + 1][-1] == ",":
					point_list = []
					j = 0
					while input_words[i + j + 1][-1] == "," and valid_article(input_words[i + j + 1][:-1]):
						point_list.append(input_words[i + j + 1][:-1])
						j += 1
					# điểm a/1, b/2, c/3 ...
					if valid_article(input_words[i + j + 1]):
						point_list.append(input_words[i + j + 1])
						# điểm a/1, b/2, c/3 khoản ...
						if input_words[i + j + 2].lower() == "khoản":
							# điểm a/1, b/2, c/3 khoản này
							if "này" in input_words[i + j + 3]:
								for point in point_list:
									output.append(f"0.{index_list[1]}.{index_list[2]}.{point}")
								return output, i + j + 3
							# điểm a/1, b/2, c/3 khoản a/1
							elif input_words[i + j + 2].isalnum():
								# điểm a/1, b/2, c/3 khoản a/1 điều ...
								if input_words[i + j + 3].lower() == "điều":
									# điểm a/1, b/2, c/3 khoản a/1 điều này
									if "này" in input_words[i + j + 4]:
										for point in point_list:
											output.append(f"0.{index_list[1]}.{input_words[i + j + 2]}.{point}")
										return output, i + j + 4
									# điểm a/1, b/2, c/3 khoản a/1 điều a/1 ...
									elif valid_article(input_words[i + j + 4]):
										# điểm a/1, b/2, c/3 khoản a/1 Điều a/1 Chương ...
										if input_words[i + j + 5].lower() == "chương":
											# điểm a/1, b/2, c/3 khoản a/1 Điều a/1 Chương này ...
											if "này" in input_words[i + j + 6]:
												for point in point_list:
													output.append(f"0.{input_words[i + j + 4]}.{input_words[i + j + 2]}.{point}")
												return output, i + j + 6
                                            # điểm a/1, b/2, c/3 khoản a/1 Điều a/1 Chương 1 ...
											if input_words[i + j + 6].isnumeric():
												for point in point_list:
													output.append(f"{input_words[i + j + 6]}.{input_words[i + j + 4]}.{input_words[i + j + 2]}.{point}")
												return output, i + j + 6
											# điểm a/1, b/2, c/3 khoản a/1 Điều a/1 Chương I
											elif is_roman(input_words[i + j + 6]):
												for point in point_list:
													output.append(f"{roman_to_int(input_words[i + j + 6])}.{input_words[i + j + 4]}.{input_words[i + j + 2]}.{point}")
												return output, i + j + 6
									# điểm a/1, b/2, c/3 khoản a/1 Điều a/1.,'
									elif input_words[i + j + 4][0].isnumeric() and not input_words[i + j + 4].isalnum():
										for point in point_list:
											output.append(f"0.{input_words[i + j + 1][:-1]}.{input_words[i + j + 3]}.{point}")
										return output, i + j + 4
                        # điểm a/1, b/2, c/3 và ...
						if input_words[i + j + 2] == "và":
							# điểm a/1, b/2, c/3 và đ/4 ...
							if input_words[i + j + 3].isalnum():
								point_list.append(input_words[i + j + 3])
								# điểm a/1, b/2, c/3 và đ/4 khoản ...
								if input_words[i + j + 4].lower() == "khoản":
									# điểm a/1, b/2, c/3 và đ/4 khoản này
									if "này" in input_words[i + j + 5]:
										for point in point_list:
											output.append(f"0.{index_list[1]}.{index_list[2]}.{point}")
										return output, i + j + 5
									# điểm a/1, b/2, c/3 và đ/4 khoản a/1 ...
									elif input_words[i + j + 5].isalnum():
										# điểm a/1, b/2, c/3 và đ/4 khoản a/1 Điều ...
										if input_words[i + j + 6].lower() == "điều":
											# điểm a/1, b/2, c/3 và đ/4 khoản a/1 Điều này
											if "này" in input_words[i + j + 7]:
												for point in point_list:
													output.append(f"0.{index_list[1]}.{input_words[i + j + 5]}.{point}")
												return output, i + j + 7
											# điểm a/1, b/2, c/3 và đ/4 khoản a/1 Điều a/1 ...
											elif input_words[i + j + 7].isalnum():
												# điểm a/1, b/2, c/3 và đ/4 khoản a/1 Điều a/1 Chương ...
												if input_words[i + j + 8].lower() == "chương":
													# điểm a/1, b/2, c/3 và đ/4 khoản a/1 Điều a/1 Chương này
													if "này" in input_words[i + j + 9]:
														for point in point_list:
															output.append(f"{index_list[0]}.{input_words[i + j + 7]}.{input_words[i + j + 5]}.{point}")
														return output, i + j + 9
													# điểm a/1, b/2, c/3 và đ/4 khoản a/1 Điều a/1 Chương 1
													elif input_words[i + j + 9].isnumeric():
														for point in point_list:
															output.append(f"{input_words[i + j + 9]}.{input_words[i + j + 7]}.{input_words[i + j + 5]}.{point}")
														return output, i + j + 9
													# điểm a/1, b/2, c/3 và đ/4 khoản a/1 Điều a/1 Chương 1./,
													elif input_words[i + j + 9][0].isnumeric() and not input_words[i + j + 9][-1].isalnum():
														for point in point_list:
															output.append(f"{input_words[i + j + 9][:-1]}.{input_words[i + j + 7]}.{input_words[i + j + 5]}.{point}")
														return output, i + j + 9
													# điểm a/1, b/2, c/3 và đ/4 khoản a/1 Điều a/1 Chương I
													elif is_roman(input_words[i + j + 9]):
														for point in point_list:
															output.append(f"{roman_to_int(input_words[i + j + 9])}.{input_words[i + j + 7]}.{input_words[i + j + 5]}.{point}")
														return output, i + j + 9
													# điểm a/1, b/2, c/3 và đ/4 khoản a/1 Điều a/1 Chương I./,
													elif is_roman(input_words[i + j + 9][0]) and not input_words[i + j + 9][-1].isalnum():
														for point in point_list:
															output.append(f"{roman_to_int(input_words[i + j + 9][:-1])}.{input_words[i + j + 7]}.{input_words[i + j + 5]}.{point}")
														return output, i + j + 9
												# điểm a/1, b/2, c/3 và đ/4 khoản a/1 Điều a/1 abcxyz ...
												elif input_words[i + j + 8].lower() != "chương":
													for point in point_list:
														output.append(f"0.{input_words[i + j + 7]}.{input_words[i + j + 5]}.{point}")
													return output, i + j + 8
									# điểm a/1, b/2, c/3 và đ/4 khoản a/1,\,
									elif not input_words[i + j + 5][-1].isalnum() and input_words[i + j + 5][:-1].isalnum():
										for point in point_list:
											output.append(f"0.{index_list[1]}.{input_words[i + j + 5][:-1]}.{point}")
										return output, i + j + 1
		# khoản ...
		elif input_words[i].lower() == "khoản":
			# if i + 1 not out of range
			if i + 1 < input_length:
				# khoản này
				if "này" in input_words[i + 1]:
					output.append(f"0.{index_list[1]}.{index_list[2]}.0")
					return output, i + 1
				
				# khoản a/1 ...
				elif input_words[i + 1].isalnum() and len(input_words[i + 1]) == 1:
					# if i + 2 not out of range
					if i + 2 < input_length:
						# khoản a/1 Điều ...
						if input_words[i + 2].lower() == "điều":
							# khoản a/1 Điều này
							if "này" in input_words[i + 3]:
								output.append(f"0.{index_list[1]}.{input_words[i + 1]}.0")
								return output, i + 3
							# khoản a/1 Điều a/1 ...
							elif input_words[i + 3].isalnum():
								# if i + 4 not out of range
								if i + 4 < input_length:
									# khoản a/1 Điều a/1 Chương ...
									if input_words[i + 4].lower() == "chương":
										# khoản a/1 Điều a/1 Chương này
										if "này" in input_words[i + 5]:
											output.append(f"0.{input_words[i + 3]}.{input_words[i + 1]}.0")
											return output, i + 5
										# khoản a/1 Điều a/1 Chương 1
										elif input_words[i + 5].isnumeric():
											output.append(f"{input_words[i + 5]}.{input_words[i + 3]}.{input_words[i + 1]}.0")
											return output, i + 5
										# khoản a/1 Điều a/1 Chương 1./,
										elif input_words[i + 5][0].isnumeric() and not input_words[i + 5][-1].isalnum():
											output.append(f"{input_words[i + 5][:-1]}.{input_words[i + 3]}.{input_words[i + 1]}.0")
											return output, i + 5
										# khoản a/1 Điều a/1 Chương I
										elif is_roman(input_words[i + 5]):
											output.append(f"{roman_to_int(input_words[i + 5])}.{input_words[i + 3]}.{input_words[i + 1]}.0")
											return output, i + 5
										# khoản a/1 Điều a/1 Chương I./,
										elif is_roman(input_words[i + 5][0]) and not input_words[i + 5][-1].isalnum():
											output.append(f"{roman_to_int(input_words[i + 5][:-1])}.{input_words[i + 3]}.{input_words[i + 1]}.0")
											return output, i + 5
									# khoản a/1 Điều a/1 abcxyz ...
									elif input_words[i + 4].lower() != "chương":
										output.append(f"0.{input_words[i + 3]}.{input_words[i + 1]}.0")
										return output, i + 3
								# elif i + 4 out of range
								else:
									output.append(f"0.{input_words[i + 3]}.{input_words[i + 1]}.0")
									return output, i + 3
							# khoản a/1 Điều 1,/. ...
							elif not input_words[i + 3][-1].isalnum() and input_words[i + 3][:-1].isalnum():
								output.append(f"0.{input_words[i + 3][:-1]}.{input_words[i + 1]}.0")
								return output, i + 3
						# khoản a/1 và điểm ...
						elif input_words[i + 2] == "và" and input_words[i + 3] == "điểm":
							for j in range(i + 4, input_length - 1):
								# khoản a/1 và điểm ... Điều này ...
								if input_words[j].lower() == "điều" and "này" in input_words[j + 1]:
									output.append(f"0.{index_list[1]}.{input_words[i + 1]}.0")
									return output, i + 1
								# khoản a/1 và điểm ... Điều a/1 ...
								elif input_words[j].lower() == "điều" and input_words[j + 1].isalnum():
									# if j + 2 not out of range
									if j + 2 < input_length:
										# khoản a/1 và điểm ... Điều a/1 Chương ...
										if input_words[j + 2].lower() == "chương":
											# khoản a/1 và điểm ... Điều a/1 Chương này
											if "này" in input_words[j + 3]:
												output.append(f"0.{input_words[j + 1]}.{input_words[i + 1]}.0")
												return output, i + 1
											# khoản a/1 và điểm ... Điều a/1 Chương 1
											elif input_words[j + 3].isnumeric():
												output.append(f"{input_words[j + 3]}.{input_words[j + 1]}.{input_words[i + 1]}.0")
												return output, i + 1
											# khoản a/1 và điểm ... Điều a/1 Chương 1./,
											elif not input_words[j + 3][-1].isnumeric() and input_words[j + 3][:-1].isnumeric():
												output.append(f"{input_words[j + 3][:-1]}.{input_words[j + 1]}.{input_words[i + 1]}.0")
												return output, i + 1
											# khoản 1 và điểm ... Điều 1 Chương I
											elif is_roman(input_words[j + 3]):
												output.append(f"{roman_to_int(input_words[j + 3])}.{input_words[j + 1]}.{input_words[i + 1]}.0")
												return output, i + 1
											# khoản 1 và điểm ... Điều 1 Chương I./,
											elif not is_roman(input_words[j + 3][-1]) and is_roman(input_words[j + 3][:-1]):
												output.append(f"{roman_to_int(input_words[j + 3][:-1])}.{input_words[j + 1]}.{input_words[i + 1]}.0")
												return output, i + 1
										# khoản a/1 và điểm ... Điều a/1 abcxyz ...
										elif input_words[j + 2].lower() != "chương":
											output.append(f"0.{input_words[j + 1]}.{input_words[i + 1]}.0")
											return output, i + 1
									# elif j + 2 out of range
									else:
										output.append(f"0.{input_words[j + 1]}.{input_words[i + 1]}.0")
										return output, i + 1
								# khoản a/1 và điểm ... Điều a/1./,
								elif input_words[j].lower() == "điều" and not input_words[j + 1][-1].isalnum() and input_words[j + 1][:-1].isalnum():
									output.append(f"0.{input_words[j + 1][:-1]}.{input_words[i + 1]}.0")
									return output, i + 1
                        # khoản a/1 và khoản b/2 ...
						elif input_words[i + 2] == "và" and input_words[i + 3].lower() == "khoản":
							# khoản a/1 và khoản b/2 ...
							if input_words[i + 4].isalnum():
								# khoản a/1 và khoản b/2 Điều ...
								if input_words[i + 5].lower() == "điều":
									# khoản a/1 và khoản b/2 Điều này
									if "này" in input_words[i + 6]:
										output.append(f"0.{index_list[1]}.{input_words[i + 1]}.0")
										output.append(f"0.{index_list[1]}.{input_words[i + 4]}.0")
										return output, i + 6
									# khoản a/1 và khoản b/2 Điều a/1 ...
									elif input_words[i + 6].isalnum():
										# if i + 7 not out of range
										if i + 7 < input_length:
											# khoản a/1 và khoản b/2 Điều a/1 Chương ...
											if input_words[i + 7].lower() == "chương":
												# khoản 1 và khoản 2 Điều 1 Chương này
												if "này" in input_words[i + 8]:
													output.append(f"0.{input_words[i + 6]}.{input_words[i + 1]}.0")
													output.append(f"0.{input_words[i + 6]}.{input_words[i + 4]}.0")
													return output, i + 8
												# khoản 1 và khoản 2 Điều 1 Chương 1
												elif input_words[i + 8].isnumeric():
													output.append(f"{input_words[i + 8]}.{input_words[i + 6]}.{input_words[i + 1]}.0")
													output.append(f"{input_words[i + 8]}.{input_words[i + 6]}.{input_words[i + 4]}.0")
													return output, i + 8
												# khoản 1 và khoản 2 Điều 1 Chương 1./,
												elif input_words[i + 8][0].isnumeric() and not input_words[j + 8][-1].isalnum:
													output.append(f"{input_words[i + 8][:-1]}.{input_words[i + 6]}.{input_words[i + 1]}.0")
													output.append(f"{input_words[i + 8][:-1]}.{input_words[i + 6]}.{input_words[i + 4]}.0")
													return output, i + 8
												# khoản 1 và khoản 2 Điều 1 Chương I
												elif is_roman(input_words[i + 8]):
													output.append(f"{roman_to_int(input_words[i + 8])}.{input_words[i + 6]}.{input_words[i + 1]}.0")
													output.append(f"{roman_to_int(input_words[i + 8])}.{input_words[i + 6]}.{input_words[i + 4]}.0")
													return output, i + 8
												# khoản 1 và khoản 2 Điều 1 Chương I./,
												elif not is_roman(input_words[i + 8][-1]) and is_roman(input_words[i + 8][:-1]):
													output.append(f"{roman_to_int(input_words[i + 8][:-1])}.{input_words[i + 6]}.{input_words[i + 1]}.0")
													output.append(f"{roman_to_int(input_words[i + 8][:-1])}.{input_words[i + 6]}.{input_words[i + 4]}.0")
													return output, i + 8
											# khoản 1 và khoản 2 Điều 1 abcxyz ...
											elif input_words[i + 7].lower() != "chương":
												output.append(f"0.{input_words[i + 6]}.{input_words[i + 1]}.0")
												output.append(f"0.{input_words[i + 6]}.{input_words[i + 4]}.0")
												return output, i + 6
										# if i + 7 out of range
										else:
											output.append(f"0.{input_words[i + 6]}.{input_words[i + 1]}.0")
											output.append(f"0.{input_words[i + 6]}.{input_words[i + 4]}.0")
											return output, i + 6
									# khoản a/1 và khoản b/2 Điều a/1, ...
									elif not input_words[i + 6][-1].isalnum() and input_words[i + 6][:-1].isalnum():
										output.append(f"0.{input_words[i + 6][:-1]}.{input_words[i + 1]}.0")
										output.append(f"0.{input_words[i + 6][:-1]}.{input_words[i + 4]}.0")
										return output, i + 6
						# khoản a/1 và b/2
						elif input_words[i + 2] == "và" and input_words[i + 3].isalnum():
							# khoản a/1 và b/2 Điều ...
							if input_words[i + 4].lower() == "điều":
								# khoản a/1 và b/2 Điều này
								if "này" in input_words[i + 5]:
									output.append(f"0.{index_list[1]}.{input_words[i + 1]}.0")
									output.append(f"0.{index_list[1]}.{input_words[i + 3]}.0")
									return output, i + 5
								# khoản a/1 và b/2 Điều a/1 ...
								elif input_words[i + 5][0].isalnum():
									# if i + 6 not out of range
									if i + 6 < input_length:
										# khoản a/1 và b/2 Điều a/1 Chương ...
										if input_words[i + 6].lower() == "chương":
											# khoản a/1 và b/2 Điều a/1 Chương này
											if "này" in input_words[i + 7]:
												output.append(f"{index_list[0]}.{input_words[i + 5]}.{input_words[i + 1]}.0")
												output.append(f"{index_list[0]}.{input_words[i + 5]}.{input_words[i + 3]}.0")
												return output, i + 7
											# khoản a/1 và b/2 Điều a/1 Chương 1
											if input_words[i + 7][0].isnumeric():
												output.append(f"{input_words[i + 7]}.{input_words[i + 5]}.{input_words[i + 1]}.0")
												output.append(f"{input_words[i + 7]}.{input_words[i + 5]}.{input_words[i + 3]}.0")
												return output, i + 7
											# khoản a/1 và b/2 Điều a/1 Chương I
											elif is_roman(input_words[i + 7]):
												output.append(f"{roman_to_int(input_words[i + 7])}.{input_words[i + 5]}.{input_words[i + 1]}.0")
												output.append(f"{roman_to_int(input_words[i + 7])}.{input_words[i + 5]}.{input_words[i + 3]}.0")
												return output, i + 7
										# khoản a/1 và b/2 Điều a/1 abcxyz
										elif input_words[i + 6].lower() != "chương":
											output.append(f"0.{input_words[i + 5]}.{input_words[i + 1]}.0")
											output.append(f"0.{input_words[i + 5]}.{input_words[i + 3]}.0")
											return output, i + 5						
						# khoản a/1 abcxyz ...
						elif len(input_words[i + 1]) <= 2 and input_words[i + 2] != "và" and input_words[i + 2].lower() != "khoản":
							output.append(f"0.{index_list[1]}.{input_words[i + 1]}.0")
							return output, i + 1
					# elif i + 2 out of range
					else:
						output.append(f"0.{index_list[1]}.{input_words[i + 1]}.0")
						return output, i + 1

				# khoản a/1, ...
				elif input_words[i + 1][:-1].isalnum() and input_words[i + 1][-1] == ",":
					clause_list = []
					j = 0
					while input_words[i + j + 1][-1] == "," and input_words[i + j + 1][:-1].isalnum():
						clause_list.append(input_words[i + j + 1][:-1])
						j += 1
					# khoản a/1, b/2, c/3 ...
					if input_words[i + j + 1][0].isalnum():
						clause_list.append(input_words[i + j + 1])
						# khoản a/1, b/2, c/3 và ...
						if input_words[i + j + 2] == "và":
							# khoản a/1, b/2, c/3 và đ/4 ...
							if input_words[i + j + 3].isalnum():
								clause_list.append(input_words[i + j + 3])
								# khoản a/1, b/2, c/3 và đ/4 Điều ...
								if input_words[i + j + 4].lower() == "điều":
									# khoản a/1, b/2, c/3 và đ/4 Điều này
									if "này" in input_words[i + j + 5]:
										for point in clause_list:
											output.append(f"0.{index_list[1]}.{point}.0")
										return output, i + j + 5
									# khoản a/1, b/2, c/3 và đ/4 Điều a/1 ...
									elif input_words[i + j + 5].isalnum():
										# khoản a/1, b/2, c/3 và đ/4 Điều a/1 Chương ...
										if input_words[i + j + 6].lower() == "chương":
											# khoản a/1, b/2, c/3 và đ/4 Điều a/1 Chương này
											if "này" in input_words[i + j + 7]:
												for point in clause_list:
													output.append(f"0.{input_words[i + j + 5]}.{point}.0")
												return output, i + j + 7
											# khoản a/1, b/2, c/3 và đ/4 Điều a/1 Chương 1
											elif input_words[i + j + 7].isnumeric():
												for point in clause_list:
													output.append(f"{input_words[i + j + 7]}.{input_words[i + j + 5]}.{point}.0")
												return output, i + j + 7
											# khoản a/1, b/2, c/3 và đ/4 Điều a/1 Chương 1./,
											elif not input_words[i + j + 7][:-1].isnumeric() and not input_words[i + j + 7][-1].isalnum():
												for point in clause_list:
													output.append(f"{input_words[i + j + 7][:-1]}.{input_words[i + j + 5]}.{point}.0")
												return output, i + j + 7
											# khoản a/1, b/2, c/3 và đ/4 Điều a/1 Chương I
											elif is_roman(input_words[i + j + 7]):
												for point in clause_list:
													output.append(f"{roman_to_int(input_words[i + j + 7])}.{input_words[i + j + 5]}.{point}.0")
												return output, i + j + 7
											# khoản a/1, b/2, c/3 và đ/4 Điều a/1 Chương I./,
											elif is_roman(input_words[i + j + 7][:-1]) and not input_words[i + j + 7][-1].isalnum():
												for point in clause_list:
													output.append(f"{roman_to_int(input_words[i + j + 7][:-1])}.{input_words[i + j + 5]}.{point}.0")
												return output, i + j + 7
										# khoản a/1, b/2, c/3 và đ/4 Điều a/1 abcxyz ...
										elif input_words[i + j + 6].lower() != "chương":
											for point in clause_list:
												output.append(f"0.{input_words[i + j + 5]}.{point}.0")
											return output, i + j + 6
							# khoản a/1, b/2, c/3 và điểm ...
							if input_words[i + j + 3] == "điểm":
								for k in range(i + j + 4, input_length - 1):
									# khoản a/1, b/2, c/3 và điểm ... Điều này ...
									if input_words[k].lower() == "điều" and "này" in input_words[k + 1]:
										for point in clause_list:
											output.append(f"0.{index_list[1]}.{point}.0")
										return output, i + j + 1
									# khoản a/1, b/2, c/3 và điểm ... Điều a/1 ...
									elif input_words[k].lower() == "điều" and input_words[k + 1].isalnum():
										# khoản a/1, b/2, c/3 và điểm ... Điều a/1 Chương ...
										if input_words[k + 2] == "Chương":
											# khoản a/1, b/2, c/3 và điểm ... Điều a/1 Chương này
											if "này" in input_words[k + 3]:
												for point in clause_list:
													output.append(f"0.{input_words[k + 1]}.{point}.0")
												return output, i + j + 1
											# khoản a/1, b/2, c/3 và điểm ... Điều a/1 Chương 1
											elif input_words[k + 3].isnumeric():
												for point in clause_list:
													output.append(f"{input_words[k + 3]}.{input_words[k + 1]}.{point}.0")
												return output, i + j + 1
											# khoản a/1, b/2, c/3 và điểm ... Điều a/1 Chương 1./,
											elif input_words[k + 3][:-1].isnumeric() and not input_words[k + 3][-1].isalnum():
												for point in clause_list:
													output.append(f"{input_words[k + 3][:-1]}.{input_words[k + 1]}.{point}.0")
												return output, i + j + 1
											# khoản a/1, b/2, c/3 và điểm ... Điều a/1 Chương I
											elif is_roman(input_words[k + 3]):
												for point in clause_list:
													output.append(f"{roman_to_int(input_words[k + 3])}.{input_words[k + 1]}.{point}.0")
												return output, i + j + 1
											# khoản a/1, b/2, c/3 và điểm ... Điều a/1 Chương I./,
											elif is_roman(input_words[k + 3][:-1]) and not input_words[k + 3][-1].isalnum():
												for point in clause_list:
													output.append(f"{roman_to_int(input_words[k + 3][:-1])}.{input_words[k + 1]}.{point}.0")
												return output, i + j + 1
										# khoản a/1, b/2, c/3 và điểm ... Điều a/1 abcxyz ...
										elif input_words[k + 2].lower() != "chương":
											for point in clause_list:
												output.append(f"0.{input_words[k + 1]}.{point}.0")
											return output, i + j + 1
									# khoản a/1, b/2, c/3 và điểm ... Điều a/1./,
									elif input_words[k].lower() == "điều" and not input_words[k + 1].isalnum() and input_words[k + 1][:-1].isalnum():
										for point in clause_list:
											output.append(f"0.{input_words[k + 1][:-1]}.{point}.0")
										return output, i + j + 1
		# điều ...
		elif input_words[i].lower() == "điều":
			# if i + 1 not out of range
			if i + 1 < input_length:
				# điều này
				if "này" in input_words[i + 1]:
					output.append(f"0.{index_list[1]}.0.0")
					return output, i + 1
				
				# điều a/1 ...
				elif valid_article(input_words[i + 1]) and len(input_words[i + 1]) == 1:
					# if i + 2 not out of range
					if i + 2 < input_length:
						# điều a/1 Chương ...
						if input_words[i + 2].lower() == "chương":
							# điều a/1 Chương này
							if "này" in input_words[i + 3]:
								output.append(f"0.{input_words[i + 1]}.0.0")
								return output, i + 3
							# điều a/1 Chương 1
							elif input_words[i + 3].isnumeric():
								output.append(f"{input_words[i + 3]}.{input_words[i + 1]}.0.0")
								return output, i + 3
							# điều a/1 Chương 1./,
							elif not input_words[i + 3].isnumeric() and input_words[i + 3][:-1].isnumeric():
								output.append(f"{input_words[i + 3][:-1]}.{input_words[i + 1]}.0.0")
								return output, i + 3
							# điều a/1 Chương I
							elif is_roman(input_words[i + 3]):
								output.append(f"{roman_to_int(input_words[i + 3])}.{input_words[i + 1]}.0.0")
								return output, i + 3
							# điều a/1 Chương I./,
							elif is_roman(input_words[i + 3][:-1]) and not is_roman(input_words[i + 3][-1]):
								output.append(f"{roman_to_int(input_words[i + 3][:-1])}.{input_words[i + 1]}.0.0")
								return output, i + 3
						# điều a/1 abcxyz ...
						elif len(input_words[i + 1]) <= 2 and input_words[i + 2].lower() != "chương":
							output.append(f"0.{input_words[i + 1]}.0.0")
							return output, i + 1
					# if i + 2 out of range
					else:
						output.append(f"0.{input_words[i + 1]}.0.0")
						return output, i + 1
				
				# điều a/1, ...
				elif not valid_article(input_words[i + 1]) and input_words[i + 1][-1] == ",":
					article_list = []
					j = 0
					while input_words[i + j + 1][-1] == "," and input_words[i + j + 1][0].isnumeric():
						article_list.append(input_words[i + j + 1][:-1])
						j += 1
					# điều a/1, b/2, c/3 ...
					if valid_article(input_words[i + j + 1]):
						article_list.append(input_words[i + j + 1])
						# điều a/1, b/2, c/3 và ...
						if input_words[i + j + 2] == "và":
							# điều a/1, b/2, c/3 và đ/4 ...
							if valid_article(input_words[i + j + 3]):
								article_list.append(input_words[i + j + 3])
								# điều a/1, b/2, c/3 và đ/4 Chương ...
								if input_words[i + j + 4].lower() == "chương":
									# điều a/1, b/2, c/3 và đ/4 Chương này
									if "này" in input_words[i + j + 5]:
										for point in article_list:
											output.append(f"0.{point}.0.0")
										return output, i + j + 5
									# điều a/1, b/2, c/3 và đ/4 Chương 1
									elif input_words[i + j + 5].isnumeric():
										for point in article_list:
											output.append(f"{input_words[i + j + 5]}.{point}.0.0")
										return output, i + j + 5
									# điều a/1, b/2, c/3 và đ/4 Chương 1./,
									elif input_words[i + j + 5][:-1].isnumeric() and not input_words[i + j + 5].isnumeric():
										for point in article_list:
											output.append(f"{input_words[i + j + 5][:-1]}.{point}.0.0")
										return output, i + j + 5
									# điều a/1, b/2, c/3 và đ/4 Chương I
									elif is_roman(input_words[i + j + 5]):
										for point in article_list:
											output.append(f"{roman_to_int(input_words[i + j + 5])}.{point}.0.0")
										return output, i + j + 5
									# điều a/1, b/2, c/3 và đ/4 Chương I./,
									elif is_roman(input_words[i + j + 5][:-1]) and not is_roman(input_words[i + j + 5][-1]):
										for point in article_list:
											output.append(f"{roman_to_int(input_words[i + j + 5][:-1])}.{point}.0.0")
										return output, i + j + 5	
								# điều a/1, b/2, c/3 và đ/4 abcxyz ...
								elif input_words[i + j + 4].lower() != "chương":
									for point in article_list:
										output.append(f"0.{point}.0.0")
									return output, i + j + 4
							# điều a/1, b/2, c/3 và đ/4, ...
							elif input_words[i + j + 3][-1] == "," and input_words[i + j + 3][0].isnumeric():
								article_list.append(input_words[i + j + 3][:-1])
								for point in article_list:
									output.append(f"0.{point}.0.0")
								return output, i + j + 3
							# điều a/1, b/2, c/3 và abcxyz
							else:
								for point in article_list:
									output.append(f"0.{point}.0.0")
								return output, i + j + 3
					# điều a/1, abcxyz ...
					if input_words[i + j + 1].isalnum() and len(input_words[i + j + 1]) >= 3:
						for point in article_list:
							output.append(f"0.{point}.0.0")
						return output, i + j
		
		# # chương ...
		# elif input_words[i].lower() == "chương":
		# 	# if i + 1 not out of range
		# 	if i + 1 < input_length:
		# 		# chương này
		# 		if "này" in input_words[i + 1]:
		# 			output.append(f"0.0.0.0")
		# 			return output, i + 1
				
		# 		# chương 1 ...
		# 		elif input_words[i + 1][0].isnumeric():
		# 			output.append(f"{input_words[i + 1]}.0.0.0")
		# 			return output, i + 1
				
		# 		# chương I ...
		# 		elif is_roman(input_words[i + 1]) and input_words[i + 1].isupper():
		# 			output.append(f"{roman_to_int(input_words[i + 1])}.0.0.0")
		# 			return output, i + 1
	
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

def remove_accent_and_lowercase(text: str) -> str:
	return unidecode(text).lower()

def find_word_position(corpus_words_list, query_words_list):
	corpus_len = len(corpus_words_list)
	for i in range(corpus_len):
		if query_words_list[0].lower() in corpus_words_list[i].lower():
			j = 1
			while (i + j) < corpus_len and j < len(query_words_list) and query_words_list[j].lower() in corpus_words_list[i + j].lower():
				j += 1
				if j == len(query_words_list):
					return i
	return -1

def find_first_occurrence_index(text, texts_list):
    original_words = text.split()
    preprocessed_words = [word.lower().strip(',.!?') for word in original_words]
    min_index = None
    
    for name in texts_list:
        parts = name.lower().split()
        name_len = len(parts)
        max_start = len(preprocessed_words) - name_len + 1
        
        for start in range(max_start):
            match = True
            for i in range(name_len):
                if preprocessed_words[start + i] != parts[i]:
                    match = False
                    break
            if match:
                if min_index is None or start < min_index:
                    min_index = start
                break  # Move to the next name after finding the first occurrence
    
    return min_index if min_index is not None else -1

def find_first_occurrence_index_new(text, texts_list, start_position=0, end_position=None):
	original_words = text.split()
	preprocessed_words = [word.lower().strip(',.:!?') for word in original_words]
	min_index = None
	matching_text = None
	
	for name in texts_list:
		parts = name.lower().split()
		name_len = len(parts)
		max_start = len(preprocessed_words) - name_len + 1
		
		for start in range(max_start):
			if start + start_position >= len(preprocessed_words):
				break  # Skip if the start position is out of bounds
			if end_position is not None and start + start_position + name_len > end_position:
				break  # Skip if the end position is out of bounds
			
			match = True
				
			for i in range(name_len):
				try:
					if preprocessed_words[start + start_position + i] != parts[i]:
						match = False
						break
				except IndexError:
					print(text, texts_list, start_position, end_position)
			if match:
				if min_index is None or (start + start_position) < min_index:
					min_index = start + start_position
					matching_text = name
				break  # Move to the next name after finding the first occurrence
	
	return min_index if min_index is not None else -1, matching_text

def find_word_position_backward(corpus_words_list, query_words_list):
	corpus_len = len(corpus_words_list)
	if len(query_words_list) == 1:
		for i in range(corpus_len - 1, -1, -1):
			if query_words_list[0].lower() in corpus_words_list[i].lower():
				return i
		return -1

	for i in range(corpus_len - 1, -1, -1):
		if query_words_list[0].lower() in corpus_words_list[i].lower():
			j = 1
			while (i + j) < corpus_len and j < len(query_words_list) and query_words_list[j].lower() in corpus_words_list[i + j].lower():
				j += 1
				if j == len(query_words_list):
					return i
	return -1

def find_end_of_sentence(input_texts: List[str], start_index: int) -> int:
	for i in range(start_index, len(input_texts)):
		if input_texts[i][-1] in ['.', '?', '!']:
			return i + 1
	return len(input_texts)

def find_start_of_sentence(input_texts: List[str], start_index: int) -> int:
	for i in range(start_index, -1, -1):
		if input_texts[i][-1] in ['.', '?', '!']:
			return i + 1
	return 0

def find_after_juris_list(input_texts: List[str], start_index: int) -> List:
	output = [start_index]
	end_index = find_end_of_sentence(input_texts, start_index)
	for i in range(start_index, end_index):
		if input_texts[i][-1] == ";":
			output.append(i + 1)
	output.append(end_index)
	return output

def find_before_juris_list(input_texts: List[str], end_index: int) -> List:
	very_start_index = find_start_of_sentence(input_texts, end_index)
	output = [very_start_index]
	for i in range(very_start_index, end_index):
		if input_texts[i][-1] == ";":
			output.append(i + 1)
	output.append(end_index)
	return output

def juris_extract_old(input_text: str):
	keywords = utils.load_json(config.KEYWORDS_PATH)
	original_text = input_text.split()
	content = []
	input_text = remove_accent_and_lowercase(input_text)
	after_keywords = keywords['appear_after']
	after_keywords = [remove_accent_and_lowercase(keyword) for keyword in after_keywords]
	before_keywords = keywords['appear_before']
	before_keywords = [remove_accent_and_lowercase(keyword) for keyword in before_keywords]
	misc_before_keywords = keywords['misc_before']
	misc_before_keywords = [remove_accent_and_lowercase(keyword) for keyword in misc_before_keywords]
	misc_after_keywords = keywords['misc_after']
	misc_after_keywords = [remove_accent_and_lowercase(keyword) for keyword in misc_after_keywords]

	agencies = utils.get_agencies_list()
	agencies = [remove_accent_and_lowercase(agency) for agency in agencies]
	input_text_words = input_text.split()
	for agency in agencies:
		if agency.lower() in input_text.lower():
			agency_words_list = agency.split()
			agency_position = find_word_position(input_text_words, agency_words_list)
			if agency_position != -1:
				for before_keyword in before_keywords:
					before_keyword_words_list = before_keyword.split()
					before_keyword_position = find_word_position_backward(input_text_words[agency_position - 10:agency_position], before_keyword_words_list)
					if before_keyword_position != -1:
						index_list = find_before_juris_list(input_text_words, agency_position + before_keyword_position - 10)
						for ch1, ch2 in zip(index_list, index_list[1:]):
							content.append(' '.join(original_text[ch1:ch2]))
						return {
							"agency": agency,
							"keyword" : before_keyword,
							"content" : content
						}
				for misc_before_keyword in misc_before_keywords:
					misc_before_keyword_words_list = misc_before_keyword.split()
					misc_before_keyword_position = find_word_position_backward(input_text_words[agency_position - 10:agency_position], misc_before_keyword_words_list)
					if misc_before_keyword_position != -1:
						for misc_after_keyword in misc_after_keywords:
							misc_after_keyword_words_list = misc_after_keyword.split()
							misc_after_keyword_position = find_word_position(input_text_words[agency_position + len(agency_words_list):agency_position + len(agency_words_list) + 10], misc_after_keyword_words_list)
							if misc_after_keyword_position != -1:
								index_list = find_before_juris_list(input_text_words, agency_position + misc_before_keyword_position - 10)
								for ch1, ch2 in zip(index_list, index_list[1:]):
									content.append(' '.join(original_text[ch1:ch2]))
								# return input_text[agency_position - misc_before_keyword_position - 5:agency_position + len(agency) + misc_after_keyword_position + 5]
								return {
									"agency" : agency,
									"keyword" : [misc_before_keyword, misc_after_keyword],
									"content" : content
								}
				for after_keyword in after_keywords:
					after_keyword_words_list = after_keyword.split()
					after_keyword_position = find_word_position(input_text_words[agency_position + len(agency_words_list):agency_position + len(agency_words_list) + 10], after_keyword_words_list)
					if after_keyword_position != -1:
						index_list = find_after_juris_list(input_text_words, agency_position + len(agency_words_list) + after_keyword_position + len(after_keyword_words_list))
						for ch1, ch2 in zip(index_list, index_list[1:]):
							content.append(' '.join(original_text[ch1:ch2]))
						return {
							"agency": agency,
							"keyword": after_keyword,
							"content" : content
						}
	return {}

def juris_extract(input_text: str):
	content = []
	jurisdictional_keywords = utils.load_json(config.KEYWORDS_PATH)
	after_keywords = jurisdictional_keywords['appear_after']
	before_keywords = jurisdictional_keywords['appear_before']
	misc_before_keywords = jurisdictional_keywords['misc_before']
	misc_after_keywords = jurisdictional_keywords['misc_after']

	agencies = utils.get_agencies_list()
	agency_position, matched_agency = find_first_occurrence_index_new(input_text, agencies)
	if agency_position != -1:
		before_keyword_position, before_keyword = find_first_occurrence_index_new(input_text, before_keywords, agency_position - 10 if agency_position - 10 > 0 else 0, agency_position)
		if before_keyword_position!= -1:
			index_list = find_before_juris_list(input_text.split(), before_keyword_position)
			for ch1, ch2 in zip(index_list, index_list[1:]):
				content.append(' '.join(input_text.split()[ch1:ch2]))
			return {
				"agency": matched_agency,
				"keyword" : before_keyword,
				"content" : content
			}
		misc_before_keyword_position, misc_before_keyword = find_first_occurrence_index_new(input_text, misc_before_keywords, agency_position - 10 if agency_position - 10 > 0 else 0, agency_position)
		if misc_before_keyword_position!= -1:
			misc_after_keyword_position, misc_after_keyword = find_first_occurrence_index_new(input_text, misc_after_keywords, agency_position + len(matched_agency.split()), agency_position + len(matched_agency.split()) + 10)
			if misc_after_keyword_position != -1:
				index_list = find_before_juris_list(input_text.split(), misc_before_keyword_position)
				for ch1, ch2 in zip(index_list, index_list[1:]):
					content.append(' '.join(input_text.split()[ch1:ch2]))
				return {
					"agency": matched_agency,
					"keyword": [misc_before_keyword, misc_after_keyword],
					"content": content
				}
		after_keyword_position, after_keyword = find_first_occurrence_index_new(input_text, after_keywords, agency_position + len(matched_agency.split()), agency_position + len(matched_agency.split()) + 10)
		if after_keyword_position != -1:
			index_list = find_after_juris_list(input_text.split(), after_keyword_position + len(after_keyword.split()))
			for ch1, ch2 in zip(index_list, index_list[1:]):
				content.append(' '.join(input_text.split()[ch1:ch2]))
			return {
				"agency": matched_agency,
				"keyword": after_keyword,
				"content": content
			}
	return {}