from pathlib import Path
from typing import List, Self, Type
from pydantic import BaseModel, Field, model_validator
from langchain_core.runnables import Runnable
from cetc_product.tools.chain_tool import MyChain
from cetc_product.tools.IO_tool import enhance_outpath, enhance_inpath


class IoParams(BaseModel):
    inpath: Path = Field(..., description="输入数据路径，支持通配符")
    read_batch_size: int = Field(..., description="读取的批次大小")
    outpath: Path = Field(..., description="输出数据的原始配置路径")

    outpath_with_now: Path | None = Field(None, description="输出数据的原始配置路径")

    @model_validator(mode="after")
    def _enhance_outpath(self) -> Self:
        """实例化时计算，之后不再改变"""
        self.outpath_with_now = enhance_outpath(self.outpath)
        return self

    @property
    def inpaths(self) -> List[Path]:
        return enhance_inpath(self.inpath)


class ChainParams(BaseModel):
    llm_name: str = Field(..., description="使用的语言模型名称")
    prompt_path: Path = Field(..., description="Prompt模板路径")
    data_model: Type[BaseModel] = Field(..., description="数据模型，用于结构化输出")
    _chain: Runnable | None = None  # 添加缓存字段

    @property
    def chain(self) -> Runnable:
        if self._chain is None:
            self._chain = MyChain(self.prompt_path, self.data_model, self.llm_name)
        return self._chain
