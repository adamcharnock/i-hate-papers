# LoRA: Low-Rank Adaptation of Large Language Models

## Introduction

The section discusses the challenges of adapting large-scale pre-trained language models to multiple downstream applications. Fine-tuning, which updates all the parameters of the pre-trained model, results in a new model with as many parameters as the original model. This becomes a critical deployment challenge for models with a large number of parameters. Existing techniques that adapt only some parameters or learn external modules for new tasks often introduce latency and fail to match the performance of fine-tuning. 

The proposed approach, called Low-Rank Adaptation (LoRA), is inspired by the low intrinsic dimension of over-parametrized models. LoRA trains dense layers indirectly by optimizing rank decomposition matrices of the dense layers' change during adaptation while keeping the pre-trained weights frozen. This approach is storage- and compute-efficient, even for models with a high number of parameters. 

LoRA has several advantages, including the ability to share a pre-trained model and build small LoRA modules for different tasks, making task-switching more efficient. It also lowers the hardware barrier to entry and introduces no inference latency compared to fully fine-tuned models. LoRA can be combined with other methods, such as prefix-tuning. 

The section also introduces terminologies and conventions used in the discussion, including dimensions of the Transformer architecture, projection

## Problem Statement

The problem statement focuses on language modeling as a use case for the proposal. It describes the task of adapting a pre-trained language model to downstream tasks such as summarization, machine reading comprehension, and natural language to SQL. The model is initialized with pre-trained weights and updated through fine-tuning to maximize the conditional language modeling objective. However, a drawback of full fine-tuning is that it requires learning a different set of parameters for each downstream task, which can be challenging and inefficient for large pre-trained models. The paper proposes a more parameter-efficient approach where a smaller set of parameters is used to encode the task-specific parameter increment. This approach involves optimizing over these smaller parameters to find the optimal parameter increment. The subsequent sections of the paper will discuss using a low-rank representation to encode this parameter increment, which is both computationally and memory-efficient.

## Aren't Existing Solutions Good Enough?

The section discusses the limitations of existing solutions for efficient model adaptation in transfer learning. It mentions two strategies: adding adapter layers and optimizing input layer activations. However, both strategies have their limitations, especially in large-scale and latency-sensitive production scenarios.

The use of adapter layers introduces inference latency, even with a small bottleneck dimension. This is because adapter layers have to be processed sequentially, which affects online inference with small batch sizes. The section provides a table showing the increase in latency when using adapters in a specific scenario.

Another strategy, prefix tuning, faces challenges in optimization and performance. It is difficult to optimize and its performance changes non-monotonically with trainable parameters. Additionally, reserving a part of the sequence length for adaptation reduces the sequence length available for downstream tasks, which may affect the performance of tuning the prompt.

Overall, existing solutions have limitations in terms of inference latency and optimization challenges, particularly in large-scale and latency-sensitive scenarios.

## Our Method

The section describes the method called LoRA (Low-Rank-Parametrized Update Matrices) and its practical benefits. LoRA is a technique that reduces the number of trainable parameters in neural networks by using low-rank decompositions for weight matrices. The authors hypothesize that the updates to the weights during adaptation also have a low "intrinsic rank." They propose representing the weight updates as a low-rank decomposition and introduce trainable parameters for the decomposition. The section also explains how LoRA can be applied to Transformer models and discusses the practical benefits and limitations of using LoRA, such as reduced memory usage, faster training, and easier task switching.

## Related Works

The section discusses various related works in the field of transformer language models, prompt engineering and fine-tuning, parameter-efficient adaptation, and low-rank structures in deep learning. 

- Transformer Language Models: Transformer is a popular architecture for language models that use self-attention. Transformer-based language models, such as BERT and GPT-2, have achieved state-of-the-art performance in many natural language processing tasks. GPT-3 is the largest Transformer language model to date.

- Prompt Engineering and Fine-Tuning: GPT-3's performance depends heavily on the input prompt, leading to the need for prompt engineering or prompt hacking. Fine-tuning involves retraining a pre-trained model on specific tasks. However, fine-tuning GPT-3 is challenging due to its size and memory requirements.

