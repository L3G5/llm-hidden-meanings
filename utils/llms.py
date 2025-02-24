import os
import openai
import anthropic
import httpx
import time
import json
import uuid
import utils.util as util
from tqdm import tqdm
import logging
import together

class ModelGigaChat:
    def __init__(self, model_name):
        self.model_name = model_name
        self.http_client = httpx.Client(verify=os.getenv("CERT_PATH")) 
        self.client = openai.OpenAI(api_key=self.get_giga_auth(), http_client=self.http_client, base_url = os.getenv("GIGACHAT_URL"))
        self.reobtain_time = time.time() + 27*60
        
    def get_giga_auth(self, GIGA_AUTH = os.getenv("GIGACHAT_API_KEY")):
        url = os.getenv("GIGACHAT_ACCESS_URL")
        rquid = str(uuid.uuid4())
        payload = os.getenv("GIGACHAT_PAYLOAD")
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "RqUID": rquid,
            "Authorization": "Basic " + GIGA_AUTH,
        }

        response = httpx.request(
            "POST",
            url,
            headers=headers,
            data=payload,
            verify=os.getenv("CERT_PATH"),
        )
        return response.json()["access_token"]

    def get_responses(self, msgs, **kwargs):
        
        GENERATION_DEFAULT_ARGS = {
            "max_tokens": 100,
            "temperature": 0.7,
        }

        responses = []
        
        for prompt in tqdm(msgs): 
            if time.time() > self.reobtain_time:
                self.client = openai.OpenAI(api_key=self.get_giga_auth(), http_client=self.http_client, base_url = os.getenv("GIGACHAT_URL"))
                self.reobtain_time = time.time() + 27*60
            payload = dict(**GENERATION_DEFAULT_ARGS)
            payload.update(kwargs)
            msg = [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
            responses.append(
                self.parse_response(
                    self.client.chat.completions.create(model = self.model_name, messages = msg, **payload)  
                    )
                )

        return responses
    def parse_response(self, response):
        return util.extract_data(response.to_dict())

class ModelGPT:
    def __init__(self, model_name, env = "OPENAI_API_KEY", batch_completed_status = "completed"):
        self.model_name = model_name
        self.client = openai.OpenAI(api_key=os.getenv(env))
        self.batch_completed_status = batch_completed_status


    def create_batch_file(self, prompts, input_file_nm, **kwargs):
        """
        Create a JSONL file for the batch API input.
        """
        batch_input = []
        for prompt in prompts:
            body = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": prompt}],
            }
            for k in ["temperature", "seed"]:
                v = kwargs.get(k, None)
                if v:
                    body[k] = v
            if self.model_name == "o1" or self.model_name == "o3-mini":
                for k in ["max_tokens"]:
                    v = kwargs.get(k, None)
                    if v and v < 150:
                        body['reasoning_effort'] = "low"
                    elif v and v < 1500:
                        body['reasoning_effort'] = "medium"
                    elif v and v >= 1500:
                        body['reasoning_effort'] = "high"
            elif self.model_name == "o1-mini":
                for k in ["max_tokens"]:
                    v = kwargs.get(k, None)
                    if v:
                        body["max_completion_tokens"] = v
            else:
                for k in ["max_tokens"]:
                    v = kwargs.get(k, None)
                    if v:
                        body[k] = v
            request = {
                "custom_id": str(uuid.uuid4()),
                "method": "POST", 
                "url": "/v1/chat/completions", 
                "body": body
            }
            batch_input.append(request)

        # Save the batch input to a JSONL file
        with open(input_file_nm, "w") as f:
            for request in batch_input:
                f.write(json.dumps(request) + "\n")
            logging.info(request)
        batch_input_file = self.client.files.create(
            file=open(input_file_nm, "rb"),
            purpose="batch"
        )
        return batch_input_file

    def submit_batch(self, batch_input_file):
        """
        Submit the batch job to OpenAI.
        """
        batch = self.client.batches.create(
            input_file_id=batch_input_file.id,
            endpoint="/v1/chat/completions",
            completion_window="24h",
        )
        # logging.info(batch)
        return batch.id

    def check_batch_status(self, batch_id):
        """
        Check the status of the batch job.
        """
        batch = self.client.batches.retrieve(batch_id)
        logging.info(f"{batch.status=}, {batch.request_counts=}")
        return batch.status

    def download_batch_results(self, batch_id, output_file):
        """
        Download the results of the batch job.
        """
        batch = self.client.batches.retrieve(batch_id)
        # print(batch)
        if batch.status == self.batch_completed_status:
            file_response = self.client.files.content(batch.output_file_id)
            with open(output_file, "w") as f:
                f.write(file_response.text)
            return True
        return False

    def get_responses(self, msgs, **kwargs):
        """
        Get responses for a batch of prompts using the OpenAI Batch API.
        """
        input_file_nm = "batch_input.jsonl"
        input_file = self.create_batch_file(msgs, input_file_nm, **kwargs)
        
        batch_id = self.submit_batch(input_file)
        print(f"Batch submitted. Batch ID: {batch_id}")
        
        while True:
            status = self.check_batch_status(batch_id)
            # print(f"Batch status: {status}")
            if status == self.batch_completed_status:
                break
            time.sleep(60)  # Wait 1 minute before checking again
        
        output_file_nm = "batch_output.jsonl"
        if self.download_batch_results(batch_id, output_file_nm):
            df = util.jsonl_to_df(input_file_nm).merge(util.jsonl_to_df(output_file_nm), how = 'left', on = 'custom_id')
            return [self.parse_response(r) for r in df['response'].tolist()]
        else:
            print("Batch processing failed.")
            return [""] * len(msgs)

    def parse_response(self, response):
        return util.extract_data(response['body'])

