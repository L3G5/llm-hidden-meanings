from itertools import product
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

def create_encoding_2b_v2(x):
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
    if not (0 <= x <= 15):
        raise ValueError("Parameters must be: 0 <= x <= 7")
    
    def encoder(input_string, prefix=''):
        result = []
        for ch in input_string:
            if ord(ch) < 128:  # ASCII characters only
                # For ASCII, we'll use a simple mapping where:
                # - y takes the top 4 bits of the ASCII code (bits 4-7)
                # - z takes the bottom 4 bits of the ASCII code (bits 0-3)
                code_point = ord(ch)
                y = (code_point >> 5) & 0xF  # Top 4 bits
                z = code_point & 0xF         # Bottom 4 bits
                
                # Construct the 4-byte UTF-8 sequence
                byte1 = 0xC0 | (y << 2) | (z >> 2)
                byte2 = 0x80 | ((z & 0x3) << 4) | x
                
                # Convert bytes to a UTF-8 character and append to result
                encoded_char = bytes([byte1, byte2]).decode('utf-8', errors='replace')
                result.append(encoded_char)
            else:
                # Pass through non-BMP characters unchanged
                result.append(ch)
        
        return prefix + ''.join(result)
    
    return encoder

def create_encoding_3b_v2(w, x):
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
                byte1 = 0xE0 | y
                byte2 = 0x80 | (z << 2) | (w >> 2)
                byte3 = 0x80 | ((w & 0x3) << 4) | x
                
                # Convert bytes to a UTF-8 character and append to result
                encoded_char = bytes([byte1, byte2, byte3]).decode('utf-8', errors='replace')
                result.append(encoded_char)
            else:
                # Pass through non-BMP characters unchanged
                result.append(ch)
        
        return prefix + ''.join(result)
    
    return encoder

def create_encoding_4b_v2(u, v, w, x):
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
                byte1 = 0xF0 | (u << 2) | (y >> 2)
                byte2 = 0x80 | ((y & 0x3) << 4) | z
                byte3 = 0x80 | (v << 2) | (w >> 2)
                byte4 = 0x80 | ((w & 0x3) << 4) | x
                
                # Convert bytes to a UTF-8 character and append to result
                encoded_char = bytes([byte1, byte2, byte3, byte4]).decode('utf-8', errors='replace')
                result.append(encoded_char)
            else:
                # Pass through non-BMP characters unchanged
                result.append(ch)
        
        return prefix + ''.join(result)
    
    return encoder


# Configuration dictionary
ENCODING_CONFIG = {
    '2b': {
        'params_range': product(range(7)),
        'encoder': create_encoding_2b,
        'param_names': ['x']
    },
    '3b': {
        'params_range': product(range(16), repeat=2),
        'encoder': create_encoding_3b,
        'param_names': ['v', 'w']
    },
    '4b': {
        'params_range': product(range(2), range(16), range(16), range(16)),
        'encoder': create_encoding_4b,
        'param_names': ['u', 'v', 'w', 'x']
    },
    '2b_v2': {
        'params_range': product(range(16)),
        'encoder': create_encoding_2b_v2,
        'param_names': ['x']
    },
    '3b_v2': {
        'params_range': product(range(16), repeat=2),
        'encoder': create_encoding_3b_v2,
        'param_names': ['v', 'w']
    },
    '4b_v2': {
        'params_range': product(range(2), range(16), range(16), range(16)),
        'encoder': create_encoding_4b_v2,
        'param_names': ['u', 'v', 'w', 'x']
    }

}

