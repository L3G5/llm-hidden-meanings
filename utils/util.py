import pandas as pd
import json

def extract_data(item):
    row = {}
    
    row['created'] = item.get('created', '')
    row['model'] = item.get('model', '')
    # row['object'] = item.get('object', '')
    
    choices = item.get('choices', [])
    if choices:
        choice = choices[0]
        
        message = choice.get('message', {})
        content = message.get('content', '')
        # role = message.get('role', '')
        # index = choice.get('index', '')
        finish_reason = choice.get('finish_reason', '')
        
        usage = item.get('usage', {})
        # prompt_tokens = usage.get('prompt_tokens', '')
        # completion_tokens = usage.get('completion_tokens', '')
        # total_tokens = usage.get('total_tokens', '')
        
        row.update({
            'content': content,
            # 'role': role,
            # 'index': index,
            'finish_reason': finish_reason,
            'usage': usage,
            # 'prompt_tokens': prompt_tokens,
            # 'completion_tokens': completion_tokens,
            # 'total_tokens': total_tokens
        })
    
    return row

def queries_and_answers(prompts, res, prompts_cols = None):
    return pd.concat([pd.DataFrame(prompts, columns= ['prompt'] if isinstance(prompts[0], str) else prompts_cols), pd.DataFrame(extract_data(res))], axis=1) 

def jsonl_to_df(name):
    lines = []
    with open(name) as f:
        lines = f.read().splitlines()

    line_dicts = [json.loads(line) for line in lines]
    return pd.DataFrame(line_dicts)
