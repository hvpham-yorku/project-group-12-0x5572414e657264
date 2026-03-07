TO RUN IN VSCODE:

While in the src folder run:
    python -m src.main
    python -X faulthandler -m src.main


To compile windows exe:
python.exe -m PyInstaller --noconfirm --clean --onefile --windowed --name StoreFlowAnalytics_0.0.1 src\main.py

To compile macOS:
python -m PyInstaller --noconfirm --clean --onefile --windowed --name StoreFlowAnalytics_0.1.1 src/main.py