def decoder(encoded_string):
    result = []
    byte_array = encoded_string.encode('utf-8')  # Convert string to raw bytes
    i = 0
    while i < len(byte_array):
        byte1 = byte_array[i]
        
        # Determine the number of bytes in the UTF-8 sequence
        if (byte1 & 0xF0) == 0xF0 and (byte1 & 0x08) == 0x00:  # 4-byte sequence
            # Ensure there are enough bytes left
            if i + 3 >= len(byte_array):
                raise ValueError("Invalid 4-byte UTF-8 sequence")
            
            byte2 = byte_array[i+1]
            byte3 = byte_array[i+2]
            byte4 = byte_array[i+3]
            
            # Validate continuation bytes
            if not ((byte2 & 0xC0) == 0x80 and (byte3 & 0xC0) == 0x80 and (byte4 & 0xC0) == 0x80):
                raise ValueError("Invalid continuation bytes in 4-byte UTF-8 sequence")
            
            # Extract y and z from the bytes
            y = ((byte3 & 0x3) << 2) | ((byte4 & 0x30) >> 4)
            z = byte4 & 0xF
            
            # Reconstruct the original ASCII character
            original_char = chr((y << 4) | z)
            result.append(original_char)
            
            i += 4
        elif (byte1 & 0xE0) == 0xE0:  # 3-byte sequence
            # Ensure there are enough bytes left
            if i + 2 >= len(byte_array):
                raise ValueError("Invalid 3-byte UTF-8 sequence")
            
            byte2 = byte_array[i+1]
            byte3 = byte_array[i+2]
            
            # Validate continuation bytes
            if not ((byte2 & 0xC0) == 0x80 and (byte3 & 0xC0) == 0x80):
                raise ValueError("Invalid continuation bytes in 3-byte UTF-8 sequence")
            
            # Extract y and z from the bytes
            y = ((byte2 & 0x3) << 2) | ((byte3 & 0x30) >> 4)
            z = byte3 & 0xF
            
            # Reconstruct the original ASCII character
            original_char = chr((y << 4) | z)
            result.append(original_char)
            
            i += 3
        elif (byte1 & 0xC0) == 0xC0:  # 2-byte sequence
            # Ensure there are enough bytes left
            if i + 1 >= len(byte_array):
                raise ValueError("Invalid 2-byte UTF-8 sequence")
            
            byte2 = byte_array[i+1]
            
            # Validate continuation byte
            if not (byte2 & 0xC0) == 0x80:
                raise ValueError("Invalid continuation byte in 2-byte UTF-8 sequence")
            
            # Extract y and z from the bytes
            y = ((byte1 & 0x3) << 2) | ((byte2 & 0x30) >> 4)
            z = byte2 & 0xF
            
            # Reconstruct the original ASCII character
            original_char = chr((y << 4) | z)
            result.append(original_char)
            
            i += 2
        else:  # ASCII character (1-byte sequence)
            result.append(chr(byte1))
            i += 1
    
    return ''.join(result)


def decoder_v2(encoded_string):
    #only for b3
    result = []
    byte_array = encoded_string.encode('utf-8')  # Convert string to raw bytes
    i = 0
    while i < len(byte_array):
        byte1 = byte_array[i]
        
        # Determine the number of bytes in the UTF-8 sequence
        if (byte1 & 0xF0) == 0xF0 and (byte1 & 0x08) == 0x00:  # 4-byte sequence
            # Ensure there are enough bytes left
            if i + 3 >= len(byte_array):
                raise ValueError("Invalid 4-byte UTF-8 sequence")
            
            byte2 = byte_array[i+1]
            byte3 = byte_array[i+2]
            byte4 = byte_array[i+3]
            
            # Validate continuation bytes
            if not ((byte2 & 0xC0) == 0x80 and (byte3 & 0xC0) == 0x80 and (byte4 & 0xC0) == 0x80):
                raise ValueError("Invalid continuation bytes in 4-byte UTF-8 sequence")
            
            # Extract y and z from the bytes
            y = ((byte3 & 0x3) << 2) | ((byte4 & 0x30) >> 4)
            z = byte4 & 0xF
            
            # Reconstruct the original ASCII character
            original_char = chr((y << 4) | z)
            result.append(original_char)
            
            i += 4
        elif (byte1 & 0xE0) == 0xE0:  # 3-byte sequence
            # Ensure there are enough bytes left
            if i + 2 >= len(byte_array):
                raise ValueError("Invalid 3-byte UTF-8 sequence")
            
            byte2 = byte_array[i+1]
            byte3 = byte_array[i+2]

            # Validate continuation bytes
            if not ((byte2 & 0xC0) == 0x80 and (byte3 & 0xC0) == 0x80):
                raise ValueError("Invalid continuation bytes in 3-byte UTF-8 sequence")
            
            # Extract y and z from the bytes
            y = ((byte1 & 0xF))
            z = (byte2 >> 2 )& 0xF
            
            # Reconstruct the original ASCII character
            original_char = chr((y << 4) | z)
            result.append(original_char)
            
            i += 3
        elif (byte1 & 0xC0) == 0xC0:  # 2-byte sequence
            # Ensure there are enough bytes left
            if i + 1 >= len(byte_array):
                raise ValueError("Invalid 2-byte UTF-8 sequence")
            
            byte2 = byte_array[i+1]
            
            # Validate continuation byte
            if not (byte2 & 0xC0) == 0x80:
                raise ValueError("Invalid continuation byte in 2-byte UTF-8 sequence")
            
            # Extract y and z from the bytes
            y = ((byte1 & 0x3) << 2) | ((byte2 & 0x30) >> 4)
            z = byte2 & 0xF
            
            # Reconstruct the original ASCII character
            original_char = chr((y << 4) | z)
            result.append(original_char)
            
            i += 2
        else:  # ASCII character (1-byte sequence)
            result.append(chr(byte1))
            i += 1
    
    return ''.join(result)


