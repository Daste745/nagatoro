from __future__ import annotations

from dataclasses import dataclass

from discord import AllowedMentions, Intents


@dataclass
class Config:
    _intents: Intents
    _allowed_mentions: AllowedMentions
    _extension_package: str | None
    _extensions: list[str]

    @classmethod
    def default(cls) -> Config:
        return cls(
            _intents=Intents.default(),
            _allowed_mentions=AllowedMentions.none(),
            _extension_package=None,
            _extensions=[],
        )

    def intents(self, value: Intents) -> Config:
        self._intents = value
        return self

    def allowed_mentions(self, value: AllowedMentions) -> Config:
        self._allowed_mentions = value
        return self

    def extension_package(self, value: str) -> Config:
        self._extension_package = value
        return self

    def extension(self, value: str) -> Config:
        if value.startswith(".") and self._extension_package is None:
            raise ValueError("Cannot use relative extension module without a package.")

        self._extensions.append(value)
        return self
