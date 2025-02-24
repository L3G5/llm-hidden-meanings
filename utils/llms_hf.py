from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from tqdm import tqdm
import time
from datetime import datetime

class ModelHuggingFace:
    def __init__(self, model_name, device_map="sequential"):
        self.model_name = model_name
        self.device_map = device_map
        self.model = AutoModelForCausalLM.from_pretrained(model_name, device_map=device_map)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False)
        self.tokenizer.pad_token = self.tokenizer.eos_token  # Set pad token
    def parse_response(self, output, input_prompt):
        """
        Parse the model's output to remove the input prompt and clean the response.
        """
        decoded_output = self.tokenizer.decode(output, skip_special_tokens=False)

        # Remove the input prompt from the decoded output
        if input_prompt in decoded_output:
            assistant_response = decoded_output.split(input_prompt)[-1].strip()
        else:
            assistant_response = decoded_output.strip()

        # Clean up special tokens or unwanted artifacts
        assistant_response = (
            assistant_response
                .replace('<|begin_of_text|>', '')
                .replace('<|start_header_id|>system<|end_header_id|>', '')
                .replace('<|start_header_id|>assistant<|end_header_id|>', '')
                .replace('<|start_header_id|>user<|end_header_id|>', '')
                .replace('<|eot_id|>', '').strip()
                .replace('<|end_of_text|>', '').strip()
                )

        return assistant_response

    def format_response(self, content, finish_reason="stop"):
        """
        Format the response to match the structure expected by `extract_data`.
        """
        return {
            "created": int(datetime.now().timestamp()),
            "model": self.model_name,
            "content": content,
            "usage": {
                "prompt_tokens": 0,  # Placeholder, update if token counts are available
                "completion_tokens": 0,  # Placeholder
                "total_tokens": 0  # Placeholder
            }
        }

    def get_responses(self, msgs, **kwargs):
        """
        Get responses for a list of prompts using the Hugging Face model.
        Processes prompts in batches to improve efficiency.
        """
        batch_size=kwargs.get("batch_size",20)
        kwargs_real = {
            # "batch_size": kwargs.get("batch_size",20),
            "max_new_tokens": kwargs.get("max_tokens",200),
        }
        responses = []
        for i in tqdm(range(0, len(msgs), batch_size)):
            batch = msgs[i:i + batch_size]
            try:
                # Apply chat template to each prompt in the batch
                formatted_prompts = [
                    self.tokenizer.apply_chat_template(
                        [{"role": "user", "content": prompt}],
                        truncation=True,
                        add_generation_prompt=True,
                        tokenize = False
                    )
                    for prompt in batch
                ]

                # Tokenize the formatted prompts in a single step
                inputs = self.tokenizer(
                    formatted_prompts,
                    padding=True,
                    truncation=True,
                    return_tensors="pt"
                ).to(self.model.device)

                # Generate responses for the batch
                outputs = self.model.generate(
                    inputs.input_ids,
                    attention_mask=inputs.attention_mask,  # Include attention mask
                    # max_new_tokens=1512,
                    do_sample=True,
                    temperature=0.3,
                    top_k=50,
                    top_p=0.95,
                    **kwargs_real
                )

                # Decode and format each response in the batch
                for j in range(len(batch)):
                    # Parse the response to remove the input prompt
                    assistant_response = self.parse_response(outputs[j], batch[j])
                    formatted_response = self.format_response(assistant_response)
                    responses.append(formatted_response)

            except Exception as e:
                print(f"Error processing batch starting at index {i}. Error: {e}")
                responses.extend([self.format_response("")] * len(batch))  # Append empty responses for failed prompts
        return responses
