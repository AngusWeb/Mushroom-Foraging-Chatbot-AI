import pdfplumber
import spacy
import tiktoken
import os

# Load spaCy model
nlp = spacy.load('en_core_web_sm')

# Prompt the user to input the OpenAI API key
openai_api_key = input("Please enter your OpenAI API key: ")

# Define the model name and pricing
MODEL_NAME = 'chatgpt4o-mini'
INPUT_PRICE_PER_1K = 0.000150          # Price per 1K input tokens
CACHED_INPUT_PRICE_PER_1K = 0.000075   # Price per 1K cached input tokens
OUTPUT_PRICE_PER_1K = 0.000600         # Price per 1K output tokens

def extract_text_from_pdfs(pdf_files):
    text_data = ""
    for pdf_file in pdf_files:
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_data += text + "\n"
    return text_data

def split_text_with_spacy(text, max_length=500):
    doc = nlp(text)
    chunks = []
    current_chunk = ""
    for sent in doc.sents:
        if len(current_chunk) + len(sent.text) <= max_length:
            current_chunk += " " + sent.text
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sent.text
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

def estimate_tokens_and_costs(text_chunks):
    total_input_tokens = 0
    total_output_tokens = 0

    # Initialize tiktoken encoding
    encoding = tiktoken.encoding_for_model('gpt-4o-mini')  # Use a compatible encoding

    for chunk in text_chunks:
        prompt = f"""
You are a helpful assistant specialized in generating question-answer pairs from given text excerpts.

Text:
\"\"\"
{chunk}
\"\"\"

Please generate a relevant question that could be answered by the text above, and provide the answer.

Format:
Question: [Your question]
Answer: [The answer]
"""
        # Token count for the prompt (input tokens)
        input_tokens = len(encoding.encode(prompt))
        total_input_tokens += input_tokens

        # Simulate average response tokens 
        average_output_tokens = 150
        total_output_tokens += average_output_tokens

    # Estimate costs
    # For simplicity, we'll assume all input tokens are uncached
    total_input_cost = (total_input_tokens / 1000) * INPUT_PRICE_PER_1K
    total_output_cost = (total_output_tokens / 1000) * OUTPUT_PRICE_PER_1K
    total_cost = total_input_cost + total_output_cost

    print(f"Estimated input tokens: {total_input_tokens}")
    print(f"Estimated output tokens: {total_output_tokens}")
    print(f"Estimated total tokens: {total_input_tokens + total_output_tokens}")
    print(f"Estimated input cost: ${total_input_cost:.6f}")
    print(f"Estimated output cost: ${total_output_cost:.6f}")
    print(f"Estimated total cost: ${total_cost:.6f}")

    return total_input_tokens, total_output_tokens

def simulate_qa_pairs(text_chunks):
    qa_pairs = []

    # Simulate generating question-answer pairs
    for i, chunk in enumerate(text_chunks):
        question = f"Simulated question {i+1} based on the provided text."
        answer = f"Simulated answer {i+1} providing information extracted from the text."
        qa_pairs.append((question, answer))

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
text_chunks = split_text_with_spacy(raw_text, max_length=500)
estimate_tokens_and_costs(text_chunks)
qa_pairs = simulate_qa_pairs(text_chunks)
formatted_dataset = format_qa_pairs(qa_pairs)

with open('formatted_dataset.txt', 'w', encoding='utf-8') as outfile:
    outfile.write(formatted_dataset)
