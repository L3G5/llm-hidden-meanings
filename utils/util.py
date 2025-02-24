import pandas as pd
import json
from IPython.display import display

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

def load_log(path: str = "logs/20250222_221246_claude-3-5-sonnet-20241022_2b|3b|4b_200_10000_None_understanding.json"):
    with open(path) as f:
        results = json.load(f)
    return pd.DataFrame(results['artifacts'])

def filter_unc(df: pd.DataFrame):
    return df.loc[~df['prompt_enc'].apply(lambda x: "�" in x)]

def display_table(df: pd.DataFrame, max_colwidth = None, max_columns = 50, max_rows = 50):
    with pd.option_context('display.max_colwidth', max_colwidth, 'display.max_columns', max_columns, 'display.max_rows', max_rows):
        display(df)
