from src.services.agent import Agent


class Article(Agent):
    prompt = "Сгенерируй статью с названием: {title}. Первый абзац должен быть " \
             "кратким описанием - сводка, самостоятельный абзац. " \
             "Со следующего абзаца должна начинаться статья без контекста сводки. "\
             "Вначале и в конце не должно быть никаких утверждений и вопросов, помимо статьи."\
             "Статья должна быть на русском языке."

    def generate(self, title: str) -> str:
        return self.msg(Article.prompt.format(title=title))

article = Article().generate("Баг 2000")
[print(s) for s in article.split("\n")]