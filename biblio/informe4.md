
Skip to main content
For regression, what loss functions do people actually use besides MSE and MAE? : r/MLQuestions
Log In
r/MLQuestions icon
Go to MLQuestions
r/MLQuestions
•
2mo ago
Final-Literature2624
For regression, what loss functions do people actually use besides MSE and MAE?

In most regression setups, MSE or MAE seems to be the default choice, but in practice they often feel quite limiting, especially when there are outliers or skewed error distributions.

So I am curious:

    What loss functions are actually used in practice or research besides MSE and MAE?

        Huber, log-cosh, quantile loss, etc. get mentioned a lot, but are any of these common go-to choices?

    When outliers matter, is it more typical to change the loss function, or handle the issue via data preprocessing, reweighting, or evaluation metrics?

    In deep learning settings such as GNNs or Transformers for regression, are there any informal rules of thumb like "if you have this kind of data, use that loss"?

I am more interested in experience-based answers, what you have tried, what worked, and what did not, rather than purely theoretical explanations.
11
·
16
Comments Section
u/New-Mathematician645 avatar
New-Mathematician645
•
2mo ago

One thing I’ve run into a lot is that when people reach for a different loss, they’re often trying to fix something that isn’t really a loss problem. In several projects, the big errors weren’t evenly spread, they were clustered around certain parts of the data.

Swapping MSE for Huber or something more “robust” helped a little, but the real gains came from changing which samples actually had influence during training, via reweighting, resampling, or influence-style approaches, while keeping the loss itself very boring.

Once that was in place, plain MSE or Huber worked surprisingly well. The loss just needed to be stable. The heavy lifting was really happening upstream in how the data contributed to learning.

For context, this is roughly the approach we’ve been working with: instead of full retrains, we use influence functions at the example and dataset level. Each sample is scored by how much it pushes or pulls a target concept using projected gradients from the final block, which lets us rank data before spending GPU on training.

Link for anyone curious: https://durinn-concept-explorer.azurewebsites.net/
1
u/GBNet-Maintainer avatar
GBNet-Maintainer
•
2mo ago

Some of the answers here come from a combination of factors. (a) How are you evaluating your predictions (b) what loss can actually be optimized (c) what the data represents and looks like. 

If outliers are important in your evaluation, then maybe don't remove them before fitting.

If you want to fit standard deviation components at the same time as the mean, the optimization is much more difficult.

If you have count data, it makes sense to represent the observations as draws from a Poisson distribution. In this case your loss is the negative log likelihood of a Poisson distribution.
2
slashdave
•
2mo ago

MAE is insensitive to outliers, which is the point.

https://en.wikipedia.org/wiki/Robust_regression#Least_squares_alternatives

Statistics makes use of all sorts of tailed distributions.

https://en.wikipedia.org/wiki/Heavy-tailed_distribution
2
Glass_Ordinary4572
•
2mo ago

Generally it's rmse or r2 score.

Regarding outliers, yes it is important to treat those in the preprocessing step. Techniques like winsorization help

ANN works for regression problems, haven't really used any transformer based problems for regression tasks.
0
u/shumpitostick avatar
shumpitostick
•
2mo ago

These are evaluation metrics, not loss functions.
6
Glass_Ordinary4572
•
2mo ago

My bad, r2 score is not a loss function. However in case of regression, loss functions and performance metrics are generally the same. So rmse scan still be considered.
1
u/Fresh_Sock8660 avatar
Fresh_Sock8660
•
2mo ago

I think MSE is just so good and simple that it makes most people think there's gotta be something smarter to use.

Have a look through the list of loss functions in Torch or Tensorflow/Keras. Those tend to be popular enough to make it into the main.

Other things you could consider is combining loss functions but that tends to be very problem specific. 
1
u/madrury83 avatar
madrury83
•
2mo ago

Quantile loss is quite useful in practice. A lot of problems are of the nature: I want to ensure that no more than some proportion of observations are larger than my predictions/forecasts. Quantile loss is a critical tool for these problems.

More generally: Generalized Linear Models and their associated loss/log-likelihood are a very rich source of alternate loss functions that have good conceptual grounding. Poisson loss is useful for counts, especially when the exposure time/area/volume varies. Gamma loss is used for stuff like transaction sizes or claim amounts. Their combination, the Tweedie loss, is the foundation of casualty insurance pricing.
12
Related Answers Section
Related Answers
Huber loss advantages over MSE for outliers
Understanding loss functions in regression
MSE vs MAE in regression analysis
Mean error versus mean absolute error
Best practices for data preprocessing in ML
New to Reddit?