- Parameter-Efficient Adaptation: Some approaches propose using adapter layers or low-rank constraints to efficiently adapt neural networks. The authors' method uses a bottleneck structure with low-rank weight updates that can be merged with the main weights during inference.

- Low-Rank Structures in Deep Learning: Low-rank structures are common in machine learning and deep learning tasks. Prior works have imposed low-rank constraints during training, but none have considered low-rank updates for adaptation to

## Understanding the Low-Rank Updates

The section discusses the properties and effects of low-rank updates in pre-trained language models. The authors aim to explain the benefits and interpretability of low-rank adaptation learned from downstream tasks. They focus on the GPT-3 175B model and conduct empirical studies to answer several questions. These questions include determining which weight matrices in the pre-trained Transformer should be adapted to maximize performance, the optimal rank for low-rank adaptation, and the relationship between the adaptation matrix and the pre-trained weights. The results show that adapting both $W_q$ and $W_v$ yields the best performance, a small rank is sufficient for adaptation, and the adaptation matrix amplifies features that are not emphasized in the pre-trained weights. These findings provide insights into using pre-trained language models for downstream tasks.

## Conclusion and Future Work

The section discusses the conclusion and future work related to the proposed LoRA adaptation strategy for language models. It highlights that fine-tuning large language models is expensive in terms of hardware and storage costs. LoRA is presented as an efficient strategy that maintains model quality without introducing latency or reducing input sequence length. It enables quick task-switching by sharing most of the model parameters. The principles of LoRA can be applied to any neural networks with dense layers, not just Transformer language models.

The future work suggestions include:
1) Combining LoRA with other efficient adaptation methods for potential improvement.
2) Exploring the mechanism behind fine-tuning and LoRA to understand how pre-training features are transformed for downstream tasks.
3) Seeking more principled ways to select weight matrices for applying LoRA instead of relying on heuristics.
4) Investigating the rank-deficiency of weight matrices and its potential implications for future research.

## Glossary (Generated)

This glossary has been generated based on the terminology used in the summarised content above.

**LoRA**: Low-Rank Adaptation of Large Language Models

**Fine-tuning**: Updating all parameters of a pre-trained model to create a new model with as many parameters as the original model.

**Latency**: The time delay between the initiation and execution of a task.

**Rank decomposition**: Representing a matrix as a product of two or more matrices with lower ranks.

**Storage-efficient**: Using minimal storage space.

**Compute-efficient**: Requiring minimal computational resources.

**Task-switching**: The ability to switch between different tasks efficiently.

**Prefix-tuning**: A method that reserves a part of the sequence length for adaptation in language models.

**Inference latency**: The delay in processing and generating predictions during inference.

**Adapter layers**: Additional layers added to a pre-trained model for adapting it to new tasks.

**Bottleneck dimension**: The dimensionality reduction applied to the input data in adapter layers.

**Optimization challenges**: Difficulties in finding the optimal values for trainable parameters.

**Non-monotonically**: Not following a consistent pattern or trend.

**Sequence length**: The number of tokens or elements in a sequence.

**Prompt engineering**: Techniques used to optimize the input prompt for language models.

**Parameter-efficient adaptation**: Approaches that aim to reduce the number of trainable parameters in neural networks during adaptation.

**Low-rank structures**: Matrix structures that have low-rank constraints imposed during training.

**Interpretability**: The ability to understand and explain the behavior and results of a model.

**Empirical studies**: Research conducted through observation and experimentation rather than theoretical analysis.

**Model quality**: The performance and effectiveness of a model in producing accurate results.

**Input sequence length**: The length of the input data provided to a model.

**Future work suggestions**: Areas for further research and exploration related to the proposed method.

# About this summary

| Argument | Value |
| -- | -- |
| INPUT | 2106.09685 |
| verbosity | 1 |
| no_input | False |
| no_html | False |
| no_open | False |
| no_footer | False |
| no_glossary | False |
| detail_level | 1 |
| model | gpt-3.5-turbo-16k |

Summary was created at `2023-09-02T14:37:31.081644+00:00`

