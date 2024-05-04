#!/bin/bash

if [ ! -d "Fooocus" ]; then
  git clone https://github.com/lllyasviel/Fooocus.git
fi

cd Fooocus
git pull

if [ ! -L ~/.conda/envs/fooocus ]; then
    ln -s /tmp/fooocus ~/.conda/envs/
fi

eval "$(conda shell.bash hook)"

if [ ! -d /tmp/fooocus ]; then
    mkdir /tmp/fooocus
    conda env create -f environment.yaml
    conda activate fooocus
    pip install -r requirements_versions.txt
    pip install torch torchvision --force-reinstall --index-url https://download.pytorch.org/whl/cu117
    conda install glib -y
    rm -rf ~/.cache/pip
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

# If the checkpoints folder exists, move it to the new checkpoints-real-folder
if [ ! -L models/checkpoints ]; then
    mv models/checkpoints models/checkpoints-real-folder
    ln -s models/checkpoints-real-folder models/checkpoints
fi

# Activate the fooocus environment
conda activate fooocus
cd ..

lt --port 8888 & wget -q -O - https://loca.lt/mytunnelpassword

# Run Python script in the background
python Fooocus/entry_with_update.py --always-high-vram &
