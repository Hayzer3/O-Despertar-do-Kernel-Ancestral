import os
import sys

# Esse script apenas redireciona para o Streamlit
from streamlit.web.cli import main

if __name__ == "__main__":
    sys.argv = [
        "streamlit",
        "run",
        "main.py",
        "--server.port",
        "8501",
        "--server.address",
        "0.0.0.0",
    ]
    main()