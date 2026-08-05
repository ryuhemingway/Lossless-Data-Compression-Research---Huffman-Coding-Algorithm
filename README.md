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


- What is the algorithm/datastructure? (Done)
- What is the problem it solves? (Done)
- Provide a brief history of the algorithm/datastructure. (make sure to cite sources)(Done)
- Provide an introduction to the rest of the paper. (Done)


## Analysis of Algorithm/Datastructure:

### Time Complexity:

When analysing the time and space complexity of Huffman's algorithm, two parameters govern the result. Let n denote the number of distinct symbols in the source alphabet, and m the total number of symbols in the input. For byte oriented input, n cannot exceed 256, since a byte represents atmost 256 distinct values, whereas m grows without bound as the file grows. For any input of non trivial length it follows that n ≪ m, and the two parameters must therefore be kept distinct since they appear in different terms of the cost.

The algorithm runs in four steps:

1. Count how many times each distinct symbol occurs in the input file.
2. Build the code tree from those counts: make each symbol a leaf weighted by its count, then repeatedly merge the two lowest-weight nodes under a new parent whose weight is their sum, until one node remains.
3. Read each symbol's codeword off the tree by walking from the root to its leaf, appending 0 for a left step and 1 for a right step.
4. Encode the file in a second pass, replacing each symbol with its codeword.

Counting and encoding only take 1 passover of the data so each one costs Θ(m). Building the tree costs O(n log n), giving a total of Θ(m + n log n).

The cost of the tree comes from merging the loop. Each merge needs the two smallest remaining weights, then the heap finds the smallest in O(n log n) time. For building a tree of n leaves and n-1 internal nodes, it will take 2n-1 insert and 2n-1 extractMin operations which with a binary heap gives O(n log n)[2]. An important point to note is that the log factor comes from sorting, not merging. Van Leeuwen proved this by showing the tree can be built in linear time if the weights are already sorted since internal nodes are are ceated and consumed in non-decreasing weight order[3]. His technique is called the Two-Queue Method.

### Space Complexity:

In terms of space complexity, the tree hold n leaves and n-1 internal nodes so 2n-1 nodes in total. The heap and fequency table also run at Θ(n) giving the total working space Θ(n).

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

2. N. G. Machado, D. L. L. de Oliveira, and M. T. Valente. 2019. Cross-Language GUI Widget Detection for Automated Testing. In *Proceedings of the 2019 27th ACM Joint Meeting on European Software Engineering Conference and Symposium on the Foundations of Software Engineering (ESEC/FSE 2019)*. ACM, New York, NY, USA, 352–362. https://doi.org/10.1145/3342555

3. Alistair Moffat. 2019. Huffman Coding. ACM Comput. Surv. 52, 4, Article 85 (August 2019), 35 pages. https://doi.org/10.1145/3342555
 