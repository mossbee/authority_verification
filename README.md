# Authority Verification

The official implementation of Vietname Legal Documents Authority Verification.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install all required libraries.

```bash
pip install -r requirements.txt
```

## Usage

Each folder in data\legal_cases is a case in the Handbook on Legal Normative Documents Verification, inside it has several files:
- Document being examined.
- Its pursuant documents.
- A .json file contains their name.

Running the 'authority_verification/main.py' to  indexing and extracting information from legal cases.
```cmd
python authority_verification/__main__.py
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)