from dataclasses import dataclass


@dataclass(frozen=True)
class HadithAPIConfig:
    api_version: str = "1"
    edition: str = "eng-bukhari"
    endpoint_root: str = "https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api"

    @property
    def edition_min_url(self) -> str:
        return (
            f"{self.endpoint_root}@{self.api_version}/editions/{self.edition}.min.json"
        )

    @property
    def edition_url(self) -> str:
        return f"{self.endpoint_root}@{self.api_version}/editions/{self.edition}.json"

    @property
    def info_min_url(self) -> str:
        return f"{self.endpoint_root}@{self.api_version}/info.min.json"

    @property
    def info_url(self) -> str:
        return f"{self.endpoint_root}@{self.api_version}/info.json"