class ModelClaude:
    def __init__(self, model_name):
        self.model_name = model_name
        self.client = anthropic.Client(api_key=os.getenv("ANTHROPIC_API_KEY"))

    def create_batch_file(self, prompts, input_file_nm, **kwargs):
        """
        Create a JSONL file for the batch API input.
        """
        batch_input = []
        for prompt in prompts:
            body = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": prompt}],
            }
            for k in ["max_tokens", "temperature", "seed"]:
                v = kwargs.get(k, None)
                if v:
                    body[k] = v
            if self.model_name == "claude-3-7-sonnet-20250219":
                body["thinking"] = {
                    "type": "disabled",
                }

            request = {
                "custom_id": str(uuid.uuid4()),
                "params": body
            }
            batch_input.append(request)
        
        # Save the batch input to a JSONL file
        with open(input_file_nm, "w") as f:
            for request in batch_input:
                f.write(json.dumps(request) + "\n")

        batch_input_file = self.client.messages.batches.create(
            requests=batch_input,
        )
        # logging.info(batch_input_file)
        return batch_input_file.id

    def check_batch_status(self, batch_id):
        """
        Check the status of the batch job.
        """
        batch = self.client.messages.batches.retrieve(batch_id)
        logging.info(f"{batch.processing_status=} {batch.request_counts.to_dict()=}")
        return batch.processing_status

    def download_batch_results(self, batch_id, output_file):
        """
        Download the results of the batch job.
        """
        batch = self.client.messages.batches.retrieve(batch_id)
        if batch.processing_status == "ended":
            file_response = self.client.messages.batches.results(batch_id)
            with open(output_file, "w") as f:
                for line in file_response:
                    f.write(json.dumps(line.to_dict())+'\n')
            return True
        return False

    def get_responses(self, msgs, **kwargs):
        """
        Get responses for a batch of prompts using the Anthropic Batch API.
        """
        input_file_nm = "batch_input_a.jsonl"
        batch_id = self.create_batch_file(msgs, input_file_nm, **kwargs)
        
        print(f"Batch submitted. Batch ID: {batch_id}")
        
        while True:
            status = self.check_batch_status(batch_id)
            # print(f"Batch status: {status}")
            if status == "ended":
                break
            time.sleep(60)  # Wait 1 minute before checking again
        
        output_file_nm = "batch_output_a.jsonl"
        if self.download_batch_results(batch_id, output_file_nm):
            df = util.jsonl_to_df(input_file_nm).merge(util.jsonl_to_df(output_file_nm), how = 'left', on = 'custom_id')
            return [self.parse_response(r['message']) for r in df['result'].tolist()]
        else:
            print("Batch processing failed.")
            return [""] * len(msgs)
        
    def parse_response(self, response):
        parsed = {
            'created': int(time.time()),
            'content': response['content'][0]["text"],
            'model': response['model'],
            'finish_reason': response['stop_reason'],
            'usage': response['usage'],
        }
        return parsed

