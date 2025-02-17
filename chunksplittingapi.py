from openai import OpenAI
import PyPDF2
import nltk
from nltk.tokenize import sent_tokenize
import tiktoken
import time

client = OpenAI(
    api_key=input("Please enter your OpenAI API key: "),  
)

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()
    return text

def count_tokens(text, encoding_name='cl100k_base'):
    """Counts the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(text))
    return num_tokens

def split_text_into_initial_chunks(text, max_tokens=2000):
    """Splits text into initial chunks based on token count."""
    nltk.download('punkt', quiet=True)
    sentences = sent_tokenize(text)
    chunks = []
    current_chunk = ''
    for sentence in sentences:
        if count_tokens(current_chunk + ' ' + sentence) <= max_tokens:
            current_chunk += ' ' + sentence
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

def get_optimal_chunks(text_chunk):
    """Uses OpenAI API to split text into optimal chunks."""
    prompt = f"""
    Please split the following text into smaller, self-contained chunks suitable for creating meaningful and contextually relevant question-answer pairs. Each chunk should be numbered and contain a complete idea, including all necessary context to make sense on its own, even if it requires repeating information from previous chunks. Do not include any questions, answers, or additional commentary.

    **Important Instructions:**

    - **Eliminate References to the Book:** Rephrase any mentions of 'this book', 'the previous section', or similar phrases to ensure each chunk makes sense independently.

    - **Include Necessary Context:** Ensure that pronouns like 'these', 'they', or 'it' have clear antecedents within the chunk. Replace them with specific nouns if necessary.

    - **Maintain Optimal Length and Style:** Each chunk should be concise yet comprehensive enough to form a meaningful question-answer pair.

    **Example Output:**

    Chunk 1: [First segment]

    Chunk 2: [Second segment]

    ...

    **Here is the text to split:**

    {text_chunk}
    """
    try:
        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=10000,
            temperature=0.5,
        )
        content = response.choices[0].message.content
        return content
    except Exception as e:
        print(f"An error occurred: {e}")
        time.sleep(5)  # Wait before retrying
        return get_optimal_chunks(text_chunk)

def parse_response(response_text):
    """Parses the API response to extract chunks."""
    chunks = []
    lines = response_text.strip().split('\n')
    current_chunk = ''
    for line in lines:
        if line.strip() == '':
            continue
        if line.lower().startswith(('chunk', 'segment', 'section', 'part', 'paragraph', 'passage')):
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = ''
            current_chunk += line
        else:
            current_chunk += ' ' + line
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

def process_pdf(pdf_path):
    """Processes the PDF and returns optimal text chunks."""
    text = extract_text_from_pdf(pdf_path)
    initial_chunks = split_text_into_initial_chunks(text)
    optimal_chunks = []
    for idx, chunk in enumerate(initial_chunks):
        print(f'Processing initial chunk {idx+1}/{len(initial_chunks)}...')
        response = get_optimal_chunks(chunk)
        split_chunks = parse_response(response)
        optimal_chunks.extend(split_chunks)
    return optimal_chunks

if __name__ == '__main__':
    if False:
        pdf_path = 'Jens_H_Petersen.pdf'  
        optimal_chunks = process_pdf(pdf_path)
        # Save the optimal chunks to a text file
        with open('optimal_chunksv2.txt', 'w', encoding='utf-8') as f:
            for idx, chunk in enumerate(optimal_chunks):
                f.write(f'Chunk {idx+1}:\n{chunk}\n\n')
        print("Processing complete. Optimal chunks have been saved to 'optimal_chunks.txt'.")

if True:
    import sys
    import os

    # List of PDF file paths
    pdf_paths = ['Jens_H_Petersen.pdf', 'BloomsburyConciseMushroomGuide.pdf', 'MushroomsComprehensiveGuidetoMushroomIdentification.pdf']  # 'Collinsfungiguide.pdf',

  

    # Open the output file once and append results from all PDFs
    with open('optimal_chunksv3.txt', 'w', encoding='utf-8') as f:
        for pdf_path in pdf_paths:
            print(f"Processing {pdf_path}...")
            optimal_chunks = process_pdf(pdf_path)
            f.write(f"Processing PDF: {pdf_path}\n")
            for idx, chunk in enumerate(optimal_chunks):
                f.write(f'Chunk {idx+1}:\n{chunk}\n\n')
            f.write("\n\n")
    print("Processing complete. Optimal chunks have been saved to 'optimal_chunksv2.txt'.")