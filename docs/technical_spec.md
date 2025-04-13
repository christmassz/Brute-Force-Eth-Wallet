# Technical Specification - Ethereum Wallet Recovery Tool

## 1. System Components

### 1.1 Core Libraries and Dependencies
```python
# Primary dependencies
bip_utils>=2.7.0    # BIP-39/44 implementation
web3>=6.0.0         # Ethereum interaction
tqdm>=4.65.0        # Progress bars
cryptography>=41.0.0 # Secure operations
```

### 1.2 Component Architecture

#### MnemonicHandler (src/validator.py)
```python
class MnemonicHandler:
    """Manages BIP-39 mnemonic operations and validation"""
    
    def __init__(self):
        self.wordlist = bip_utils.Bip39WordsNum.WORDS_NUM_24
        self.language = bip_utils.Bip39Languages.ENGLISH
        
    def validate_word_list(self, words: List[str]) -> bool:
        """
        Validates if all words are in the BIP-39 wordlist
        
        Args:
            words (List[str]): List of words to validate
            
        Returns:
            bool: True if all words are valid
        """
        
    def construct_mnemonic(self, 
                          permuted_words: List[str], 
                          fixed_words: List[str]) -> str:
        """
        Combines permuted and fixed words into full mnemonic
        
        Args:
            permuted_words: First 9 words in current permutation
            fixed_words: Known words for positions 10-24
            
        Returns:
            str: Complete 24-word mnemonic phrase
        """
        
    def validate_checksum(self, mnemonic: str) -> bool:
        """
        Validates BIP-39 checksum of complete mnemonic
        
        Args:
            mnemonic (str): Complete 24-word mnemonic
            
        Returns:
            bool: True if checksum is valid
        """
```

#### WalletDeriver (src/wallet.py)
```python
class WalletDeriver:
    """Handles Ethereum wallet derivation from mnemonics"""
    
    DERIVATION_PATHS = [
        "m/44'/60'/0'/0/0",    # Standard Ethereum
        "m/44'/60'/0'",        # Alternative path
    ]
    
    def __init__(self, target_address: str):
        self.target_address = target_address.lower()
        self.w3 = Web3()
        
    def derive_address(self, 
                      mnemonic: str, 
                      path: str = "m/44'/60'/0'/0/0") -> str:
        """
        Derives Ethereum address from mnemonic using specified path
        
        Args:
            mnemonic (str): Valid 24-word mnemonic
            path (str): BIP-44 derivation path
            
        Returns:
            str: Derived Ethereum address
        """
```

#### PermutationManager (src/permutation.py)
```python
class PermutationManager:
    """Handles permutation generation and distribution"""
    
    def __init__(self, chunk_size: int = 1000):
        self.chunk_size = chunk_size
        
    def generate_permutation_chunks(self, 
                                  words: List[str]) -> Iterator[List[List[str]]]:
        """
        Generates permutations in memory-efficient chunks
        
        Args:
            words: List of 9 words to permute
            
        Yields:
            List[List[str]]: Chunk of permutations
        """
        
    @staticmethod
    def get_total_permutations() -> int:
        """Returns total number of possible permutations (9!)"""
        return 362880
```

#### ProgressManager (src/worker.py)
```python
class ProgressManager:
    """Handles progress tracking, saving, and recovery"""
    
    def __init__(self, save_file: str = "recovery_progress.json"):
        self.save_file = save_file
        self.processed_count = 0
        self.start_time = time.time()
        self.lock = threading.Lock()
        
    def save_progress(self, 
                     current_chunk: int, 
                     processed_permutations: int):
        """
        Saves progress atomically
        
        Args:
            current_chunk: Index of current chunk
            processed_permutations: Total processed permutations
        """
        
    def load_progress(self) -> Tuple[int, int]:
        """
        Loads previous progress
        
        Returns:
            Tuple[int, int]: (last_chunk, processed_permutations)
        """
        
    def calculate_statistics(self) -> Dict[str, Any]:
        """
        Returns progress statistics
        
        Returns:
            Dict containing:
            - processed_count: int
            - completion_percentage: float
            - elapsed_time: float
            - estimated_remaining: float
            - permutations_per_second: float
        """
```

