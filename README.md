# 🧠 Jay - Desktop AI Assistant
## Description

A cute, draggable, AI-powered desktop assistant built with Python, Tkinter, and Ollama. Click the floating character to open the chat bubble. As default, it is powered by `Meta Llama 3.2`, running locally.

## Features

- 🧩 Tiny floating assistant with click-to-chat interface
- 💬 AI responses powered by `Meta Llama 3.2` (You can change!)
- 🤖 Multi-model support, you can change the model and try out different models from Ollama!
- 🪟 Lightweight GUI using `tkinter`
- 🧵 Multithreaded design to avoid GUI freezing
- 💻 Runs locally, no API keys required!

## 🛠️ Installation

1. Clone the repository

```sh
git clone https://github.com/yegekucuk/jay.git
cd jay
```

2. Install dependencies

```sh
# For virtual environment (optional but recommended):
python -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

3. Pull the model Llama3.2
```sh
ollama pull llama3.2:3b
```
- Note: Make sure [Ollama](https://github.com/ollama/ollama) is installed and running.
- Note: You can edit the model name in `main.py` to use any supported Ollama model.

## 🚀 Usage

```sh
# If you use virtual environment:
source venv/bin/activate

python src/main.py
```

The assistant will appear in the bottom-right corner of your screen. Click on it to start chatting!

Right-click the character to:
- Toggle the chat bubble
- Close the application

## 📄 License

Built by [Yunus Ege Küçük](https://github.com/yegekucuk). The software is licensed under the GPL-3 License.

Meta Llama 3 is licensed under the [Meta Llama 3 Community License](https://github.com/meta-llama/llama3/blob/main/LICENSE), Copyright © Meta Platforms, Inc. All Rights Reserved. This is a personal project and this project is not affiliated with or endorsed by Meta.
