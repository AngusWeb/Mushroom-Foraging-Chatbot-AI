import pdfplumber
import re
from openai import OpenAI

if True:
    client = OpenAI(
        api_key=input("Please enter your OpenAI API key: "),  # You can omit this if the API key is set in an environment variable
    )
import pdfplumber
import spacy


# Load spaCy model
nlp = spacy.load('en_core_web_sm')

import re

def extract_main_chunks(content):
    """
    Extracts main chunks from the content based on 'Chunk N:' pattern,
    after removing empty 'Chunk N:' lines and extra spaces.
    """
    # Remove empty 'Chunk N:' lines (lines that have 'Chunk N:' and nothing else)
    content = re.sub(r'^Chunk \d+:$\n?', '', content, flags=re.MULTILINE)
    
    # Remove extra blank lines (optional, in case there are multiple blank lines)
    content = re.sub(r'\n+', '\n', content)
    
    # Now extract chunks
    pattern = r'Chunk \d+:\s*(.*?)(?=Chunk \d+:|$)'
    matches = re.findall(pattern, content, re.DOTALL)
    chunks = [match.strip() for match in matches]
    return chunks

def extract_sub_chunks(chunk_content):
    """
    Extracts sub-chunks from a main chunk based on sub-chunk patterns.
    """
    # Pattern for '### Chunk N' or '### Chunk N:'
    pattern1 = r'(### Chunk \d+:?\s*(.*?))(?=(### Chunk \d+|$))'
    # Pattern for '**Chunk N:'
    pattern2 = r'(\*\*Chunk \d+:\s*(.*?))(?=(\*\*Chunk \d+:|$))'

    # Try the first pattern
    matches1 = re.findall(pattern1, chunk_content, re.DOTALL)
    if matches1:
        sub_chunks = [match[1].strip() for match in matches1]
        return sub_chunks

    # Try the second pattern
    matches2 = re.findall(pattern2, chunk_content, re.DOTALL)
    if matches2:
        sub_chunks = [match[1].strip() for match in matches2]
        return sub_chunks

    # If no sub-chunk patterns are found, return the whole chunk
    return [chunk_content.strip()]

def retrieve_chunks(file_path):
    """
    Reads the text file and retrieves all chunks into a Python list.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract main chunks
    main_chunks = extract_main_chunks(content)

    all_chunks = []
    for main_chunk in main_chunks:
        # Extract sub-chunks from each main chunk
        sub_chunks = extract_sub_chunks(main_chunk)
        all_chunks.extend(sub_chunks)
    return all_chunks

if __name__ == '__main__':
    if False:
        file_path = 'optimal_chunksv3.txt' 
        chunks = retrieve_chunks(file_path)
        for idx, chunk in enumerate(chunks):
            
            print(chunk)
            print('---')



def generate_qa_pairs_batched(text_chunks, batch_size=10):
    qa_pairs = []
    # Process in batches
    for i in range(0, len(text_chunks), batch_size):
        
        batch_chunks = [chunk for chunk in text_chunks[i:i+batch_size] if chunk != '']
        
        # Build the prompt for this batch
        prompt = """
You are an expert assistant specialized in creating educational question-answer pairs from the provided text excerpts about mushroom picking.

Your task is to:

1. Read each text carefully.
2. For each text, generate a clear and concise question that focuses on a key piece of information or concept presented in the text.
3. Provide an accurate answer to the question, based solely on the information given in the text.
4. Ensure that both the question and the answer are self-contained and do not reference "the text," "the passage," "the article," "the book," "the author," or any external sources. Avoid phrases like "according to the text," "as mentioned," "the text states," etc.

Please format your response exactly as follows:

Question 1: [Your question for Text 1]

Answer 1: [Your answer for Text 1]

Question 2: [Your question for Text 2]

Answer 2: [Your answer for Text 2]

... (and so on for all texts)

Below are the texts:

"""
        for idx, chunk in enumerate(batch_chunks, start=1):
            prompt += f"Text {idx}:\n\"\"\"\n{chunk}\n\"\"\"\n\n"

        try:
            response = client.chat.completions.create(
                model='gpt-4o-mini',
                messages=[{'role': 'user', 'content': prompt}],
                temperature=0.7,
            )
            # Access the content from the response
            content = response.choices[0].message.content
            print(content)
            # Parse the response to extract questions and answers
            pattern = r'Question (\d+):\s*(.*?)\nAnswer \1:\s*(.*?)(?=\nQuestion \d+:|\Z)'
            matches = re.findall(pattern, content, re.DOTALL)
            for match in matches:
                question_num = int(match[0])
                question = match[1].strip()
                answer = match[2].strip()
                qa_pairs.append((question, answer))
                print(f"Question {question_num}: {question}")
        except Exception as e:
            print(f"An error occurred: {e}")
            continue
    return qa_pairs

def format_qa_pairs(qa_pairs):
    formatted_data = ""
    for question, answer in qa_pairs:
        formatted_dialogue = f"""<|begin_of_text|><|start_header_id|>user<|end_header_id|>

{question}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

{answer}<|eot_id|>
"""
        formatted_data += formatted_dialogue
    return formatted_data

# Main execution
pdf_files = ['Jens_H_Petersen.pdf']
file_path = 'optimal_chunksv3.txt'  
text_chunks = retrieve_chunks(file_path)



qa_pairs = generate_qa_pairs_batched(text_chunks)
formatted_dataset = format_qa_pairs(qa_pairs)

with open('formatted_datasetv4_complete.txt', 'w', encoding='utf-8') as outfile:
    outfile.write(formatted_dataset)
