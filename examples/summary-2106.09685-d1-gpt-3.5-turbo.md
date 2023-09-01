# LoRA: Low-Rank Adaptation of Large Language Models

## Introduction

The section introduces the concept of adapting pre-trained language models to multiple downstream applications. It highlights the challenge of fine-tuning, which updates all parameters of the pre-trained model and increases the number of parameters in the new model. This challenge becomes critical for large models like GPT-3 with 175 billion trainable parameters. Existing techniques that adapt only some parameters or learn external modules for new tasks often introduce latency or fail to match the performance of fine-tuning. The section introduces Low-Rank Adaptation (LoRA) as a solution that optimizes rank decomposition matrices of dense layers' change during adaptation while keeping the pre-trained weights frozen. LoRA is shown to be storage- and compute-efficient, allowing for efficient task-switching and reducing the hardware barrier to entry. It introduces several advantages, including no inference latency, compatibility with other methods, and efficient training with adaptive optimizers. The section also provides terminologies and conventions used in the discussion.

## Problem Statement

The problem statement focuses on language modeling as a use case and discusses the maximization of conditional probabilities given a task-specific prompt. It introduces a pre-trained autoregressive language model and explains how it can be adapted to downstream conditional text generation tasks. The model is fine-tuned by updating its weights through gradient optimization. However, a drawback of full fine-tuning is that it requires learning a different set of parameters for each downstream task, which can be challenging and inefficient for large pre-trained models. To address this, the paper proposes a more parameter-efficient approach where a smaller set of parameters is used to encode the task-specific parameter increment. This approach involves optimizing over these smaller parameters to find the optimal parameter increment. The subsequent sections of the paper will discuss the use of a low-rank representation to encode this parameter increment in a compute- and memory-efficient manner.

## Aren't Existing Solutions Good Enough?

The section discusses the limitations of existing solutions for efficient model adaptation in transfer learning. It mentions two strategies: adding adapter layers and optimizing input layer activations. However, both strategies have their limitations, especially in large-scale and latency-sensitive production scenarios. 

The use of adapter layers introduces inference latency, even with a small bottleneck dimension. This is because adapter layers have to be processed sequentially, which affects online inference with small batch sizes. The section provides a table showing the increase in latency when using adapter layers in a specific scenario.

The other strategy, optimizing the prompt (as seen in prefix tuning), also faces challenges. It is difficult to optimize and its performance changes non-monotonically with trainable parameters. Additionally, reserving a part of the sequence length for adaptation reduces the sequence length available for processing downstream tasks.

Overall, existing solutions for efficient model adaptation have limitations in terms of latency and optimization challenges.

## Our Method

The section describes the method called LoRA, which is a technique used to reduce the number of trainable parameters in neural networks. It focuses on dense layers in deep learning models, specifically in Transformer language models. LoRA uses low-rank parametrized update matrices to represent weight updates during adaptation. It decomposes the weight matrix into two matrices, B and A, with a low rank. During training, the original weight matrix is frozen, and only B and A are updated. This reparametrization helps reduce the need to retune hyperparameters when varying the rank. LoRA is a generalization of full fine-tuning, allowing the training of a subset of pre-trained parameters. It does not introduce additional inference latency during deployment and can be applied to different weight matrices in a neural network. LoRA provides practical benefits such as reduced memory usage, faster training speed, and easier task switching during deployment. However, it also has limitations when batching inputs for different tasks with different matrices.

## Related Works

The section discusses various related works in the field of Transformer language models, prompt engineering and fine-tuning, parameter-efficient adaptation, and low-rank structures in deep learning.

- Transformer Language Models: The section mentions that Transformer is a popular architecture for language models and has been applied to autoregressive language modeling. Transformer-based language models like BERT and GPT-2 have achieved state-of-the-art performance in many NLP tasks. GPT-3 is the largest Transformer language model trained to-date.

- Prompt Engineering and Fine-Tuning: The section highlights that the behavior of GPT-3 depends heavily on the input prompt. Prompt engineering or prompt hacking is the empirical art of composing and formatting the prompt to maximize the model's performance on a desired task. Fine-tuning involves retraining a pre-trained model on specific tasks. However, fine-tuning GPT-3 175B is challenging due to its size.

- Parameter-Efficient Adaptation: The section mentions the use of adapter layers in neural networks to achieve parameter-efficient adaptation. The proposed method uses a bottleneck structure to impose a low-rank constraint on weight updates. The learned weights can be merged with the main weights during inference without introducing latency. Other methods like \textsc{compacter} and

## Understanding the Low-Rank Updates

The section discusses the properties of low-rank adaptation learned from downstream tasks in the context of pre-trained language models. The authors aim to explain the advantages of low-rank adaptation and its relationship with the pre-trained weights. They focus on GPT-3 175B and perform empirical studies to answer questions related to weight matrices, optimal rank, and the relationship between the adaptation matrix and the pre-trained weights. The results show that adapting both $W_q$ and $W_v$ yields the best performance, a small rank is sufficient for adaptation, and the adaptation matrix amplifies features that are not emphasized in the pre-trained weights. These findings provide insights into using pre-trained language models for downstream tasks in NLP.

## Conclusion and Future Work

The section discusses the conclusion and future work related to the proposed LoRA adaptation strategy for language models. It highlights that fine-tuning large language models is expensive in terms of hardware and storage costs. LoRA is presented as an efficient strategy that maintains high model quality without introducing latency or reducing input sequence length. It enables quick task-switching by sharing most of the model parameters. The principles of LoRA can be applied to other neural networks with dense layers as well.

The future work includes exploring the combination of LoRA with other efficient adaptation methods for potential improvement. The mechanism behind fine-tuning or LoRA is not well understood, and the authors suggest that LoRA could provide insights into this process. They also mention the need for more principled approaches to select weight matrices for applying LoRA. Additionally, the rank-deficiency of certain variables suggests potential avenues for further research and inspiration.
