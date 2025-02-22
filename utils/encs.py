# see https://en.wikipedia.org/wiki/UTF-8

def create_encoding_4b(u, v, w, x):
    """
    Creates an encoding function that maps characters to 4-byte UTF-8 sequences
    with the format: 11110uvv 10vvwwww 10xxxxyy 10yyzzzz
    where u, v, w, x are fixed values and y, z are derived from the input character.
    
    Parameters:
    u (int): Value for u bits (0-1)
    v (int): Value for v bits (0-15)
    w (int): Value for w bits (0-15)
    x (int): Value for x bits (0-15)
    
    Returns:
    function: A function that converts input strings to the specified encoding
    """
    # Validate input parameters
    if not (0 <= u <= 1 and 0 <= v <= 15 and 0 <= w <= 15 and 0 <= x <= 15):
        raise ValueError("Parameters must be: 0 <= u <= 1, 0 <= v,w,x <= 15")
    
    def encoder(input_string, prefix=''):
        result = []
        for ch in input_string:
            if ord(ch) < 128:  # ASCII characters only
                # For ASCII, we'll use a simple mapping where:
                # - y takes the top 4 bits of the ASCII code (bits 4-7)
                # - z takes the bottom 4 bits of the ASCII code (bits 0-3)
                code_point = ord(ch)
                y = (code_point >> 4) & 0xF  # Top 4 bits
                z = code_point & 0xF         # Bottom 4 bits
                
                # Construct the 4-byte UTF-8 sequence
                byte1 = 0xF0 | (u << 2) | (v >> 2)
                byte2 = 0x80 | ((v & 0x3) << 4) | w
                byte3 = 0x80 | (x << 2) | (y >> 2)
                byte4 = 0x80 | ((y & 0x3) << 4) | z
                
                # Convert bytes to a UTF-8 character and append to result
                encoded_char = bytes([byte1, byte2, byte3, byte4]).decode('utf-8', errors='replace')
                result.append(encoded_char)
            else:
                # Pass through non-BMP characters unchanged
                result.append(ch)
        
        return prefix + ''.join(result)
    
    return encoder

def create_encoding_3b(w, x):
    """
    Creates an encoding function that maps characters to 3-byte UTF-8 sequences
    with the format: 1110wwww 10xxxxyy 10yyzzzz
    where w, x are fixed values and y, z are derived from the input character.
    
    Parameters:
    w (int): Value for w bits (0-15)
    x (int): Value for x bits (0-15)
    
    Returns:
    function: A function that converts input strings to the specified encoding
    """
    # Validate input parameters15
    if not (0 <= w <= 15 and 0 <= x <= 15):
        raise ValueError("Parameters must be: 0 <= w,x <= 15")
    
    def encoder(input_string, prefix=''):
        result = []
        for ch in input_string:
            if ord(ch) < 128:  # ASCII characters only
                # For ASCII, we'll use a simple mapping where:
                # - y takes the top 4 bits of the ASCII code (bits 4-7)
                # - z takes the bottom 4 bits of the ASCII code (bits 0-3)
                code_point = ord(ch)
                y = (code_point >> 4) & 0xF  # Top 4 bits
                z = code_point & 0xF         # Bottom 4 bits
                
                # Construct the 4-byte UTF-8 sequence
                byte1 = 0xE0 | w
                byte2 = 0x80 | (x << 2) | (y >> 2)
                byte3 = 0x80 | ((y & 0x3) << 4) | z
                
                # Convert bytes to a UTF-8 character and append to result
                encoded_char = bytes([byte1, byte2, byte3]).decode('utf-8', errors='replace')
                result.append(encoded_char)
            else:
                # Pass through non-BMP characters unchanged
                result.append(ch)
        
        return prefix + ''.join(result)
    
    return encoder

def create_encoding_2b(x):
    """
    Creates an encoding function that maps characters to 2-byte UTF-8 sequences
    with the format: 110xxxyy 10yyzzzz
    where x are fixed values and y, z are derived from the input character.
    
    Parameters:
    x (int): Value for x bits (0-7)
    
    Returns:
    function: A function that converts input strings to the specified encoding
    """
    # Validate input parameters
    if not (0 <= x <= 7):
        raise ValueError("Parameters must be: 0 <= x <= 7")
    
    def encoder(input_string, prefix=''):
        result = []
        for ch in input_string:
            if ord(ch) < 128:  # ASCII characters only
                # For ASCII, we'll use a simple mapping where:
                # - y takes the top 4 bits of the ASCII code (bits 4-7)
                # - z takes the bottom 4 bits of the ASCII code (bits 0-3)
                code_point = ord(ch)
                y = (code_point >> 4) & 0xF  # Top 4 bits
                z = code_point & 0xF         # Bottom 4 bits
                
                # Construct the 4-byte UTF-8 sequence
                byte1 = 0xC0 | (x << 2) | (y >> 2)
                byte2 = 0x80 | ((y & 0x3) << 4) | z
                
                # Convert bytes to a UTF-8 character and append to result
                encoded_char = bytes([byte1, byte2]).decode('utf-8', errors='replace')
                result.append(encoded_char)
            else:
                # Pass through non-BMP characters unchanged
                result.append(ch)
        
        return prefix + ''.join(result)
    
    return encoder
