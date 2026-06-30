#!/bin/bash
# This script downloads a sample CAIDA trace (placeholder URL)
mkdir -p data/raw
wget -O data/raw/caida_sample.pcap http://example.com/caida-trace.pcap
echo "Download complete."
