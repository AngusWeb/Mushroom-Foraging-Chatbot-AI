# Mushroom Foraging Chatbot AI

A specialised chatbot for UK mushroom foraging built by fine-tuning the LLaMA 3.2-3B model. This project leverages a curated dataset of mycological literature, advanced fine-tuning techniques with LoRA adapters, and a user-friendly web interface to deliver an engaging and informative experience for mushroom enthusiasts.

---

## Project Overview

This project involves:
- **Fine-Tuning:** Adapting the LLaMA 3.2-3B model for a niche application in mushroom foraging.
- **Dataset Creation:** Building a comprehensive dataset from carefully selected mycological literature.
- **Training Implementation:** Utilising Google Colab, Unsloth for optimisation, and Hugging Face's TRL library to train the model.
- **Deployment:** Creating a ChatGPT-style interface with NextJS, local hosting via Ollama, and Twitter integration for broader accessibility.

---

## Model Selection

The LLaMA 3.2-3B model was chosen based on:
- **Performance:** A recent release with strong performance metrics.
- **Compactness:** A manageable 3B parameter size ideal for specialised tasks.
- **Licensing:** Free commercial licence.
- **Compatibility:** Works seamlessly with tools such as Unsloth and Ollama.

---

## Dataset Creation

The dataset was developed through a multi-stage process:

### 1. Source Material Selection
- **Initial Testing:** Began with a single book to validate the process.
- **Expansion:** Curated a collection of textbooks and field guides based on expert recommendations and Amazon reviews.
- **Quality Control:** Removed non-informational content (e.g., indexes, title pages) to ensure high-quality data.

### 2. Content Extraction and Processing
- **PDF Processing:** Utilised PyPDF2 for reading and processing PDFs.
- **Token Estimation:** Implemented a token cost estimation system.
- **Two-Stage Pipeline:**
  - **Extraction:** Employed ChatGPT-4-mini to extract fact chunks from the source materials.
  - **Q&A Generation:** Generated question-answer pairs from these chunks.
- **Data Formatting:** Iteratively refined prompts and formatted data to meet LLaMA’s conversation-style fine-tuning requirements.

### 3. Dataset Formatting
- Developed custom Python scripts to ensure compatibility with LLaMA’s expected input structure.
- Validated data quality and consistency across the dataset.

---

## Training Implementation

### Technical Stack
- **Environment:** Google Colab
- **Optimisation:** Unsloth
- **Fine-Tuning:** Hugging Face's TRL library
- **Frontend Development:** NextJS

### Training Process
1. **Dataset Conversion:** Read, parsed, and converted the dataset, and set up the tokenizer.
2. **Incorporating LoRA Adapters:** Enhanced model capabilities by adding LoRA adapters.
3. **Training:** Utilised Hugging Face's `SFTTrainer` and Unsloth's `train_on_completions` method to train the model—focusing on the assistant outputs while ignoring user input loss.
4. **Testing:** Employed a TextStreamer to evaluate the model's performance.
5. **Merging & Saving:** Merged the LoRA adapters into the base model and saved the final model in GGUF format, compatible with Ollama.

---

## Deployment

### Web Interface
- **Frontend:** Developed a ChatGPT-style interface using NextJS.
- **Model Hosting:** Hosted the model locally using Ollama.
- **Remote Access:** Demonstrated remote access with Ngrok's tunnel-based approach.

### Twitter Integration
- **Automated Presence:** Created an automated Twitter account for the chatbot.
- **API Interaction:** Utilised the Twikit Python library to integrate with the Twitter API.
- **Cost-Effective Access:** Implemented user spoofing for efficient API usage.
- **Integration:** Leveraged the existing API setup from the NextJS implementation.

---

## Conclusion

This project demonstrates the effective integration of advanced NLP techniques, specialised model fine-tuning, and modern web deployment to create a dedicated chatbot for mushroom foraging in the UK. By carefully curating a dataset, applying precise training methods, and deploying a user-friendly interface, the project delivers an AI assistant that serves as a valuable resource for mushroom enthusiasts.


