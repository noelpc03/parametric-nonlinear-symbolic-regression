Advanced Bibliographical and Analytical Framework for Root-Finding in Scalar Functions and Multivariate Polynomial Systems
The identification of zeros within mathematical functions and the resolution of complex systems of equations constitute one of the most enduring challenges in the mathematical sciences. For the researcher engaged in thesis-level work, the landscape is divided between the iterative precision of numerical analysis and the structural rigor of computational algebraic geometry. This report provides an exhaustive bibliographical and technical survey of these methodologies, with a particular emphasis on the theory and application of Gröbner bases, which represent the primary tool for the symbolic manipulation of polynomial ideals. The following analysis synthesizes foundational texts, seminal algorithms, high-performance software documentation, and contemporary research trends to provide a comprehensive roadmap for the study of function zeros.
Foundational Frameworks in Numerical Root-Finding and Function Analysis
Numerical methods for finding zeros are traditionally the first line of defense in applied mathematics, engineering, and the physical sciences. These techniques prioritize the approximation of solutions through iterative refinement, often where an analytical or exact symbolic solution is either unknown or computationally expensive. The bibliography in this domain is extensive, beginning with the established standards for mathematical constants and special functions.
The Handbook of Mathematical Functions by Abramowitz and Stegun remains a critical reference for the definition and approximation of special functions, providing the essential formulas, graphs, and tables required to verify the behavior of numerical root-finding algorithms.[1, 2] For the researcher, this text serves as a benchmark for evaluating the accuracy of computed zeros in transcendental functions. Further depth in the general application of approximation techniques is found in the work of Faires and Burden, who emphasize the implementation of numerical routines in engineering contexts.[3] Their work is particularly valuable for its focus on error analysis—explaining not only why methods work but where they are likely to fail due to singularities or ill-conditioned data.[3]
Scalar Iteration and Convergence Theory
The study of zeros in univariate functions f(x)=0 is characterized by a progression from simple bracketing methods to high-order iterative schemes. Textbooks such as Kendall Atkinson’s An Introduction to Numerical Analysis provide the theoretical underpinnings for these methods, detailing the convergence rates and stability of the Bisection method, the Secant method, and the Newton-Raphson method.[1]
The mathematical mechanism behind these iterative solvers is deeply rooted in the Taylor series expansion. As noted in introductory material on numerical methods, the Taylor series and finite difference calculus form the basic building blocks for constructing approximation routines.[4] For a function f(x) near a root x∗, the expansion:
f(x)≈f(x0​)+f′(x0​)(x−x0​)+2f′′(x0​)​(x−x0​)2+…
allows for the derivation of the Newton iteration xn+1​=xn​−f(xn​)/f′(xn​), which typically exhibits quadratic convergence provided the initial guess is sufficiently close to x∗ and f′(x∗)=0.[3] The literature explores various modifications to these schemes to handle multiple roots and functions where derivatives are difficult to compute, leading to the development of derivative-free optimization methods.[1]
Multivariate Systems and Linearized Operators
When transitioning to systems of equations F(x)=0, the complexity shifts to the management of the Jacobian matrix J(x)=[∂fi​/∂xj​]. The multivariate Newton method requires the solution of a linear system at each iteration:
J(xk​)Δxk​=−F(xk​)
Foundational references such as Golub and Van Loan’s Matrix Computations are essential for understanding the numerical linear algebra required to solve these systems efficiently, particularly regarding the use of LU decomposition, QR factorization, and iterative methods for large, sparse matrices.[1] In many cases, particularly in differential-algebraic equations (DAEs), the root-finding process is embedded within the solution of initial-value problems, as discussed by Brenan, Campbell, and Petzold.[1]
Method Category
	
Notable Authors
	
Primary Focus
	
Application Domain
General Numerical Analysis
	
Atkinson, Burden, Faires
	
Error theory and convergence [1, 3]
	
Engineering, Physics
Matrix Computations
	
Golub, Van Loan, Leon
	
Linear system resolution [1]
	
Computational Science
Special Functions
	
Abramowitz, Stegun
	
Standardized mathematical definitions [1, 2]
	
Theoretical Mathematics
Least Squares
	
Björck, Levenberg
	
Overdetermined system optimization [1]
	
