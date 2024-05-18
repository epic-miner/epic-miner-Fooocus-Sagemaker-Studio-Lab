#!/bin/bash

# Set the installation directory based on the install_in_temp_dir variable
install_in_temp_dir=true
install_folder="~/.conda/envs/fooocus"

# Check if the Fooocus directory exists, if not, clone the repository
if [ ! -d "Fooocus" ]; then
  git clone https://github.com/lllyasviel/Fooocus.git
fi

# Navigate to the Fooocus directory and pull the latest changes
cd Fooocus || exit
git pull

# Display the installation directory based on the install_in_temp_dir variable
echo "Installation directory: $install_folder"

# If install_in_temp_dir is true, create a temporary installation directory and set up a symbolic link
if [ "$install_in_temp_dir" = true ]; then
  temporary_install_folder="/tmp/fooocus_env"
  echo "Temporary installation folder: $temporary_install_folder"
  if [ ! -L ~/.conda/envs/fooocus ]; then
    echo "Removing existing symbolic link ~/.conda/envs/fooocus"
    rm -rf ~/.conda/envs/fooocus
    rmdir ~/.conda/envs/fooocus
    ln -s "$temporary_install_folder" ~/.conda/envs/fooocus
  fi
fi

# Activate the Conda environment
eval "$(conda shell.bash hook)"

# Verify if the installation folders exist
if [ ! -d ~/.conda/envs/fooocus ]; then 
  echo ".conda/envs/fooocus is not a directory or does not exist"
fi

# Perform installation if the installation directories are missing
if [ "$install_in_temp_dir" = true ] && [ ! -d /tmp/fooocus_env ] || [ "$install_in_temp_dir" = false ] && [ ! -d ~/.conda/envs/fooocus ]; then
  echo "Installing dependencies"
  
  # Create Conda environment and install dependencies
  conda env create -f environment.yaml
  conda activate fooocus
  pwd
  ls
  pip install -r requirements_versions.txt
  pip install torch torchvision --force-reinstall --index-url https://download.pytorch.org/whl/cu117
  pip install opencv-python-headless
  
  # Install ngrok
  pip install pyngrok
  
  # Install glib
  rm -f /opt/conda/.condarc
  conda install -y conda-forge::glib
  rm -rf ~/.cache/pip
fi

# Move checkpoint files into a folder with a different name
current_folder=$(pwd)
model_folder="${current_folder}/models/checkpoints-real-folder"
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

# Activate fooocus environment and start the application
conda activate fooocus
cd ..

# Check for command-line arguments
if [ $# -eq 0 ]; then
  python start-ngrok-zrok.py 
elif [ "$1" = "reset" ]; then
  python start-ngrok-zrok.py --reset 
fi
