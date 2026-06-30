# CacheFlow: Dependency-Aware Rule Caching for SDN

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)

This repository contains the complete implementation of **CacheFlow**, a novel dependency-aware rule caching system proposed in our paper:

> **"CacheFlow：一种针对大量流表而设计软硬件联合查找方法研究及其实现"**  
> *Zhao Chenwei, Wan Ying* — Southeast University, 2026.

## Key Features
- **Dependency Graph Construction**: Extracts priority and matching coverage relationships among ACL/FW rules.
- **Dependency-Aware Admission & Replacement**: Caches entire dependency closures to ensure semantic consistency.
- **Consistency-First Scheduling**: Two-phase commit with shadow rules to prevent packet reordering.
- **Incremental Updates**: Only affected subgraphs are recomputed, reducing TCAM rewrite overhead by about 40%.

## Quick Start
```bash
git clone https://github.com/your-username/CacheFlow.git
cd CacheFlow
./scripts/setup_env.sh
pip install -r requirements.txt
python experiments/run_experiment.py --config experiments/configs/cacheflow_full.yaml
