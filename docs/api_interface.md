# CacheFlow API Interfaces

## install_rule
- Input: rule JSON
- Output: boolean (success/failure)

## query_cache
- Input: match fields (tuple)
- Output: list of matched rules

## sync_hw
- Input: batch updates list
- Output: boolean

## metrics
- Input: time window (ms)
- Output: hit rate and average latency
