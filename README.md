# I "Hate" Papers

**Create easily readable versions of papers via OpenAI**

I often need to read a paper to provide background on a related topic. 
In these cases the technical depth of a paper can be a major obstacle.
So I created I Hate Papers to create easily digestible versions of 
academic research.

# Installation

    pip install i-hate-papers

# Example use
    
    # First set your OpenAI API key
    ❱ export OPENAI_API_KEY=...
    
    # Summarise a arXiv paper ID
    ❱ i_hate_papers 2106.09685
    
    # Summarise a latex file
    ❱ i_hate_papers path/to/some-paper.tex

# Example output

* [Example Markdown](https://github.com/adamcharnock/i-hate-papers/blob/main/examples/summary-2106.09685-d1-gpt-3.5-turbo.md)
* [Example HTML](https://adamcharnock.github.io/i-hate-papers/examples/summary-2106.09685-d1-gpt-3.5-turbo.html) (includes rendered math using MathJax)

# Reference

    ❱ i_hate_papers --help
    usage: i_hate_papers [-h] [--verbosity {0,1,2}] [--no-input] [--no-html] [--no-open] 
                         [--detail-level {0,1,2}] [--model MODEL] INPUT
    
    Summarise an arXiv paper
    
    You must set the OPENAI_API_KEY environment variable using your OpenAi.com API key
    
    positional arguments:
      INPUT                 arXiv paper ID (example: 1234.56789) or path to a .tex file
    
    options:
      -h, --help            show this help message and exit
      --verbosity {0,1,2}   Set the logging verbosity (0 = quiet, 1 = info logging, 2 = debug logging). Default is 1
      --no-input            Don't prompt for file selection, just use the largest tex file
      --no-html             Skip HTML file generation
      --no-open             Don't open the HTML file when complete (macOS only)
      --detail-level {0,1,2}
                            How detailed should the summary be? (0 = minimal detail, 1 = normal, 2 = more detail)
      --model MODEL         What model to use to generate the summaries

# Release process

For internal use:

    export VERSION=0.1.0 
    git tag "v$VERSION"      
    git push origin  refs/tags/v$VERSION
    poetry publish --build