Statistics, Modeling
The Paradigm of Computational Algebraic Geometry: Gröbner Bases
For the thesis researcher, the symbolic approach provided by algebraic geometry offers a more robust framework for systems where exact solutions or the qualitative structure of the solution set are required. The centerpiece of this field is the Gröbner basis, a concept that has transformed commutative algebra into a computational discipline.
Historical Context and Buchberger's Innovation
Gröbner bases were introduced by Bruno Buchberger in his 1965 doctoral thesis under the supervision of Wolfgang Gröbner.[5, 6] Buchberger’s primary contribution was the discovery of an algorithm that transforms an arbitrary set of polynomials into a "standard" or "Gröbner" basis for the same ideal, enjoying properties that make questions about the ideal algorithmically decidable.[7, 8]
Before Buchberger's work, finding the zeros of a multivariate system was hampered by the fact that the division algorithm for polynomials in one variable does not naturally generalize to multiple variables without a specific ordering of terms.[9, 10] Buchberger’s algorithm provides a common generalization of the Euclidean algorithm (for univariate polynomials) and Gaussian elimination (for linear systems).[7, 11, 12]
Theoretical Foundations in Ideal and Variety Theory
The study of polynomial systems is essentially the study of algebraic varieties—the sets of points where all polynomials in a given ideal vanish.[9, 13] The relationship between the algebraic object (the ideal I) and the geometric object (the variety V(I)) is the core of the algebra-geometry dictionary.[14] Seminal works in this area include:

    Cox, Little, and O’Shea (Ideals, Varieties, and Algorithms): This text is widely regarded as the most accessible entry point for undergraduates and researchers. it covers the Hilbert Basis Theorem, which guarantees the existence of finite bases, and the Nullstellensatz, which relates ideals to varieties in algebraically closed fields.[9, 10, 15]
    Becker, Weispfenning, and Kredel (Gröbner Bases: A Computational Approach to Commutative Algebra): This comprehensive graduate-level text provides the rigorous mathematical verification of Buchberger’s algorithm and explores extensions to modules and non-commutative rings.[11, 16]
    Bernd Sturmfels (Solving Systems of Polynomial Equations): This work bridges symbolic and numerical techniques, discussing the state-of-the-art in polynomial system solving as of the early 2000s, including applications in statistics, economics, and game theory.[13, 17, 18]

Concept
	
Definition/Significance
	
Reference
Monomial Ordering
	
A total ordering on the set of monomials (lex, degrevlex, etc.) [19]
	
Cox et al. [9]
S-Polynomial
	
A combination of two polynomials designed to cancel their leading terms [8]
	
Buchberger [7]
Buchberger’s Criterion
	
A set is a Gröbner basis iff all S-polynomials reduce to zero [7, 8]
	
Becker et al. [16]
Reduced Gröbner Basis
	
A unique basis for any ideal given a fixed monomial ordering [5, 19]
	