## 2. Data Structures

### 2.1 Progress State Schema
```json
{
    "timestamp": "2024-03-21T10:00:00Z",
    "processed_chunks": 100,
    "processed_permutations": 50000,
    "total_permutations": 362880,
    "elapsed_time": 3600,
    "estimated_remaining_time": 7200,
    "current_chunk_start": ["word1", "word2", "..."],
    "checksum": "sha256-hash-of-state"
}
```

### 2.2 Configuration Schema
```json
{
    "chunk_size": 1000,
    "num_workers": 8,
    "save_interval": 300,
    "derivation_paths": ["m/44'/60'/0'/0/0"],
    "logging_level": "INFO",
    "progress_file": "recovery_progress.json",
    "log_file": "recovery.log"
}
```

## 3. Process Flow

### 3.1 Initialization
1. Load and validate configuration
2. Validate input words against BIP-39 wordlist
3. Load previous progress (if exists)
4. Initialize worker processes
5. Set up logging and progress tracking

### 3.2 Main Processing Loop
```python
def main_loop(permutable_words: List[str], 
              fixed_words: List[str], 
              target_address: str):
    """Main processing loop"""
    
    # Initialize components
    permutation_manager = PermutationManager()
    progress_manager = ProgressManager()
    
    # Load previous progress
    start_chunk, processed = progress_manager.load_progress()
    
    # Create worker pool
    with Pool(num_workers) as pool:
        try:
            # Generate and process chunks
            for chunk in permutation_manager.generate_permutation_chunks(
                permutable_words, start_from=start_chunk):
                
                # Process chunk asynchronously
                future = pool.apply_async(
                    process_chunk, 
                    (chunk, fixed_words, target_address)
                )
                
                # Handle results
                if future.get():
                    return future.get()
                
                # Update progress
                progress_manager.update(len(chunk))
                
        except KeyboardInterrupt:
            progress_manager.save_progress()
            raise
```

### 3.3 Worker Process
```python
def process_chunk(chunk: List[List[str]], 
                 fixed_words: List[str],
                 target_address: str) -> Optional[str]:
    """Process a chunk of permutations"""
    
    mnemonic_handler = MnemonicHandler()
    wallet_deriver = WalletDeriver(target_address)
    
    for permutation in chunk:
        # Construct and validate mnemonic
        mnemonic = mnemonic_handler.construct_mnemonic(
            permutation, fixed_words
        )
        if not mnemonic_handler.validate_checksum(mnemonic):
            continue
            
        # Try each derivation path
        for path in WalletDeriver.DERIVATION_PATHS:
            address = wallet_deriver.derive_address(mnemonic, path)
            if address.lower() == target_address.lower():
                return mnemonic
                
    return None
```

## 4. Error Handling

### 4.1 Graceful Shutdown
```python
def handle_shutdown(signal, frame):
    """Handle SIGINT/SIGTERM signals"""
    logger.info("Shutdown signal received")
    progress_manager.save_progress()
    sys.exit(0)

signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGTERM, handle_shutdown)
```

### 4.2 Error Recovery
- Automatic retry for failed chunks (up to 3 attempts)
- Corruption detection in progress files using checksums
- Worker process health monitoring
- Memory usage monitoring and garbage collection

## 5. Security Considerations

### 5.1 Memory Management
- Secure memory wiping after processing sensitive data
- Limited chunk size to prevent memory exhaustion
- Regular garbage collection

### 5.2 Progress File Security
- Encrypted storage of progress data
- Atomic writes to prevent corruption
- Checksum validation on load

### 5.3 Input Validation
- Comprehensive validation of all input parameters
- Sanitization of file paths and configuration values
- Validation of Ethereum addresses

## 6. Performance Optimization

### 6.1 Chunk Size Optimization
- Dynamic chunk size based on system memory
- Optimal size determined through benchmarking
- Default: 1000 permutations per chunk

### 6.2 Worker Process Management
- Number of workers based on CPU cores
- Memory monitoring and worker restart
- Load balancing across workers

### 6.3 Early Termination
- Checksum validation before key derivation
- Caching of intermediate results
- Quick rejection of invalid permutations 