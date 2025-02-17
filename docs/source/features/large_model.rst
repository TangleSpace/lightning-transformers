.. _large_model:

Big Transformers Model Inference
================================

Lightning Transformers provides out of the box support for running inference with very large billion parameter models. Under-the-hood we use HF Accelerates' Transformer support to auto-select devices for optimal throughput and memory usage.

Below is an example of how you can run generation with a large 6B parameter transformer model using Lightning Transformers.


.. code-block:: bash

   pip install accelerate

.. code-block:: python

    import torch
    from accelerate import init_empty_weights
    from transformers import AutoTokenizer

    from lightning_transformers.task.nlp.language_modeling import LanguageModelingTransformer

    with init_empty_weights():
        model = LanguageModelingTransformer(
            pretrained_model_name_or_path="EleutherAI/gpt-j-6B",
            tokenizer=AutoTokenizer.from_pretrained("EleutherAI/gpt-j-6B"),
            low_cpu_mem_usage=True,
            device_map="auto"
        )

    output = model.generate("Hello, my name is", device=torch.device("cuda"))
    print(model.tokenizer.decode(output[0].tolist()))


This will allow the model to be split onto GPUs/CPUs and even kept onto Disk to optimize memory space.

Inference with Manual Checkpoints
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Download the sharded checkpoint weights that we'll be using:

.. code-block:: bash

   git clone https://huggingface.co/sgugger/sharded-gpt-j-6B
   cd sharded-gpt-j-6B
   git-lfs install
   git pull


.. code-block:: python

   import torch
   from accelerate import init_empty_weights
   from transformers import AutoTokenizer

   from lightning_transformers.task.nlp.language_modeling import LanguageModelingTransformer

   # initializes empty model for us to the load the checkpoint.
   with init_empty_weights():
      model = LanguageModelingTransformer(
      pretrained_model_name_or_path="EleutherAI/gpt-j-6B",
      tokenizer=AutoTokenizer.from_pretrained("EleutherAI/gpt-j-6B")
    )

   # automatically selects the best devices (cpu/gpu) to load model layers based on available memory
   model.load_checkpoint_and_dispatch("sharded-gpt-j-6B", device_map="auto", no_split_module_classes=["GPTJBlock"])

   output = model.generate("Hello, my name is", device=torch.device("cuda"))
   print(model.tokenizer.decode(output[0].tolist()))


To see more details about the API, see `here <https://huggingface.co/docs/accelerate/big_modeling>`__.
