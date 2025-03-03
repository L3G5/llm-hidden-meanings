# Your LLM might have more to say than you can understand

This is the code accompanying paper [2503.xxxxx](url), which presents a peculiar observations that LLMs can interpret gibberish texts as English.

I will clean this repository up later, but for now you can test your model using instructions in quick start (`main.py` for understanding test and `attack.py` for attack test). All the logs for understanding are availible at `logs` and for attacks at `logs/attack`.

## Quick start

To reproduce this evaluation you should first install the required packages. We recommend using `uv`

```bash
uv sync
```

and then run the tests for understanding like

```bash
uv run main.py --model <model_name> --seed 2025
```

To test for susceptibilty to attacks on [JBB dataset](https://huggingface.co/datasets/JailbreakBench/JBB-Behaviors), use

```bash
uv run attack.py --model <model_name> ...
```

The output will be a file you have to label, then you just have to calculate ASR.  


Currently OpenAI- and Anthropic- compatible clients are supported, as well as models from Together AI, Nebius and GigaChat. If you want to test another models, you should write an implementation for it in `utils/llm.py`. This implementation should have `get_responses` method which should return a list of dictionaries with fields `created, model, content, finish_reason`.


