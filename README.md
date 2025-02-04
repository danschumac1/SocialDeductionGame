- conda create -n raylibPyEnv
- conda activate raylibPyEnv
- python -m pip install --upgrade pip
- python -m pip install setuptools
- pip install raylib-py
- pip install fastapi uvicorn websockets streamlit


wsl 
tmux new -s messaging_server
conda activate raylibEnv <- may need to repeat above
python3 ./src/server.py

- python ./src/main.py


########################
might be necessary
#######################
# if windows
wsl --install
# Once inside WSL
sudo apt update
sudo apt install tmux

# if mac
brew install tmux

# if linux
sudo apt update
sudo apt install tmux
