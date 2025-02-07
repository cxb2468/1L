from dataclasses import dataclass


@dataclass
class Article:
    date: str
    link: str
    title: str

    def __str__(self) -> str:
        return f'{self.date} {self.link} {self.title}'

    def __eq__(self, value: object) -> bool:
        return self.date == value.date and self.link == value.link and self.title == value.title
