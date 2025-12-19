import os
from langchain.chat_models import init_chat_model
from typing import Dict, Optional

TIME_OUT = 60 * 6


class LlmFactory:
    """LLM管理器，单例模式，用于管理和获取不同的语言模型"""

    _instance: Optional["LlmFactory"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self._models: Dict = {}
        self._configs = {
            "doubao_seed_medium": {
                "model": "doubao-seed-1-6-251015",
                "model_provider": "openai",
                "temperature": 0,
                "base_url": os.getenv("DOUBAO_BASEURL"),
                "api_key": os.getenv("DOUBAO_APIKEY_FS_AGENT"),
                "max_completion_tokens": 64000,
                "extra_body": {"thinking": {"type": "enabled"}},
                "reasoning_effort": "medium",
                "timeout": TIME_OUT,
            },
            "doubao_seed_low": {
                "model": "doubao-seed-1-6-251015",
                "model_provider": "openai",
                "temperature": 0,
                "base_url": os.getenv("DOUBAO_BASEURL"),
                "api_key": os.getenv("DOUBAO_APIKEY_FS_AGENT"),
                "max_completion_tokens": 64000,
                "extra_body": {"thinking": {"type": "enabled"}},
                "reasoning_effort": "low",
                "timeout": TIME_OUT,
            },
            "doubao_seed_low_auth": {
                "model": "doubao-seed-1-6-251015",
                "model_provider": "openai",
                "temperature": 0,
                "base_url": os.getenv("DOUBAO_BASEURL"),
                "api_key": os.getenv("DOUBAO_APIKEY_FS_AUTH"),
                "max_completion_tokens": 64000,
                "extra_body": {"thinking": {"type": "enabled"}},
                "reasoning_effort": "low",
                "timeout": TIME_OUT,
            },
            "doubao_flash": {
                "model": "doubao-seed-1-6-flash",
                "model_provider": "openai",
                "temperature": 0,
                "base_url": os.getenv("DOUBAO_BASEURL"),
                "api_key": os.getenv("DOUBAO_APIKEY_FS_AGENT"),
                "max_completion_tokens": 64000,
                "timeout": TIME_OUT,
            },
            "doubao_lite_medium": {
                "model": "doubao-seed-1-6-lite-251015",
                "model_provider": "openai",
                "temperature": 0,
                "base_url": os.getenv("DOUBAO_BASEURL"),
                "api_key": os.getenv("DOUBAO_APIKEY_FS_AGENT"),
                "max_completion_tokens": 64000,
                "reasoning_effort": "medium",
                "timeout": TIME_OUT,
            },
            "doubao_lite_low": {
                "model": "doubao-seed-1-6-lite-251015",
                "model_provider": "openai",
                "temperature": 0,
                "base_url": os.getenv("DOUBAO_BASEURL"),
                "api_key": os.getenv("DOUBAO_APIKEY_FS_AGENT"),
                "max_completion_tokens": 64000,
                "reasoning_effort": "low",
                "timeout": TIME_OUT,
            },
            "doubao_flash_auth": {
                "model": "doubao-seed-1-6-flash",
                "model_provider": "openai",
                "temperature": 0,
                "base_url": os.getenv("DOUBAO_BASEURL"),
                "api_key": os.getenv("DOUBAO_APIKEY_FS_AUTH"),
                "max_completion_tokens": 64000,
                "timeout": TIME_OUT,
            },
            "doubao_lite_medium_auth": {
                "model": "doubao-seed-1-6-lite-251015",
                "model_provider": "openai",
                "temperature": 0,
                "base_url": os.getenv("DOUBAO_BASEURL"),
                "api_key": os.getenv("DOUBAO_APIKEY_FS_AUTH"),
                "max_completion_tokens": 64000,
                "reasoning_effort": "medium",
                "timeout": TIME_OUT,
            },
            "doubao_lite_low_auth": {
                "model": "doubao-seed-1-6-lite-251015",
                "model_provider": "openai",
                "temperature": 0,
                "base_url": os.getenv("DOUBAO_BASEURL"),
                "api_key": os.getenv("DOUBAO_APIKEY_FS_AUTH"),
                "max_completion_tokens": 64000,
                "reasoning_effort": "low",
                "timeout": TIME_OUT,
            },
            "gpt_medium": {
                "model": "gpt-5",
                "model_provider": "openai",
                "temperature": 0,
                "base_url": os.getenv("BASEURL_FS"),
                "api_key": os.getenv("OPENAI_APIKEY_FS"),
                "reasoning_effort": "medium",
                "timeout": TIME_OUT,
            },
            "gpt_low": {
                "model": "gpt-5",
                "model_provider": "openai",
                "temperature": 0,
                "base_url": os.getenv("BASEURL_FS"),
                "api_key": os.getenv("OPENAI_APIKEY_FS"),
                "reasoning_effort": "low",
                "timeout": TIME_OUT,
            },
            "qwen_max": {
                "model": "qwen3-max-preview",
                "model_provider": "openai",
                "temperature": 0,
                "base_url": os.getenv("QWEN_BASEURL"),
                "api_key": os.getenv("QWEN_APIKEY_FS"),
                "extra_body": {"enable_thinking": True},
                "stream": True,
                "timeout": TIME_OUT,
            },
            "qwen_plus": {
                "model": "qwen-plus",
                "model_provider": "openai",
                "temperature": 0,
                "base_url": os.getenv("QWEN_BASEURL"),
                "api_key": os.getenv("QWEN_APIKEY_FS"),
                "extra_body": {"enable_thinking": True},
                "stream": True,
                "timeout": TIME_OUT,
            },
            "qwen_flash": {
                "model": "qwen-flash",
                "model_provider": "openai",
                "temperature": 0,
                "base_url": os.getenv("QWEN_BASEURL"),
                "api_key": os.getenv("QWEN_APIKEY_FS"),
                "extra_body": {"enable_thinking": True},
                "stream": True,
                "extra_headers": {
                    "X-DashScope-DataInspection": '{"input":"disable","output":"disable"}'
                },
                "timeout": TIME_OUT,
            },
        }

    def __getitem__(self, model_name: str):
        """通过模型名获取对应的模型实例"""
        if model_name not in self._models:
            if model_name not in self._configs:
                raise KeyError(f"Model '{model_name}' not found in configurations")
            self._models[model_name] = init_chat_model(**self._configs[model_name])
        return self._models[model_name]

    def get_config(self, model_name: str) -> dict:
        """获取模型配置"""
        return self._configs.get(model_name, {})


# 创建单例实例
llm_manager = LlmFactory()
