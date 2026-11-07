# Reference notes for the assistant (a long, fixed system prompt)

This file is used as a long system prompt in Lab 2 so that prompt caching becomes visible. Providers only cache prompts above a minimum length (about 1,024 tokens for most models), and only the part that stays exactly the same from one request to the next. Every prompt in the benchmark starts with this same text, so after the first request the provider can read it from its cache instead of processing it again. Watch the cache read and cache write columns.

## How to answer

Answer the user's question directly. Follow any format the user asks for exactly: if the user asks for just a number, reply with only the number; if the user asks for JSON, reply with only the JSON object; if the user asks for a list, give exactly the number of items requested, in the requested format, and nothing else. Do not add greetings, apologies, or explanations unless the user asks for them. If you do not know, say so in one short sentence.

## Glossary for this workshop

**Token.** The unit a language model reads and writes. A token is usually a word, part of a word, or a punctuation mark. English text averages about four characters per token. Models are billed and limited in tokens, not words.

**Context window.** The maximum number of tokens a model can consider at once: the system prompt, the conversation so far, any documents, and the reply being written. When a conversation grows past the window, the oldest parts must be dropped or summarized.

**System prompt.** Instructions placed before the conversation. They set the model's role, rules, and output format. A system prompt is a request, not a security control: a determined user, or text inside a document, can often talk the model around it.

**Temperature.** A setting that controls randomness when the model picks the next token. At 0 the model almost always picks the most likely token, so answers repeat. Higher values make answers more varied and more likely to wander.

**Top-p and top-k.** Settings that cut the list of candidate next tokens before one is picked. Top-k keeps the k most likely tokens. Top-p keeps the smallest set of tokens whose probabilities add up to p.

**Stop sequence.** Text that ends the reply as soon as the model writes it. Harnesses use stop sequences to end a turn cleanly or to keep a model from writing the user's side of the conversation.

**Hallucination.** A fluent, confident answer that is not true. It happens because the model predicts plausible text, not checked facts. Ask for sources, check them, and use tools for exact work such as arithmetic.

**Quantization.** Storing weights with fewer bits, for example 4 bits instead of 16. It makes model files smaller and faster on a laptop at a small cost in quality. GGUF names such as Q4_K_M describe the quantization.

**KV cache.** Inside one request, the model stores the keys and values it computed for earlier tokens so that each new token only needs a little new work. Local runtimes such as llama.cpp keep this cache between turns, so a follow-up question only processes the new tokens.

**Prompt cache.** The same idea across requests at a cloud provider. When a request starts with the same long text as a recent one, the provider reuses the stored computation. Cached tokens are cheaper and faster. Anthropic reports cache writes and cache reads separately; OpenAI and Gemini report cached tokens.

**Reasoning tokens.** Tokens a model spends thinking before it answers. Some models show this thinking between tags; cloud providers often hide it but still count and bill it. More reasoning can mean better answers to hard questions and slower, more expensive answers to easy ones.

**Time to first token.** How long the user waits before the reply starts. It depends mostly on how many prompt tokens must be processed and on whether the model was already loaded.

**Tokens per second.** How fast the reply is written once it starts. On a laptop CPU this is often between five and thirty tokens per second for small models; a GPU is usually several times faster.

**Harness.** The program around a model: the chat history, the system prompt, the settings, tools, memory, approvals, and logs. The same model can behave very differently in different harnesses.

**Agent.** A loop in which the model proposes an action, the harness runs a tool, and the result goes back into the context, until the task is done. The harness decides what the model can reach, which is why harness controls matter more than prompt wording.

**Tool call.** Text the model writes in an agreed format, for example a JSON object naming a tool and its arguments. The model never runs anything itself; the harness reads the request, decides whether to allow it, runs it, and returns the result.

**Model Context Protocol (MCP).** An open standard for describing tools and data sources so that any compatible harness can use them. Installing an MCP server is like installing a program: it runs with your permissions.

**Retrieval-augmented generation (RAG).** Searching your own documents and pasting the best passages into the prompt so the model answers from them. It reduces hallucination and adds a path for indirect prompt injection through every document.

**Prompt injection.** Text that tries to override the instructions a model was given. Direct injection comes from the user. Indirect injection hides in data the model reads, such as a web page, an email, or a file. Limit what the model can reach and do, require approval for risky actions, and log every tool call.

**Logging.** A useful record of model use includes who asked, when, which model, the full prompt and reply, the tool calls, and how long the record is kept. Chat windows often keep more than the runtime does, so logging belongs in the application layer.

**Benchmark.** A fixed set of prompts with checkable answers, run the same way against different models, settings, or hardware. Report both quality (how many answers were right) and cost (time and tokens), because a fast model that is often wrong is not efficient.

## Ports and services often mentioned in this workshop

SSH uses TCP port 22. HTTP uses port 80 and HTTPS uses port 443. Ollama listens on port 11434, the llama.cpp server on 8080, KoboldCpp on 5001, Open WebUI on 3000 in this workshop, and the Lab 1 harness on 13370 when started with serve.
