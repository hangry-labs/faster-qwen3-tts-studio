"""Persisted operator defaults, independent of browser workflow selections."""
from pydantic import BaseModel, ConfigDict, Field, model_validator
from .model_catalog import MODELS

DEFAULT_MODELS = {
    'custom': 'Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice',
    'clone': 'Qwen/Qwen3-TTS-12Hz-0.6B-Base',
    'design': 'Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign',
}


class WorkflowPolicy(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    model: str
    keep_loaded: bool = True


class ModelPolicy(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    enabled: bool = True
    workflows: dict[str, WorkflowPolicy] = Field(default_factory=lambda: {
        mode: WorkflowPolicy(model=model) for mode, model in DEFAULT_MODELS.items()})

    @model_validator(mode='after')
    def validate_workflows(self):
        if set(self.workflows) != set(DEFAULT_MODELS):
            raise ValueError('Configure Generate, Clone and Design workflows.')
        for mode, choice in self.workflows.items():
            if choice.model not in MODELS or MODELS[choice.model]['mode'] != mode:
                raise ValueError(f'Choose a compatible model for {mode}.')
        return self

    @property
    def resident_models(self):
        return {choice.model for choice in self.workflows.values() if self.enabled and choice.keep_loaded}
