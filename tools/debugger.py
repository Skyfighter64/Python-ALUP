from pyalup.Frame import Frame
from typing import List
import re
"""
Script for debugging ALUP connections.
"""

def main():
    text = input("Enter raw frame data: ")
    AnalyzeRawData(text)

def ExtractRawFrame(text: str) -> List[int]:
    """
    Extract raw bytes from a string of space-separated 10s complement numbers
    @param text: The text containing the numbers. Non-number symbols are ignored
    @returns: a list of numbers

    Example: 
    """
    return bytes([int(i) for i in re.findall("\d+", text)])

def FrameFromText(text):
    """
    Parse an ALUP frame from a string of text containing space-separated raw frame data.
    Other text than numbers will be ignored
    """


def AnalyzeRawData(text:str):
    """
    Extract a frame from raw text data and parse its contents
    Example input: 
    raw data: "Received: 1 Received: 0 Received: 0 0 0 3 Received: 0 0 0 0 Received: 0 0 0 0 Received: 0 255 0"


    """
    frame_bytes = bytes(ExtractRawFrame(text))
    print("\nExtracted Frame Bytes:")
    print(frame_bytes)
    print("\nInteger Representation:")
    print([int(i) for i in frame_bytes])
    frame = Frame()
    frame.FromBytes(frame_bytes)
    print("\nExtracted Frame:")
    print(frame)



def TestFrameParsing():
    frame = Frame()
    frame.colors = [0xffffff, 0x00ff00, 0x000000, 0x0000ff]
    print("Original:")
    print(frame)
    frame_bytes = frame.ToBytes(time_delta_ms=0)
    print("bytes:")
    print(frame_bytes)
    print("Reconstructed:")
    new_frame = Frame()
    new_frame.FromBytes(frame_bytes)
    print(new_frame) 

if __name__ == "__main__":
    main()
    #TestFrameParsing()
    #print(NumberStringToInt("Received: 202 Received: 0 Received: 0 0 0 3"))