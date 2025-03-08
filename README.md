# LocalAI Bench
Your personal AI benchmarking tool.

## Introduction
LocalAI Bench is a benchmarking tool for AI models. It provides a platform to evaluate and compare different AI models based on various tasks and categories. It supports multiple AI models from Hugging Face hub via custom implementation or Ollama API. It also supports models from other API providers.

## Goal
The goal of LocalAI Bench is to provide a platform to evaluate and compare different AI models based on various tasks which are useful for the user.

It not aims to compare SOTA models, but a locally available models which are useful in a stituation where API usage is not recommended choise - like in a corporate environment, where data privacy is a concern or to reduce the cost of API usage.

Unlike other benchmarking tools, LocalAI Bench is not to provide a score on a general field, like Math, Physics or reasoning capabilites, but to compare AI models in categories usefull for the user like:
- specific document types understanding,
- agentic usage in a unique enterprise process,
- coding tasks on a specific language or framework or event corporate coding standards.


## Categories of benchmarks:
There is no limit to the number of categories and tasks that can be added to LocalAI Bench. The first version of LocalAI Bench will contain 3 default categories:

- Coding specific to User Interface (Vision)
  - Example tasks: Implement change in the  UI components based on the user graphical instructions.
- Corporate Document Understanding
  - Example tasks: Extract information from invoices in specific format; summarize legal documents; classify internal documents based on few examples.
- Agentic usage in recruitment process
  - Example tasks: Automate candidate screening workflows; generate personalized 
    candidate feedback.


## Scoring
For each category, there are multiple tasks with different complexity levels and scoring criteria.
Scoring criteria now include:
- Time Score: Time taken to complete the task, normalized in the range [0.8, 1.2].
- Quality Score: How good the solution is based on user judgment or provided ground truth (scale 1 to 10).
- Complexity Score: Complexity of the task (scale 1 to 5).
- Cost Factor: A normalized metric representing the cost of executing the task.
- Memory Usage Factor: A normalized metric measuring memory consumption.

Configurable weights allow users to prioritize components for every task/category. A proposed formula is:

Ultimate Score = (Time Score * w_time) *
                 (Quality Score * w_quality) *
                 (Complexity Score * w_complexity) *
                 (Cost Factor * w_cost) *
                 (Memory Usage Factor * w_memory)

Users can adjust the weights (w_time, w_quality, w_complexity, w_cost, w_memory)
to tailor the scoring model based on operational and resource constraints.

### Dashboard
The dashboard provides a summary of the scores for each model in each category. It also provides a detailed view of the scores for each task in each category. #TODO



## Quick Start

### Clone the repository
```bash
git clone https://github.com/dev-it-with-me/LocalAI_Bench
cd localai-bench
```

### Installation using uv
```bash
uv sync
```

### Installation using pip
```bash
pip install -r requirements.txt
```


## Supported Models
### Hugging Face
#TODO

#### Adding new model
#TODO


### API Providers
#TODO
