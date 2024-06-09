#!/bin/bash

# Clone the repository if it doesn't exist
if [ ! -d "Fooocus" ]; then
  git clone https://github.com/lllyasviel/Fooocus.git
fi

# Navigate into the repository and pull the latest changes
cd Fooocus
git pull

# Create a symbolic link to the Conda environment if it doesn't exist
if [ ! -L ~/.conda/envs/fooocus ]; then
    ln -s /tmp/fooocus ~/.conda/envs/
fi

# Initialize Conda in the script's shell
eval "$(conda shell.bash hook)"

# Create the Conda environment and install dependencies if it doesn't exist
if [ ! -d /tmp/fooocus ]; then
    mkdir /tmp/fooocus
    conda env create -f environment.yaml
    conda activate fooocus
    pip install -r requirements_versions.txt
    pip install torch torchvision --force-reinstall --index-url https://download.pytorch.org/whl/cu117
    conda install glib -y
    rm -rf ~/.cache/pip

    # Install Node.js and npm using Conda
    conda install -c conda-forge nodejs -y

    # Install localtunnel globally
    npm install -g localtunnel
else
    conda activate fooocus
fi

# Setup the path for model checkpoints
current_folder=$(pwd)
model_folder=${current_folder}/models/checkpoints-real-folder
if [ ! -e config.txt ]; then
  json_data="{ \"path_checkpoints\": \"$model_folder\" }"
  echo "$json_data" > config.txt
  echo "JSON file created: config.txt"
else
  echo "Updating config.txt to use checkpoints-real-folder"
  jq --arg new_value "$model_folder" '.path_checkpoints = $new_value' config.txt > config_tmp.txt && mv config_tmp.txt config.txt
fi

# Move the checkpoints folder to the new location and create a symbolic link
if [ ! -L models/checkpoints ]; then
    mv models/checkpoints models/checkpoints-real-folder
    ln -s models/checkpoints-real-folder models/checkpoints
fi

# Ensure the fooocus environment is activated before running the server and script
conda activate fooocus

# Start a local tunnel and background Python script
lt --port 7865 & wget -q -O - https://loca.lt/mytunnelpassword

# Run the Python script in the background within the fooocus environment
python Fooocus/entry_with_update.py --always-high-vram &