class ModelTogether:
    def __init__(self, model_name):
        self.model_name = model_name
        self.client = together.Together(api_key=os.getenv("TOGETHER_API_KEY"))

    def get_responses(self, msgs, **kwargs):
        """
        Get responses for a list of prompts using the Together API.
        Respects the rate limit of 60 RPM by sleeping for 1 second after each request.
        """
        responses = []
        sleep_time = kwargs.get('sleep', 1)
        print(sleep_time)
        for prompt in tqdm(msgs):
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    **kwargs
                )
                responses.append(self.parse_response(response))
            except Exception as e:
                print(f"Error processing prompt: {prompt}. Error: {e}")
                responses.append("")
            
            # Sleep for 1 second to respect the 60 RPM rate limit
            time.sleep(sleep_time)
        
        return responses
    
    def parse_response(self, response):
        return util.extract_data(response.model_dump())

class ModelNebius(ModelGPT):
    def __init__(self, model_name):
        super().__init__(model_name, env = "NEBIUS_API_KEY", batch_completed_status = "done")
        self.client.base_url="https://api.studio.nebius.com/v1/"
    def parse_response(self, response):
        return util.extract_data(response)

def load_hf():
    import utils.llms_hf as llms_hf
    return llms_hf.ModelHuggingFace
# import torch
# from transformers import AutoModelForCausalLM, AutoTokenizer
# class ModelHuggingFace:
#     def __init__(self, model_name):
#         model_dict = {
#             "phi3": "microsoft/Phi-3-mini-128k-instruct",
#             "gemma2-9b": "google/gemma-2-9b-it",
#             "llama3-8b": "meta-llama/Meta-Llama-3-8B-Instruct",
#             "r2d2": "cais/zephyr_7b_r2d2",
#         }
#         self.system_prompts = {
#             "phi3": "You are a helpful AI assistant.",
#             "gemma2-9b": "",
#             "llama3-8b": "You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature. If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don’t know the answer to a question, please don’t share false information.",
#             "r2d2": "A chat between a curious human and an artificial intelligence assistant. The assistant gives helpful, detailed, and polite answers to the human’s questions.",
#         }
#         self.device = torch.device("cuda")
#         self.model_name = model_name
#         self.model = AutoModelForCausalLM.from_pretrained(model_dict[model_name], torch_dtype=torch.float16, device_map=self.device,token=os.getenv("HF_TOKEN"), trust_remote_code=True).eval()
#         self.tokenizer = AutoTokenizer.from_pretrained(model_dict[model_name], token=os.getenv("HF_TOKEN"))

#     def get_response(self, prompt, max_n_tokens, temperature):
#         conv = [{"role": "user", "content": prompt}]
#         if self.system_prompts[self.model_name] != "":
#             conv = [{"role": "system", "content": self.system_prompts[self.model_name]}] + conv
#         prompt_formatted = self.tokenizer.apply_chat_template(conv, tokenize=False, add_generation_prompt=True)
#         inputs = self.tokenizer(prompt_formatted, return_tensors='pt').to(self.device)

#         outputs = self.model.generate(input_ids=inputs['input_ids'], max_new_tokens=max_n_tokens, temperature=temperature, do_sample=True)
#         outputs_truncated = outputs[0][len(inputs['input_ids'][0]):]
#         response = self.tokenizer.decode(outputs_truncated, skip_special_tokens=True)

#         return response
