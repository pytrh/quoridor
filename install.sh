#!/bin/bash

echo "###########################################"
echo "###########################################"
echo "########                         ::########"
echo "########   installation quoridor   ########"
echo "########::                         ########"
echo "###########################################"
echo "###########################################"
echo ""
echo ""

# Check if the OS is Linux
if [[ "$(uname)" == "Linux" ]]; then
    echo "[v] Linux system detected. Installing dependencies..."
    
    # Installing PyGObject, GTK, and their dependencies 
    sudo apt update 
    sudo apt install -y python3-gi python3-gi-cairo gir1.2-gtk-4.0
    sudo apt install -y libgirepository-2.0-dev gcc libcairo2-dev pkg-config
    sudo apt install -y libgles2-mesa-dev libegl1-mesa-dev
    sudo apt install -y fonts-noto-color-emoji
    echo "[v] Dependencies installation completed."

    if [ -d "quoridor" ]; then
        cd "quoridor" || exit
        echo "[-] Installing Python dependencies from pyproject.toml..."
        pip install -e .
        echo "[v] Installation completed!"
        echo ""
        read -p "Press Enter to exit..."
    else
        echo "[x] Error: The ~/quoridor directory does not exist."
        echo ""
        read -p "Press Enter to exit..."
        exit 1
    fi
else
    echo "[x] Unsupported system. This script is only compatible with Linux"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi
