# Agent基类 - 所有Agent的父类

from abc import ABC, abstractmethod
from typing import Optional


class BaseAgent(ABC):
    """Agent基类"""

    def __init__(self):
        self.name = self.__class__.__name__

    @abstractmethod
    async def execute(self, input_data: dict) -> dict:
        """
        执行Agent任务
        - input_data: 输入数据
        - 返回: 执行结果
        """
        pass

    def log(self, message: str):
        """记录日志"""
        print(f"[{self.name}] {message}")
