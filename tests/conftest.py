import os
from pathlib import Path

import pytest
from hydra.experimental import compose, initialize
from hydra.test_utils.test_utils import find_parent_dir_containing

from cli import main

# GitHub Actions use this path to cache datasets.
# Use `datadir` fixture where possible and use `DATASETS_PATH` in
# `pytest.mark.parametrize()` where you cannot use `datadir`.
# https://github.com/pytest-dev/pytest/issues/349
from tests import CACHE_PATH


@pytest.fixture(scope="session")
def datadir():
    return Path(CACHE_PATH)


def find_hydra_conf_dir(config_dir="conf"):
    """
    Util function to find the hydra config directory from the main repository for testing.
    Args:
        config_dir: Name of config directory.

    Returns: Relative config path

    """
    parent_dir = find_parent_dir_containing(config_dir)
    relative_conf_dir = os.path.relpath(parent_dir, os.path.dirname(__file__))
    return os.path.join(relative_conf_dir, config_dir)


@pytest.fixture
def hydra_runner():

    def run(task: str, dataset: str, suffix: str = ""):
        cmd_line = f"+task={task} +dataset={dataset} trainer.fast_dev_run=True " + suffix
        relative_conf_dir = find_hydra_conf_dir()
        with initialize(config_path=relative_conf_dir, job_name="test_app"):
            cfg = compose(config_name="config", overrides=cmd_line.split(" "))
            main(cfg)

    return run


@pytest.fixture()
def hf_runner(hydra_runner, datadir):
    cache_dir: Path = datadir / "huggingface"

    def run(task: str, dataset: str, model: str, max_samples: int = 64):
        suffix = f'backbone.pretrained_model_name_or_path={model} ' \
                 f'dataset.cfg.limit_train_samples={max_samples} ' \
                 f'dataset.cfg.limit_val_samples={max_samples} ' \
                 f'dataset.cfg.limit_test_samples={max_samples} ' \
                 f'dataset.cfg.cache_dir={cache_dir}'
        hydra_runner(task=f'nlp/huggingface/{task}', dataset=f'nlp/{task}/{dataset}', suffix=suffix)

    return run