Lazard [5]
Mechanism of the Buchberger Algorithm
The algorithm proceeds by considering pairs of polynomials from an initial set B. For each pair (f,g), an S-polynomial S(f,g) is computed. This S-polynomial is then reduced with respect to the current set G using a multivariate division algorithm.[7, 19] If the remainder is non-zero, it is added to G, and new pairs are generated. The process terminates when all S-polynomials reduce to zero, a condition guaranteed by the Hilbert Basis Theorem, which ensures that there are no infinite ascending chains of ideals in the polynomial ring K[x1​,…,xn​].[14, 15, 20]
Advanced Computational Techniques: Efficiency and Scale
While the basic Buchberger algorithm is theoretically powerful, its worst-case complexity is doubly exponential in the number of variables.[7] This has necessitated the development of more efficient algorithms and the exploitation of specialized mathematical structures.
The F4 and F5 Algorithms by Jean-Charles Faugère
The modern standard for computing Gröbner bases is defined by the work of Jean-Charles Faugère. His F4 algorithm, published in 1999, replaces the individual reduction of S-polynomials with sparse linear algebra.[5, 21] By forming a large matrix where rows are polynomials and columns are monomials, F4 can reduce many polynomials simultaneously, taking advantage of high-performance libraries for matrix row reduction.[21, 22]
The F5 algorithm (2002) further optimized this process by introducing signatures to track the origin of polynomials. This allows the algorithm to avoid "reductions to zero"—computational steps that result in no new basis elements—by predicting which pairs will be redundant based on the known syzygies (polynomial relations) of the generators.[5, 21, 23] Research has shown that F5 is particularly efficient for "regular" or "semi-regular" systems, which are common in cryptographic applications.[5, 24, 25]
Elimination Theory and Variable Hiding
One of the primary uses of Gröbner bases in solving systems is elimination theory. By using a lexicographic (lex) monomial ordering, a Gröbner basis can be computed that behaves like a triangular system.[12, 14] In a zero-dimensional system (one with a finite number of solutions), the last element of a lex basis will be a univariate polynomial in the last variable, allowing for its roots to be found numerically or symbolically.[6, 13, 25]
However, computing a lex basis is often much slower than computing a degree-reverse lexicographic (degrevlex) basis.[5] This has led to the FGLM algorithm, which converts a degrevlex basis into a lex basis for zero-dimensional ideals with a complexity that is polynomial in the number of solutions.[5, 12, 26] Alternatively, researchers may use resultants—determinants of Macaulay matrices—to eliminate variables without the full overhead of a Gröbner basis computation.[27, 28, 29]
Numerical Algebraic Geometry and Homotopy Methods
A parallel development in the search for zeros is the field of numerical algebraic geometry, which utilizes homotopy continuation to track solutions from a known start system to a target system.
Homotopy Continuation and Path Tracking
Homotopy continuation is a hybrid symbolic-numeric approach that solves a target system F(x)=0 by embedding it in a family of systems H(x,t)=(1−t)G(x)+tF(x). Starting at t=0 with the known solutions of G(x), numerical path-tracking techniques follow these solutions as t moves toward 1.[27, 29]
Sommese and Wampler’s The Numerical Solution of Systems of Polynomials is the foundational text for this methodology.[27] Unlike Gröbner basis methods, which can become numerically unstable when using floating-point arithmetic, homotopy continuation is inherently numerical but provides global guarantees: it is designed to find all isolated roots of a polynomial system.[27, 30, 31]
Sparse Resultants and Minimal Solvers
In applications like computer vision, where systems must be solved in milliseconds, "minimal solvers" are developed using sparse resultants. These methods exploit the Newton polytope of the polynomials to construct smaller elimination templates than those required by general Gröbner basis methods.[30, 32, 33] Recent work has compared resultant-based methods against Gröbner-based solvers, showing that resultants can lead to more stable and compact solvers for certain geometric problems, such as camera pose estimation.[32, 33]
Algorithm Type
	
Key Characteristics
	
Scalability
	
Numerical Stability
Buchberger
	
S-polynomial reduction [7]
	
Low (doubly exponential)
	
Low (symbolic preferred)
F4/F5
	
Matrix-based / Syzygy criteria [5, 21]
	
High (state-of-the-art)
	
Low (requires exact arithmetic)
FGLM
	
Order conversion for zero-dim ideals [5]
	
