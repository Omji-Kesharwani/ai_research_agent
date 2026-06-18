import uuid
from typing import List , Dict , Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document


class DocumentIngestionService:
    def __init__(self):
        self.parent_splitter = RecursiveCharacterTextSplitter(
            chunk_size = 2000,
            chunk_overlap = 200
        )

        self.child_splitter = RecursiveCharacterTextSplitter(
            chunk_size = 400 ,
            chunk_overlap = 50
        )

    def process_pdf(self, file_path : str) -> Dict[str ,Any]:
        """
        Reads a PDF and generates mapped parent and child chunks.
        """
        print(f"Loading document from {file_path}...")
        loader = PyPDFLoader(file_path)
        raw_pages = loader.load()


        # 1. Create Parent Chunks
        parent_docs = self.parent_splitter.split_documents(raw_pages)

        processed_data = {
            "parents": [],
            "children": []
        }

        # 2. Iterate and Create Child Chunks linked to Parents

        for parent in parent_docs:
            # Generate a unique ID for the parent using standard UUIDs
            parent_id = str(uuid.uuid4())

            parent.metadata["doc_id"] =parent_id
            processed_data["parents"].append(parent)

            # Split this specific parent into children

            child_docs = self.child_splitter.split_documents([parent])

            for child in child_docs:
                child.metadata["parent_id"] = parent_id
                processed_data["children"].append(child)

        print(f"Created {len(processed_data['parents'])} Parent Chunks and {len(processed_data['children'])} Child Chunks.")
        return processed_data


# --- File: core/ingestion.py ---
# (Keep your existing DocumentIngestionService class above this)

if __name__ == "__main__":
    # import os
    
    # Path to your test PDF
    # sample_pdf_path = "sample_paper.pdf"
    
    # if not os.path.exists(sample_pdf_path):
    #     print(f"❌ Error: Please place a file named '{sample_pdf_path}' in your project root folder.")
    # else:
    #     # Initialize the modular service
        service = DocumentIngestionService()
        
    #     # Run the ingestion pipeline
    #     data = service.process_pdf(sample_pdf_path)
        
    #     # Print a sample verification statement
    #     print("\n--- Ingestion Verification Successful ---")
    #     if data["children"]:
    #         sample_child = data["children"][0]
    #         print(f"Sample Child Content Preview: {sample_child.page_content[:150]}...")
    #         print(f"Linked Parent UUID: {sample_child.metadata.get('parent_id')}")
    #         print(f"Source Page: {sample_child.metadata.get('page')}")