Create your account and connect with a world of communities.
Continue With Phone Number
By continuing, you agree to our User Agreement and acknowledge that you understand the Privacy Policy.
More posts you may like

    EnVision math advice
    r/mathteachers
    •
    5mo ago
    EnVision math advice
    6 upvotes · 11 comments
    Multiple regression advice wanted
    r/econometrics
    •
    4mo ago
    Multiple regression advice wanted
    r/econometrics - Multiple regression advice wanted
    2
    44 upvotes · 14 comments
    How to do Maths for MSQE
    r/ISIKolkata icon
    r/ISIKolkata
    •
    2mo ago
    How to do Maths for MSQE
    10 upvotes · 18 comments
    Tips to succeed in regression?
    r/OMSA icon
    r/OMSA
    •
    5mo ago
    Tips to succeed in regression?
    6 upvotes · 10 comments
    Items that make ms easier
    r/MultipleSclerosis
    •
    4d ago
    Items that make ms easier
    27 upvotes · 71 comments
    Why do some engineering solutions seem ridiculous until you actually think about them?
    r/Engineers
    •
    2mo ago
    Why do some engineering solutions seem ridiculous until you actually think about them?
    42 upvotes · 34 comments
    Loss curves like this will be the death of me.
    r/reinforcementlearning
    •
    3mo ago
    Loss curves like this will be the death of me.
    r/reinforcementlearning - Loss curves like this will be the death of me.
    42 upvotes · 8 comments
    Single-handedly changing Mercs economics 😭
    r/MercenariesGames icon
    r/MercenariesGames
    •
    2mo ago
    Single-handedly changing Mercs economics 😭
    r/MercenariesGames - Single-handedly changing Mercs economics 😭
    116 upvotes · 35 comments
    Need advice for math
    r/HiSET icon
    r/HiSET
    •
    7mo ago
    Need advice for math
    r/HiSET - Need advice for math
    8 upvotes · 12 comments
    Whats the difference between Foresight and prediction
    r/IntelligenceScaling icon
    r/IntelligenceScaling
    •
    7mo ago
    Whats the difference between Foresight and prediction
    r/IntelligenceScaling - Whats the difference between Foresight and prediction
    2
    14 upvotes · 9 comments
    Econometrics help
    r/stata
    •
    1mo ago
    Econometrics help
    5 upvotes · 13 comments
    Market research!
    r/Speedsoft icon
    r/Speedsoft
    •
    9mo ago
    Market research!
    r/Speedsoft - Market research!
    34 upvotes · 38 comments
    High variance in potential outcomes
    r/trolleyproblem icon
    r/trolleyproblem
    •
    3mo ago
    High variance in potential outcomes
    r/trolleyproblem - High variance in potential outcomes
    98 upvotes · 40 comments
    Has there been any major solves since the end of 2024?
    r/Lostwave icon
    r/Lostwave
    •
    5mo ago
    Has there been any major solves since the end of 2024?
    26 upvotes · 31 comments
    Grading question
    r/Morgans icon
    r/Morgans
    •
    1mo ago
    Grading question
    r/Morgans - Grading question
    2
    27 upvotes · 7 comments
    Depreciation curves are way off
    r/MacanEV icon
    r/MacanEV
    •
    4mo ago
    Depreciation curves are way off
    r/MacanEV - Depreciation curves are way off
    2
    41 upvotes · 61 comments
    Why has value prediction not gained more relevance?
    r/computerarchitecture icon
    r/computerarchitecture
    •
    3mo ago
    Why has value prediction not gained more relevance?
    29 upvotes · 10 comments
    It really is getting useful.
    r/BetterOffline icon
    r/BetterOffline
    •
    1mo ago
    It really is getting useful.
    9 comments
    Levers of Operational Excellence - Help me challenge my framework.
    r/LeanManufacturing
    •
    6mo ago
    Levers of Operational Excellence - Help me challenge my framework.
    r/LeanManufacturing - Levers of Operational Excellence - Help me challenge my framework.
    14 upvotes · 9 comments
    Recommendation on CS classes
    r/SMC icon
    r/SMC
    •
    7mo ago
    Recommendation on CS classes
    6 upvotes · 15 comments
    Less is more? Have you done math before?
    r/writingcirclejerk icon
    r/writingcirclejerk
    •
    2mo ago
    Less is more? Have you done math before?
    71 upvotes · 9 comments
    What is methodology?
    r/IntelligenceScaling icon
    r/IntelligenceScaling
    •
    9mo ago
    What is methodology?
    9 upvotes · 4 comments
    Math of Movement
    r/Bryce3D icon
    r/Bryce3D
    •
    8mo ago
    Math of Movement
    r/Bryce3D - Math of Movement
    101 upvotes · 7 comments
    Increasing performance question
    r/frackinuniverse icon
    r/frackinuniverse
    •
    9d ago
    Increasing performance question
    r/frackinuniverse - Increasing performance question
    32 upvotes · 9 comments
    Regarding Semester 2 Math (core)
    r/Manipal_Academics icon
    r/Manipal_Academics
    •
    2mo ago
    Regarding Semester 2 Math (core)
    21 upvotes · 19 comments

View Post in
Português (Brasil)
हिन्दी
Community Info Section
r/MLQuestions
Machine Learning Questions
A place for beginners to ask stupid questions and for experts to help them! /r/Machine learning is a great subreddit, but it is for interesting articles and news related to machine learning. Here, you can feel free to ask any question regarding machine learning.
Public
Reddit Rules Privacy Policy User Agreement Your Privacy Choices Accessibility Reddit, Inc. © 2026. All rights reserved.
