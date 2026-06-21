# Real-ESRGAN NCNN Vulkan WebGUI

A simple web interface for running Real-ESRGAN NCNN Vulkan through a Flask-based backend.

## Features

* Web-based image upload
* Real-ESRGAN NCNN Vulkan image upscaling
* Vulkan GPU acceleration
* Multiple Real-ESRGAN models
* Simple Flask web interface
* Podman-compatible deployment

## Project Structure

```text
.
├── source
│   ├── realesrgan-ncnn-vulkan-20220424-ubuntu.zip
│   └── realesrgan-ncnn-vulkan-20220424-ubuntu.zip.sha256
├── upscale
│   ├── pyserver
│   │   ├── templates
│   │   │   └── index.html
│   │   └── app.py
│   ├── realesrgan-ncnn-vulkan-20220424-ubuntu
│   │   ├── models
│   │   └── realesrgan-ncnn-vulkan
│   ├── requirements.txt
│   └── run.sh
└── README.md
```

## Download Real-ESRGAN

Download the NCNN Vulkan release:

```text
https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesrgan-ncnn-vulkan-20220424-ubuntu.zip
```

Expected SHA256:

```text
e5aa6eb131234b87c0c51f82b89390f5e3e642b7b70f2b9bbe95b6a285a40c96
```

Verify the download:

```bash
sha256sum source/realesrgan-ncnn-vulkan-20220424-ubuntu.zip
```

## Requirements

### Ubuntu / Debian

```bash
sudo apt update
sudo apt install -y \
    python3 \
    python3-pip \
    libgomp1
```

## Install Python Dependencies

```bash
cd upscale

pip3 install -r requirements.txt
```

## Running Locally

```bash
cd upscale

chmod +x run.sh
./run.sh
```

The web interface will be available at:

```text
http://localhost:5011
```

## Running with Podman

Start a container:

```bash
podman run -dit \
    --name anime-upscale \
    -p 5011:5011 \
    --device /dev/dri/card1:/dev/dri/card1 \
    --device /dev/dri/renderD128:/dev/dri/renderD128 \
    -v $(pwd)/upscale:/upscale:Z \
    ubuntu:22.04 \
    bash -c "
        apt update &&
        apt install -y python3 python3-pip libgomp1 &&
        pip3 install -r /upscale/requirements.txt &&
        cd /upscale &&
        chmod +x run.sh &&
        ./run.sh
    "
```

View logs:

```bash
podman logs -f anime-upscale
```

Stop the container:

```bash
podman stop anime-upscale
```

Remove the container:

```bash
podman rm -f anime-upscale
```

## GPU Configuration

Example GPU device mapping:

```bash
--device /dev/dri/card1:/dev/dri/card1
--device /dev/dri/renderD128:/dev/dri/renderD128
```

Adjust the device paths according to your system configuration.

## Accessing the Web Interface

Open your browser and navigate to:

```text
http://localhost:5011
```

Upload an image, select a model, and start the upscaling process.

## Credits

* Real-ESRGAN by Xintao Wang and contributors
* NCNN Vulkan backend
* Flask web interface


## GPU Verification

Before running Real-ESRGAN, verify that Vulkan can detect your GPU.

### Host

Install Vulkan tools:

```bash
sudo apt install -y vulkan-tools
```

Check the detected GPU:

```bash
vulkaninfo | grep deviceName
```

Example output:

```text
deviceName        = AMD Radeon RX 6600
```

### Podman Container

Verify that the GPU is accessible from the running container:

```bash
podman exec -it anime-upscale bash
```

Inside the container:

```bash
apt update
apt install -y vulkan-tools

vulkaninfo | grep deviceName
```

Example output:

```text
deviceName        = AMD Radeon RX 6600
```

If the GPU name is displayed, Vulkan has successfully detected the GPU and Real-ESRGAN can use hardware acceleration.
