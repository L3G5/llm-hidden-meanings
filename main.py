import click
from itertools import product
import os
import json
from datetime import datetime
import pandas as pd
import logging

import utils.encs as encs
import utils.llms as llms
import utils.util as util
import judges
import random

import dotenv
dotenv.load_dotenv(override=True)

# prefixes for constructing queries

# UNDERSTANDING_ENCODED_PREFIXES = ["say ", "repeat "]
UNDERSTANDING_ENCODED_PREFIXES = ["say "]
UNDERSTANDING_ENGLISH_PREFIXES = ["decipher ", ""]

# offset for considering words similar
MAX_LEVENSTEIN_OFFSET = 4

# maximum parameters to test during the understanding phase 
# MAX_PARAMS_UNDERSTANDING = 16*16
MAX_PARAMS_UNDERSTANDING = 10_000


logging.getLogger().setLevel(logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

def run_tests_understanding(encoding_types: list, model: str, prompts_seed_dict: dict[str, str], max_params: int, **model_kwargs):
    logging.info(f"running {encoding_types} on {model}")
    model_class = llms.ModelTogether if model in util.TOGETHER_MODELS else llms.ModelNebius if model in util.NEBIUS_MODELS else llms.ModelGigaChat if 'GigaChat' in model else llms.ModelGPT if 'gpt' in model or 'o1' in model or 'o3' in model else llms.ModelClaude if 'claude' in model else llms.load_hf()
    target_llm = model_class(model)  
    
    prompts, prompts_enc, responses, params, params_tuples, prefixes, encoding_types_col = [], [], [], [], [], [], []
    prompts_seed_dict_parsed = {k: v.split('|') for k, v in prompts_seed_dict.items()}
    prompts_seed = list(prompts_seed_dict.keys())
    
    for encoding_type in encoding_types:
        print(encoding_type)
        config = encs.ENCODING_CONFIG[encoding_type]
        encoder_func = config['encoder']
        param_names = config['param_names']
        encoding_params = list(config['params_range'])
        
        # if len(encoding_params) > max_params:
        #     encoding_params = random.sample(encoding_params, max_params)
        cur_params = 0
        for param_values in encoding_params:
            enc = encoder_func(*param_values)
            if ("�" in enc("abra")):
                continue
            cur_params += 1
            if cur_params > max_params:
                break
            for enc_prefix, eng_prefix in product(UNDERSTANDING_ENCODED_PREFIXES, UNDERSTANDING_ENGLISH_PREFIXES):
                prompts.extend(p for p in prompts_seed)
                params.extend(dict(zip(param_names, param_values)) for p in prompts_seed)
                params_tuples.extend(tuple(param_values) for p in prompts_seed)
                prefixes.extend((enc_prefix, eng_prefix) for p in prompts_seed)
                prompts_enc.extend(eng_prefix + enc(enc_prefix+p) for p in prompts_seed)
                encoding_types_col.extend(encoding_type for p in prompts_seed)
    
    responses = target_llm.get_responses(
        msgs=prompts_enc,
        **model_kwargs,
    )
    with open(f"responses_{datetime.now().strftime('%d_%m_%Y__%H_%M_%S')}.json", 'w') as f:
        json.dump(responses, f, ensure_ascii=False)
        
    df_res = pd.DataFrame(responses)
    df_res = pd.concat([pd.DataFrame(list(zip(prompts, encoding_types_col, params, params_tuples, prefixes, prompts_enc)), columns= ['prompt', 'encoding_type', 'params', 'params_tuples', 'prefixes', 'prompt_enc']), df_res], axis = 1)
    judgements =  [
            judges.judge_understanding(
                resp,
                rule,
                MAX_LEVENSTEIN_OFFSET
            )
            for resp, rule in zip(
                df_res["content"], df_res["prompt"].map(prompts_seed_dict_parsed)
            )
        ]
    df_res["best_words"], df_res["best_scores"], df_res["understood"] = list(zip(*judgements))

    return df_res

@click.command()
@click.option('--model', type=str, required=True, help='Model to use for the test.')
@click.option('--encodings', type=str, default = None, help='Model to use for the test.')
@click.option('--understanding-data', type=str, default='data/understanding_test.csv', help='CSV file with data used for understanding evaluation.')
@click.option('--max-tokens', type=int, default=200, help='Max tokens used during understanding evaluation.')
@click.option('--max-params', type=int, default=MAX_PARAMS_UNDERSTANDING, help='Max parameters to use for each encoding during understanding evaluation.')
@click.option('--log-dir', type=str, default='logs', help='Directory to store logs.')
@click.option('--seed', type=int, default=None, help='Fix seed to seed.')
def main(model, encodings, understanding_data, max_tokens, max_params, log_dir, seed):
    logging.info(f"{model=}, {encodings=}, {understanding_data=}, {max_tokens=}, {max_params=}, {log_dir=}, {seed=}")
    if seed:
        random.seed(seed)
    
    prompts_seed_dict = pd.read_csv(understanding_data, index_col="word").to_dict()['rules']
    model_kwargs = util.MODEL_CONFIGS.get(model, {})
    
    log_data = {}
    log_data['metadata'] = dict(model = model, understanding_data = prompts_seed_dict, max_tokens = max_tokens, max_params = max_params, seed = seed, model_kwargs = model_kwargs)
    
    if encodings:
        encoding_types = encodings.split('|')
    else:
        encoding_types = ["2b", "3b", "4b"]
        # encoding_types = list(encs.ENCODING_CONFIG.keys())
        # encodings = "|".join(encoding_types)
    result = run_tests_understanding(
        encoding_types=encoding_types, model=model, prompts_seed_dict = prompts_seed_dict, max_tokens = max_tokens, max_params=max_params, **model_kwargs
    )
    understanding_rate = float(result['understood'].mean())
    logging.info(f"{understanding_rate=}")
    log_data["understanding_rate"] = understanding_rate
    # log_data[encoding_type]["understanding_rate_by_prefix"] = result.groupby(['prefixes'])['understood'].mean().sort_values(ascending=False).to_dict()
    # log_data[encoding_type]["understanding_rate_by_params"] = result.groupby(['params_tuples'])['understood'].mean().sort_values(ascending=False).to_dict()
    log_data["artifacts"] = result.to_dict(orient='records')

    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"{timestamp}_{model.split('/')[-1]}_{encodings}_{max_tokens}_{max_params}_{seed}_understanding.json")
    with open(log_file, 'w') as f:
        json.dump(log_data, f, ensure_ascii=False)

if __name__ == '__main__':
    main()