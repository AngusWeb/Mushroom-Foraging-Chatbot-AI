import pdfplumber
import re
from openai import OpenAI

if False:
    client = OpenAI(
        api_key=input("Please enter your OpenAI API key: "), 
    )
import pdfplumber
import spacy


# Load spaCy model
nlp = spacy.load('en_core_web_sm')

def extract_text_from_pdfs(pdf_files):
    text_data = ""
    for pdf_file in pdf_files:
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    # Normalise line breaks and spaces
                    text = text.replace('\r\n', '\n').replace('\r', '\n')
                    text_data += text + "\n"
    return text_data

def split_text_into_chunks(text, min_words=100, max_words=300):
    """
    Splits the input text into chunks that are optimal for generating question-answer pairs.
    Each chunk is between min_words and max_words and maintains semantic coherence.

    Args:
        text (str): The input text to split.
        min_words (int): Minimum number of words per chunk.
        max_words (int): Maximum number of words per chunk.

    Returns:
        List[str]: A list of text chunks.
    """
    # Preprocess the text
    text = preprocess_text(text)
    
    # Use spaCy to process the text
    doc = nlp(text)
    
    chunks = []
    current_chunk = ''
    current_chunk_word_count = 0

    for sent in doc.sents:
        sent_text = sent.text.strip()
        if not sent_text:
            continue

        words_in_sent = len(sent_text.split())
        if (current_chunk_word_count + words_in_sent > max_words) and (current_chunk_word_count >= min_words):
            # Save current chunk and start new one
            chunks.append(current_chunk.strip())
            print(current_chunk.strip())
            current_chunk = sent_text + ' '
            current_chunk_word_count = words_in_sent
            
            print('\n-----------------------------------')
        else:
            current_chunk += sent_text + ' '
            current_chunk_word_count += words_in_sent

    # Add the last chunk
    if current_chunk:
        chunks.append(current_chunk.strip())
    print(len(chunks))
    return chunks


def preprocess_text(text):
    """
    Preprocesses the text by removing non-essential content and normalizing whitespace.

    Args:
        text (str): The text to preprocess.

    Returns:
        str: The preprocessed text.
    """
    # Remove figure references like '(see page 41)'
    text = re.sub(r'\(see page \d+\)', '', text)
    # Remove multiple newlines
    text = re.sub(r'\n+', ' ', text)
    # Remove multiple spaces
    text = re.sub(r' {2,}', ' ', text)
    return text

def is_heading(paragraph):
    """
    Determines if a paragraph is a heading based on simple heuristics.

    Args:
        paragraph (str): The paragraph to check.

    Returns:
        bool: True if the paragraph is a heading, False otherwise.
    """
    # Lines that are short and in title case are considered headings
    lines = paragraph.strip().split('\n')
    if len(lines) == 1:
        line = lines[0]
        # If line is in title case and less than 10 words
        if len(line.split()) < 10 and line == line.title():
            return True
    return False


def generate_qa_pairs(text_chunks):
    qa_pairs = []
    for chunk in text_chunks:
        prompt = f"""
You are an expert assistant specialized in creating educational question-answer pairs from the provided text excerpt about mushroom picking.

Text:
\"\"\"
{chunk}
\"\"\"

Your task is to:

1. Read the text carefully.
2. Generate a clear and concise question that focuses on a key piece of information or concept presented in the text.
3. Provide an accurate answer to the question, based solely on the information given in the text.

Please format your response exactly as follows:

Question: [Your question]

Answer: [Your answer]
"""
        try:
            response = client.chat.completions.create(
                model='gpt-4o-mini',
                messages=[{'role': 'user', 'content': prompt}],
                temperature=0.7,
            )
            # Access the content from the response
            content = response.choices[0].message.content
            if 'Question:' in content and 'Answer:' in content:
                question = content.split('Question:')[1].split('Answer:')[0].strip()
                answer = content.split('Answer:')[1].strip()
                qa_pairs.append((question, answer))
                print(question)
                
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
raw_text = extract_text_from_pdfs(pdf_files)

text_chunks = split_text_into_chunks(raw_text)


quit(1)
qa_pairs = generate_qa_pairs(text_chunks)
formatted_dataset = format_qa_pairs(qa_pairs)

with open('formatted_datasetv2.txt', 'w', encoding='utf-8') as outfile:
    outfile.write(formatted_dataset)
