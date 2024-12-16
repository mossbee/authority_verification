from pathlib import Path
from typing import Dict, List, Optional
import json
from docx import Document
import logging

class DocxProcessor:
    """A class to process .docx files and manage their content."""

    def __init__(self, file_path: str):
        """Initialize the DocxProcessor with a file path.

        Args:
            file_path (str): Path to the .docx file
        """
        self.file_path = Path(file_path)
        self.document = None
        self.indexed_paragraphs: Dict[int, str] = {}
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Set up logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def read_document(self) -> bool:
        """Read the .docx document.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.file_path.exists():
                self.logger.error(f"File not found: {self.file_path}")
                return False
            
            self.document = Document(self.file_path)
            self.logger.info(f"Successfully read document: {self.file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error reading document: {str(e)}")
            return False

    def index_paragraphs(self) -> Dict[int, str]:
        """Index all paragraphs in the document.

        Returns:
            Dict[int, str]: Dictionary of indexed paragraphs
        """
        if not self.document:
            self.logger.error("No document loaded. Call read_document() first.")
            return {}

        self.indexed_paragraphs = {
            idx: para.text
            for idx, para in enumerate(self.document.paragraphs)
            if para.text.strip()  # Only include non-empty paragraphs
        }
        
        self.logger.info(f"Indexed {len(self.indexed_paragraphs)} paragraphs")
        return self.indexed_paragraphs

    def save_to_json(self, output_path: Optional[str] = None) -> bool:
        """Save indexed paragraphs to a JSON file.

        Args:
            output_path (Optional[str]): Path for the output JSON file.
                If None, uses the same name as input with .json extension.

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.indexed_paragraphs:
            self.logger.error("No indexed paragraphs to save")
            return False

        try:
            if output_path is None:
                output_path = self.file_path.with_suffix('.json')

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.indexed_paragraphs, f, indent=4, ensure_ascii=False)
            
            self.logger.info(f"Successfully saved JSON to: {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving JSON: {str(e)}")
            return False

    def get_paragraph(self, index: int) -> Optional[str]:
        """Retrieve a specific paragraph by index.

        Args:
            index (int): Index of the paragraph to retrieve

        Returns:
            Optional[str]: The paragraph text if found, None otherwise
        """
        return self.indexed_paragraphs.get(index)
    
def main():
    # Create processor instance
    processor = DocxProcessor("example.docx")
    
    # Read and process document
    if processor.read_document():
        # Index paragraphs
        indexed_content = processor.index_paragraphs()
        
        # Save to JSON
        processor.save_to_json("output.json")
        
        # Get specific paragraph
        first_para = processor.get_paragraph(0)
        if first_para:
            print(f"First paragraph: {first_para}")

if __name__ == "__main__":
    main()