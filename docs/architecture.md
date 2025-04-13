# System Architecture - Ethereum Wallet Recovery Tool

## 1. System Overview

### 1.1 Architecture Diagram
```
+------------------------+     +------------------------+     +------------------------+
|      User Interface    |     |    Master Process     |     |    Progress Manager   |
|------------------------|     |------------------------|     |------------------------|
| - CLI Arguments       |     | - Permutation Control  |     | - Progress Tracking   |
| - Progress Display    |     | - Worker Management    |     | - State Persistence   |
| - Error Reporting     |     | - Resource Management  |     | - Statistics Calc     |
+------------------------+     +------------------------+     +------------------------+
           |                            |                             |
           |                            |                             |
           v                            v                             v
+------------------------+     +------------------------+     +------------------------+
|    Mnemonic Handler    |     |    Worker Processes   |     |    Wallet Deriver    |
|------------------------|     |------------------------|     |------------------------|
| - Word Validation      |     | - Chunk Processing    |     | - Address Generation  |
| - Checksum Validation  |     | - Memory Management   |     | - Path Derivation     |
| - Mnemonic Assembly    |     | - Result Reporting    |     | - Key Management      |
+------------------------+     +------------------------+     +------------------------+
```

## 2. Component Interactions

### 2.1 Data Flow
```
[User Input] -> [Input Validation] -> [Permutation Generation] -> [Worker Distribution]
                                                                        |
                                                                        v
[Result Output] <- [Progress Updates] <- [Worker Processing] <- [Chunk Processing]
```

### 2.2 Process Flow
1. **Initialization Phase**
   ```
   User Input -> Validation -> Configuration Loading -> Worker Pool Creation
   ```

2. **Processing Phase**
   ```
   Permutation Generation -> Chunk Distribution -> Parallel Processing -> Result Collection
   ```

3. **Progress Management**
   ```
   Worker Updates -> Progress Calculation -> State Persistence -> UI Updates
   ```

## 3. Component Details

### 3.1 User Interface Layer
- **Command Line Interface**
  - Argument parsing and validation
  - Progress display (tqdm-based)
  - Error reporting and logging
  - Graceful shutdown handling

- **Configuration Management**
  - JSON-based configuration
  - Environment variable support
  - Runtime parameter validation

### 3.2 Processing Layer
- **Master Process**
  - Worker pool management
  - Resource allocation
  - Task distribution
  - Result aggregation

- **Worker Processes**
  - Chunk processing
  - Memory management
  - Error handling
  - Result reporting

### 3.3 Cryptographic Layer
- **Mnemonic Operations**
  - BIP-39 word validation
  - Checksum verification
  - Mnemonic construction

- **Wallet Operations**
  - Key derivation (BIP-44)
  - Address generation
  - Path management

## 4. State Management

### 4.1 Progress State
```
                    +-------------------+
                    |  Progress State   |
                    +-------------------+
                            |
                 +--------------------+
                 |                    |
        +----------------+  +------------------+
        | Volatile State |  | Persistent State |
        +----------------+  +------------------+
        - Current chunk    - Processed chunks
        - Active workers   - Total progress
        - Memory usage     - Timestamps
```

### 4.2 Worker State
```
                    +---------------+
                    | Worker State  |
                    +---------------+
                           |
                 +-------------------+
                 |                   |
        +--------------+  +------------------+
        | Processing   |  |     Results      |
        +--------------+  +------------------+
        - Current chunk  - Found matches
        - Memory stats   - Error states
        - Progress      - Completion status
```

## 5. Security Architecture

### 5.1 Data Protection
```
+------------------------+     +------------------------+
|    Memory Protection   |     |    Storage Protection  |
|------------------------|     |------------------------|
| - Secure allocation    |     | - Encrypted storage   |
| - Wiping on completion |     | - Atomic writes       |
| - Overflow prevention  |     | - Checksum validation |
+------------------------+     +------------------------+
```

### 5.2 Process Isolation
```
+------------------------+     +------------------------+
|    Worker Isolation    |     |   Resource Controls   |
|------------------------|     |------------------------|
| - Process separation   |     | - Memory limits       |
| - Resource containment |     | - CPU quotas          |
| - Error containment    |     | - I/O restrictions    |
+------------------------+     +------------------------+
```

## 6. Performance Architecture

### 6.1 Resource Management
```
                    +--------------------+
                    | Resource Manager   |
                    +--------------------+
                            |
                 +---------------------+
                 |                     |
        +----------------+   +------------------+
        | CPU Management |   | Memory Management|
        +----------------+   +------------------+
        - Core allocation   - Chunk sizing
        - Load balancing    - Garbage collection
        - Process scaling   - Cache management
```

### 6.2 Optimization Strategies
```
+------------------------+     +------------------------+
|    Computational      |     |      I/O              |
|------------------------|     |------------------------|
| - Early termination    |     | - Buffered writes     |
| - Cached validation    |     | - Atomic operations   |
| - Parallel processing  |     | - Compressed storage  |
+------------------------+     +------------------------+
```

## 7. Monitoring and Logging

### 7.1 Metrics Collection
- Processing speed (permutations/second)
- Memory usage per worker
- CPU utilization
- Progress percentage
- Error rates

### 7.2 Logging Architecture
```
+------------------------+     +------------------------+
|    Application Logs    |     |    System Metrics     |
|------------------------|     |------------------------|
| - Progress updates     |     | - Resource usage      |
| - Error tracking       |     | - Performance stats   |
| - Debug information    |     | - Health checks       |
+------------------------+     +------------------------+
```

## 8. Deployment Architecture

### 8.1 Local Deployment
```
+------------------------+     +------------------------+
|    Python Runtime      |     |    Dependencies       |
|------------------------|     |------------------------|
| - Version: 3.8+       |     | - bip_utils           |
| - Virtual Environment  |     | - web3               |
| - Platform specific   |     | - cryptography       |
+------------------------+     +------------------------+
```

### 8.2 Development Environment
```
+------------------------+     +------------------------+
|    Testing Framework   |     |    Development Tools  |
|------------------------|     |------------------------|
| - pytest              |     | - flake8             |
| - Coverage reporting  |     | - black              |
| - Mocking support     |     | - mypy               |
+------------------------+     +------------------------+
``` 