def create_encoding_2b_to_3b(w, x):
    """
    Creates an encoding function that maps 2-byte UTF-8 sequences to 3-byte UTF-8 sequences
    with the format: 1110wwww 10xxxxyy 10yyzzzz
    where w and x are fixed values, and y, z are derived from the input 2-byte UTF-8 sequence.
    
    Parameters:
    w (int): Value for w bits (0-15)
    x (int): Value for x bits (0-1)
    
    Returns:
    function: A function that converts input 2-byte UTF-8 sequences to the specified 3-byte encoding
    """
    # Validate input parameters
    if not (0 <= w <= 15 and 0 <= x <= 1):
        raise ValueError("Parameters must be: 0 <= w <= 15, 0 <= x <= 1")
    
    def encoder(input_string, prefix=''):
        result = []
        for ch in input_string:
            code_point = ord(ch)
            if 0x80 <= code_point <= 0x7FF:  # Check if the character is a 2-byte UTF-8 sequence
                # Extract x, y, and z from the 2-byte UTF-8 sequence
                # The 2-byte UTF-8 format is: 110xxxyy 10yyzzzz
                x0 = (code_point >> 8) & 0xF
                y = (code_point >> 4) & 0xF  # Top 4 bits
                z = code_point & 0xF         # Bottom 4 bits
                # Construct the 4-byte UTF-8 sequence
                byte1 = 0xE0 | w
                byte2 = 0x80 | ((x0 + (x << 3)) << 2) | (y >> 2)
                byte3 = 0x80 | ((y & 0x3) << 4) | z
                                                
                # Convert bytes to a UTF-8 character and append to result
                encoded_char = bytes([byte1, byte2, byte3]).decode('utf-8', errors='replace')
                result.append(encoded_char)
            else:
                # Pass through non-2-byte UTF-8 characters unchanged
                result.append(ch)
        
        return prefix + ''.join(result)
    
    return encoder

def create_encoding_2b_to_4b(u, v, w, x):
    """
    Creates an encoding function that maps 2-byte UTF-8 sequences to 4-byte UTF-8 sequences
    with the format: 11110uvv 10vvwwww 10xxxxyy 10yyzzzz
    where u, v, w, and x are fixed values, and y, z are derived from the input 2-byte UTF-8 sequence.
    
    Parameters:
    u (int): Value for u bits (0-1)
    v (int): Value for v bits (0-7)
    w (int): Value for w bits (0-15)
    x (int): Value for x bits (0-1)
    
    Returns:
    function: A function that converts input 2-byte UTF-8 sequences to the specified 4-byte encoding
    """
    # Validate input parameters
    if not (0 <= u <= 1 and 0 <= v <= 15 and 0 <= w <= 15 and 0 <= x <= 1):
        raise ValueError("Parameters must be: 0 <= u <= 1, 0 <= v <= 15, 0 <= w <= 15, 0 <= x <= 1")
    
    def encoder(input_string, prefix=''):
        result = []
        for ch in input_string:
            code_point = ord(ch)
            if 0x80 <= code_point <= 0x7FF:  # Check if the character is a 2-byte UTF-8 sequence
                # Extract y and z from the 2-byte UTF-8 sequence
                # The 2-byte UTF-8 format is: 110xxxyy 10yyzzzz
                x0 = (code_point >> 8) & 0xF
                y = (code_point >> 4) & 0xF  # Top 4 bits
                z = code_point & 0xF         # Bottom 4 bits
                # Construct the 4-byte UTF-8 sequence
                
                # Construct the 4-byte UTF-8 sequence
                byte1 = 0xF0 | (u << 2) | (v >> 2)               # 11110uvv
                byte2 = 0x80 | ((v & 0x3) << 4) | w     # 10vvwwww
                byte3 = 0x80 | ((x0 + (x << 3)) << 2) | (y >> 2)   # 10xxxxyy
                byte4 = 0x80 | ((y & 0x3) << 4) | z              # 10yyzzzz
                                                
                # Convert bytes to a UTF-8 character and append to result
                encoded_char = bytes([byte1, byte2, byte3, byte4]).decode('utf-8', errors='replace')
                result.append(encoded_char)
            else:
                # Pass through non-2-byte UTF-8 characters unchanged
                result.append(ch)
        
        return prefix + ''.join(result)
    
    return encoder