Medium (depends on # roots)
	
Moderate
Homotopy
	
Path tracking from G(x) to F(x) [27]
	
High (for isolated roots)
	
High (with path tracking)
Sparse Resultant
	
Newton polytope exploitation [30]
	
High (for sparse systems)
	
Moderate to High
Software Ecosystems and Implementation Strategies
For a thesis involving the search for zeros, selecting the appropriate software environment is critical. The landscape is dominated by specialized computer algebra systems (CAS) and high-performance libraries.
Specialized Computer Algebra Systems: Singular and Macaulay2

    Singular: Directed by Gert-Martin Greuel, Gerhard Pfister, and Hans Schönemann, Singular is specifically tailored for polynomial computations in commutative and non-commutative algebra, algebraic geometry, and singularity theory.[34, 35, 36] It is known for having one of the fastest implementations of various Gröbner basis algorithms, including Buchberger's and Mora’s tangent cone algorithm.[34] Singular’s libraries, such as normal.lib for computing the normalization of affine rings, provide high-level mathematical functionality beyond basic basis computation.[37, 38]
    Macaulay2: Developed by Daniel Grayson and Michael Stillman, Macaulay2 is a system designed to support research in algebraic geometry and commutative algebra.[39, 40, 41] It features a powerful interpreted language for defining high-level mathematical objects (quotient rings, modules, schemes) and uses a compiled C++ core for its Gröbner basis engine.[40, 42] Macaulay2 is particularly well-suited for researchers who need to perform complex experiments in scheme theory or local algebra.[41, 43]

The msolve Library and High-Performance Solving
A more recent development is the msolve library, a C library dedicated to solving multivariate polynomial systems of dimension zero.[26, 44, 45] msolve represents a significant advancement in the field, as it integrates F4-style Gröbner basis computation over prime fields with multi-modular techniques to solve systems over the rational numbers.[45, 46, 47]
One of the key features of msolve is its implementation of the Rational Univariate Representation (RUR), which provides an algebraic parametrization of the solution set, as well as fast real-root isolation.[44, 45] By utilizing AVX2 vectorization and multi-threading, msolve has been shown to dramatically outperform traditional CAS for many challenging problems, such as those arising in cryptography and optimization.[5, 45]
Specialized and Hybrid Tools
For numerical algebraic geometry, PHCpack (Portable Homotopy Continuation) is the standard for solving systems via path tracking.[13, 48] In the MATLAB environment, the MacaulayLab toolbox provides numerical linear algebra algorithms for solving multivariate systems and multiparameter eigenvalue problems, working independently of a particular polynomial basis or monomial ordering.[49]
Software / Library
	
Core Algorithms
	
Primary Environment
	
Best Used For
Singular
	
Buchberger, Mora, F4/F5 variants [34, 38]
	
C++, Integrated Shell
	
Singularity theory, local rings
Macaulay2
	
GB, Free resolutions, Hilbert series [40, 42]
	
C++, Interpreted Language
	
Scheme theory, research
msolve
	
F4, FGLM, RUR, Real root isolation [44, 45]
	
C Library (AVX2, Threads)
	
Zero-dimensional systems over Q
PHCpack
	
Homotopy Continuation, Path tracking [13]
	
C / Interface to Python
	
Finding all complex solutions
MacaulayLab
	
Numerical Linear Algebra (Macaulay Matrix) [49]
	
MATLAB
	
Eigenvalue problems, numeric GB
Contemporary Research Frontiers (2015–2025)
The search for zeros continues to be a fertile ground for research, with recent papers pushing the boundaries of what is computationally feasible and exploring new application domains.
Complexity and Cryptographic Attacks
In the domain of post-quantum cryptography, the hardness of the Learning with Errors (LWE) problem is directly linked to the complexity of Gröbner basis computations on the associated polynomial systems.[24] Recent research has utilized the Castelnuovo-Mumford regularity and the Macaulay bound to estimate the solving degree—the maximum degree of polynomials generated during a basis computation—for these systems.[24] These estimates provide crucial bounds for the security parameters of cryptographic protocols.[24]
Machine Learning and Optimization in Polynomial Solving
An emerging trend is the application of deep learning to improve the efficiency of algebraic solvers. Research conducted between 2019 and 2024 has demonstrated that variable reordering—which traditionally requires heuristic choices—can be optimized using classification networks to select the most stable or fastest monomial ordering for a given system.[32] This "online stability improvement" represents a bridge between symbolic methods and data-driven optimization.[32]
Geometric Modeling and Computer Vision
The field of 3D computer vision remains one of the most prolific users of advanced polynomial solvers. The "Minimal Problems" involved in trifocal pose estimation and triangulation lead to polynomial systems with high degrees and many unknowns, some resulting in over 10,000 solutions.[30, 33, 50] Research in this area (2020–2025) has focused on reducing the size of elimination templates and using adaptive multi-precision to handle the inherent numerical instability of these high-degree systems.[29, 30]
A notable innovation is the use of "Simulator HC," where a regression-based online simulation is used to generate starting problem-solution pairs for homotopy continuation, enabling the tracking of a single solution efficiently rather than tracking all possible roots in the complex domain.[30, 33]
Theoretical Insights into Dimension and Stability
The nature of the solution set (the variety) fundamentally dictates the appropriate method for root-finding.
Dimension and Multiplicity
Systems are classified by their dimension: zero-dimensional systems have a finite number of complex solutions, while positive-dimensional systems have infinite solutions forming curves, surfaces, or higher-dimensional manifolds.[9, 14] Gröbner basis methods are uniquely suited for determining the dimension of a variety, as the number of "standard" monomials (those not in the leading term ideal) corresponds to the dimension of the quotient ring K[x1​,…,xn​]/I.[9, 19] For zero-dimensional systems, this number is exactly the number of solutions counted with multiplicity in an algebraically closed field.[5, 19]
The Real World: Real Root Isolation and Tame Functions
While algebraic geometry often works over algebraically closed fields (like C), practical applications often require real roots. Algorithms like msolve's real-root isolation are crucial for these cases.[44, 45] Furthermore, in analyzing the topology near singular points, Gröbner bases are used to determine if a real polynomial mapping has a Milnor fibration, a concept essential in the study of tame functions.[51]
Symbolic-Numeric Interoperability
Recent doctoral dissertations (2024) have explored how symbolic and numerical modes of computing can co-exist. The goal is to develop systems that can trace through numerical code to produce symbolic expressions and convert symbolic expressions back into high-quality numerical code at staged compilation time.[52] This symbiosis allows researchers to leverage the full power of algebraic manipulation while maintaining the performance required for engineering modeling.[52, 53]
Analysis of Complex Minimal Solvers in Computer Vision
The following data compares recent advancements in polynomial solvers specifically optimized for computer vision, illustrating the scale of the systems being addressed in contemporary research.
Problem Type
	
Number of Solutions
	
Method Used
	
Key Reference
	
Year
Point-Line Minimal Problems (PL1P)
	
High-degree
	
Elimination Templates [30]
	
Duff et al. [30]
	
2020
Tri-focal Relative Pose (Lines at points)
	
Complex set
	
Efficient HC (C++) [30]
	
Fabbri et al. [30]
	
2020
Generalized Three-view Relative Pose
	
Minimal set
	
GPU-based HC [30]
	
Ding et al. [30]
	
2023
Sparse Resultant Based Minimal Solvers
	
Sparse set
	
Sparse Resultant [32]
	
Bhayani et al. [32]
	
2024
Largest Successful Elimination Template
	
512
	
Octuple Precision [33]
	
Zhang et al. [33]
	
2025
Strategic Recommendations for Thesis Bibliography
In assembling a bibliography for a thesis focused on search for zeros and Gröbner bases, a researcher should structure their citations around the following pillars:

    Seminal Theory: Buchberger's original papers [5, 7, 8] and the foundational texts by Cox, Little, and O’Shea [9, 14, 54] provide the necessary theoretical background.
    State-of-the-Art Algorithms: Jean-Charles Faugère’s papers on F4 and F5 [21, 23] are essential for discussing modern computational efficiency.
    Numerical Context: References to Sommese and Wampler [27] and the comparison papers between symbolic and numerical solvers [50, 55] demonstrate a nuanced understanding of the field's breadth.
    Software Documentation: Citing the manuals and papers for Singular [34, 37], Macaulay2 [41], and msolve [26, 45] grounds the thesis in practical implementation.
    Targeted Applications: Depending on the thesis's specific area of application (e.g., Robotics [31], Cryptography [24], or Computer Vision [32]), the researcher should include the relevant recent works from Larsson, Kukelova, or Safey El Din.

The evolution of root-finding from simple iterative approximations to the sophisticated manipulation of polynomial ideals via signature-based Gröbner algorithms represents a significant arc in mathematical history. For the contemporary researcher, the integration of these symbolic techniques with numerical stability and hardware acceleration is the current frontier. The bibliographical landscape described herein provides the comprehensive foundation required to contribute to this expanding field.
--------------------------------------------------------------------------------

    References — Fundamentals of Numerical Computation - Toby Driscoll, https://tobydriscoll.net/fnc-julia/refs.html
    Numerical Methods for Special Functions | SIAM Publications Library, https://epubs.siam.org/doi/10.1137/1.9780898717822
    Numerical_Methods__Faires&Bu, https://uodiyala.edu.iq/uploads/PDF%20ELIBRARY%20UODIYALA/collect%20EL3/Numerical_Methods__Faires&Burden.pdf
    Numerical - Methods, https://blasingame.engr.tamu.edu/z_zCourse_Archive/P620_15C/P620_15C_zReference/PDF_Txt_Hnbk_Num_Meth.pdf
    Gröbner basis - Wikipedia, https://en.wikipedia.org/wiki/Gr%C3%B6bner_basis
    On Gröbner Bases and Their Uses in Solving System of Polynomial Equations and Graph Coloring, https://thescipub.com/pdf/jmssp.2018.175.182.pdf
    Buchberger's algorithm - Scholarpedia, http://www.scholarpedia.org/article/Buchberger%27s_algorithm
    Gr??bner Bases: A Short Introduction for Systems Theorists - ResearchGate, https://www.researchgate.net/publication/221432610_Grbner_Bases_A_Short_Introduction_for_Systems_Theorists
    Gröbner Bases Bibliography, https://www.risc.jku.at/Groebner-Bases-Bibliography/details.php?details_id=443
    An Introduction to Grobner Bases - American Mathematical Society, https://www.ams.org/books/gsm/003/gsm003-endmatter.pdf
    Gröbner Bases: A Computational Approach To Commutative Algebra (Graduate Texts In Mathematics) - Thomas Becker, http://www.iri.csic.es/people/thomas/Collection/details/17562.html
    Gröbner Basis -- from Wolfram MathWorld, https://mathworld.wolfram.com/GroebnerBasis.html
    Solving Systems of Polynomial Equations Bernd Sturmfels, https://math.berkeley.edu/~bernd/cbms.pdf
    Ideals, Varieties, and Algorithms, https://www.nzdr.ru/data/media/biblio/kolxoz/M/MA/MAco/Cox%20D.,%20Little%20J.,%20O'Shea%20D.%20Ideals,%20Varieties,%20and%20Algorithms(3ed.,%20Springer,%202007)(ISBN%200387356509)(565s)MAco.pdf
    OPERA TIONS RESEARCH CENTER Working Paper MASSACHUSETTS INSTITUTE OF TECHNOLOGY - DSpace@MIT, http://dspace.mit.edu/bitstream/handle/1721.1/5359/OR-329-98-43940446.pdf;sequence=1
    Gröbner Bases: A Computational Approach to Commutative Algebra - Thomas Becker, Volker Weispfenning, Heinz Kredel - Google Books, https://books.google.com/books/about/Gr%C3%B6bner_Bases.html?id=qoU_AQAAIAAJ
    Solving systems of polynomial equations - University of California Santa Barbara, https://search.library.ucsb.edu/discovery/fulldisplay?vid=01UCSB_INST%3AUCSB&docid=alma990024134250203776&context=L
    CBMS Conference on Solving Polynomial Equations, http://ndl.ethernet.edu.et/bitstream/123456789/33048/1/14.pdf.pdf
    Gröbner Bases — Theory and Applications Franz Winkler Research Institute for Symbolic Computation (RISC-Linz) Johannes Kepler, https://www.risc.jku.at/projects/science/school/fifth/materials/GB.pdf
    On Grobner Bases and Their Applications | ID: tq57p6879 - Carolina Digital Repository, https://cdr.lib.unc.edu/concern/dissertations/tq57p6879
    Faugère's F4 and F5 algorithms - Wikipedia, https://en.wikipedia.org/wiki/Faug%C3%A8re%27s_F4_and_F5_algorithms
    An Algorithm For Splitting Polynomial Systems Based On F4 - CECM, https://www.cecm.sfu.ca/CAG/papers/pascoRomMon17.pdf
    F4/5 - Academia.edu, https://www.academia.edu/932599/F4_5
    arXiv:2402.07852v3 [cs.CR] 29 Mar 2025, https://arxiv.org/pdf/2402.07852
    Gröbner-Bases, Gaussian elimination and resolution of systems of algebraic equations, https://www.semanticscholar.org/paper/Gr%C3%B6bner-Bases%2C-Gaussian-elimination-and-resolution-Lazard/698aa381d52839b50db9353dac8eef7c6414e93d
    [2104.03572] msolve: A Library for Solving Polynomial Systems - arXiv, https://arxiv.org/abs/2104.03572
    The Numerical Solution of Systems of Polynomials Arising in Engineering and Science, https://www.worldscientific.com/worldscibooks/10.1142/5763
    (PDF) Solving Systems of Polynomial Equations - ResearchGate, https://www.researchgate.net/publication/3208374_Solving_Systems_of_Polynomial_Equations
    numerical solution of bivariate and polyanalytic polynomial systems - Lirias, https://lirias.kuleuven.be/retrieve/38a37e1e-f946-4214-8a21-0d496919c001
    Simulator HC: Regression-based Online Simulation of Starting ..., https://arxiv.org/pdf/2411.03745
    Finding Only Finite Roots to Large Kinematic Synthesis Systems | J. Mechanisms Robotics, https://asmedigitalcollection.asme.org/mechanismsrobotics/article/9/2/021005/473072/Finding-Only-Finite-Roots-to-Large-Kinematic
    [PDF] Beyond Grobner Bases: Basis Selection for Minimal Solvers ..., https://www.semanticscholar.org/paper/492fcea5cc0a9a9446c1caa1e14ec3864deeb454
    Regression-based Online Simulation of Starting Problem-Solution Pairs for Homotopy Continuation in Geometric Vision, https://openaccess.thecvf.com/content/CVPR2025/papers/Zhang_Simulator_HC_Regression-based_Online_Simulation_of_Starting_Problem-Solution_Pairs_for_CVPR_2025_paper.pdf
    Singular A Computer Algebra System for Polynomial Computations Manual Version 1.2, https://d-nb.info/1026737532/34
    List of computer algebra systems - Wikipedia, https://en.wikipedia.org/wiki/List_of_computer_algebra_systems
    (PDF) Singular-Tutorial - ResearchGate, https://www.researchgate.net/publication/228796179_Singular-Tutorial
    How to cite SINGULAR, https://www.singular.uni-kl.de/index.php/how-to-cite-singular.html
    Singular Manual, http://fe.math.kobe-u.ac.jp/icms2010-dvd/Singular/singular.pdf
    Computations in algebraic geometry with Macaulay 2 - Stanford University, http://stanford.edu/~mluciano/m2book.pdf
    Macaulay2 - Preface, https://macaulay2.com/Book/ComputationsBook/chapters/preface/chapter-wrapper.pdf
    Macaulay2Doc -- Macaulay2 documentation, https://macaulay2.com/doc/Macaulay2/share/doc/Macaulay2/Macaulay2Doc/html/index.html
    Computations in algebraic geometry with Macaulay 2, https://macaulay2.com/Book/ComputationsBook/book/book.pdf
    [math/0003033] Macaulay 2 and the geometry of schemes - arXiv, https://arxiv.org/abs/math/0003033
    Macaulay2 interface for msolve; computes real solutions and Groebner basis, etc., https://macaulay2.com/doc/Macaulay2/share/doc/Macaulay2/Msolve/html/index.html
    How to solve multivariate polynomial systems with msolve?, https://msolve.lip6.fr/downloads/msolve-tutorial.pdf
    algebraic-solving/msolve: Library for Polynomial System Solving through Algebraic Methods - GitHub, https://github.com/algebraic-solving/msolve
    msolve - Mohab Safey El Din - GitLab, https://gitlab.lip6.fr/safey/msolve
    Some examples for solving systems of algebraic equations by calculating Groebner bases, https://www.researchgate.net/publication/223218307_Some_examples_for_solving_systems_of_algebraic_equations_by_calculating_Groebner_bases
    Solving Multivariate Polynomial Systems and Rectangular Multiparameter Eigenvalue Problems with MacaulayLab - Index of /, https://ftp.esat.kuleuven.be/pub/stadius/cvermeer/25-90.pdf
    GPU-Based Homotopy Continuation for Minimal Problems in Computer Vision, https://par.nsf.gov/servlets/purl/10393153
    "Gröbner bases with an application to tame functions" by Jessica D. Marconi, https://digitalcommons.unf.edu/etd/1287/
    Symbolic-numeric programming in scientific computing Shashi Gowda - DSpace@MIT, https://dspace.mit.edu/bitstream/handle/1721.1/155320/gowda-gowda-phd-math-2024-thesis.pdf?sequence=1&isAllowed=y
    A Modular Programming Language for Engineering Design - DSpace@MIT, https://dspace.mit.edu/bitstream/handle/1721.1/43080/244385026-MIT.pdf?sequence=2
    VL: Discrete Geometry: Polytopes and Polynomials, WS 14/15 - Institut für Mathematik - TU Berlin, https://www3.math.tu-berlin.de/Vorlesungen/WS14/DiskGeom2/
    Complexity: Groebner bases method vs homotopy continuation method - MathOverflow, https://mathoverflow.net/questions/404857/complexity-groebner-bases-method-vs-homotopy-continuation-method