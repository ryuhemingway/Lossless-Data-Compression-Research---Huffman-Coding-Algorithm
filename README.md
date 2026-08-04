# Research Paper
* Name: Ryu Hemingway   
* Semester: SU2026
* Topic: Huffman Coding Algorithm
* Language: Python


Note the following is an example outline to help you. Please rework as you need, you do not need to follow the section heads and *YOU SHOULD NOT* make everything a bulleted list. This needs to read as an executive report/research paper. 

## Introduction:

In 1951 a student named David Huffman took an information technology course for his electrical engineering graduate program. The class was offered to either write a report or take an exam and naturally, Huffman decided the report would be easier than the exam. For the report, Huffmans professor Robert Fano asked students to find the most eﬃcient method of representing numbers, letters or other symbols using a binary code[1]. Coming close to giving up, he finally recognised that assigning the longest codes first and proceeding from the branches toward the root yields an optimal solution every time [1]. His report ended up being published and is still used to this day for lossless data compression.

Huffman coding is a type of prefix code (a set of code words where no code word is the start of another code word) that is predominantly used for lossless data compression. Lossless data compression is the process of compressing a file and then reversing the compression process without losing any information. The method used to achieve lossless compression is based on the observation that fixed-width encoding wastes space. Giving the letters 'A' and 'X' both 8 bits is wasteful if 'A' occurs 10 times more frequently than 'X'. Therefore, the basis of the algorithm is: if some symbols appear more often than others, assign the more frequent symbols shorter codes.

$$
\begin{aligned}
\text{Compression:}&\quad \text{File}_{100\text{MB}} \xrightarrow{\text{encode}} \text{File}_{70\text{MB}} \\[6pt]
\text{Decompression:}&\quad \text{File}_{70\text{MB}} \xrightarrow{\text{decode}} \text{File}_{100\text{MB}}
\end{aligned}
$$

The reason Huffman encoding is useful is that conventional character encodings assign a fixed number of bits to every symbol in the alphabet. ASCII, for example, allocates eight bits per character irrespective of its frequency. This creates a memory inefficiency, since fixed-width encoding expends identical storage on symbols of potentially significantly different utility. Huffman encoding solves this by eliminating the redundancy through assigning shorter code words to higher-frequency symbols. The justification behind this principle will be explored in more depth throughout the report.


- What is the algorithm/datastructure?
- What is the problem it solves? 
- Provide a brief history of the algorithm/datastructure. (make sure to cite sources)
- Provide an introduction to the rest of the paper. 


## Analysis of Algorithm/Datastructure
Make sure to include the following:
- Time Complexity
- Space Complexity
- General analysis of the algorithm/datastructure

## Empirical Analysis
- What is the empirical analysis?
- Provide specific examples / data.


## Application
- What is the algorithm/datastructure used for?
- Provide specific examples
- Why is it useful / used in that field area?
- Make sure to provide sources for your information.


## Implementation
- What language did you use?
- What libraries did you use?
- What were the challenges you faced?
- Provide key points of the algorithm/datastructure implementation, discuss the code.
- If you found code in another language, and then implemented in your own language that is fine - but make sure to document that.


## Summary
- Provide a summary of your findings
- What did you learn?

## LLM Use Disclosure 


## References

1. Inna Pivkina. [n. d.]. Discovery of Huffman Codes. Retrieved August 4, 2026 from https://www.cs.nmsu.edu/historical-projects/Projects/18920140825Huffman.pdf
