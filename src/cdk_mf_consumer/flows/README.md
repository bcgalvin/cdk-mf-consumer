# Metaflow Flows 

## Overview

```mermaid
flowchart TD
    A[Start] --> B[Get Updates]
    B --> C[Process Items in Batches]
    C --> D[Process Users in Batches]
    D --> E[Save Data]
    E --> F[End]

    subgraph "Process Items"
    C --> C1[Fetch Item Details]
    C1 --> C2[Update Statistics]
    C2 --> C3[Rate Limit]
    end

    subgraph "Process Users"
    D --> D1[Fetch User Profiles]
    D1 --> D2[Update Statistics]
    D2 --> D3[Rate Limit]
    end

    subgraph "Save Data"
    E --> E1[Convert to Dataframes]
    E1 --> E2[Create Partitions]
    E2 --> E3[Write Parquet Files]
    end
```

## Output Structure

```
data/raw/
  ├── stories/
  │   └── year=2024/month=01/day=15/
  │       └── 20240115_123456.parquet
  ├── comments/
  │   └── year=2024/month=01/day=15/
  │       └── 20240115_123456.parquet
  └── users/
      └── year=2024/month=01/day=15/
          └── 20240115_123456.parquet
```
