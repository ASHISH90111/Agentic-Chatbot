from tavily import TavilyClient
from langchain_core.prompts import ChatPromptTemplate
import os


class AINewsNode:

    def __init__(self, llm):
        self.tavily = TavilyClient(
            api_key=os.getenv("TAVILY_API_KEY")
        )
        self.llm = llm

    def fetch_news(self, state: dict) -> dict:

        frequency = state['messages'][0].content.lower()

        # ADD THIS LINE
        state['frequency'] = frequency

        time_range_map = {
            'daily': 'd',
            'weekly': 'w',
            'monthly': 'm',
            'year': 'y'
        }

        response = self.tavily.search(
            query="Top Artificial Intelligence (AI) technology news India and globally",
            topic="news",
            time_range=time_range_map[frequency],
            include_answer="advanced",
            max_results=20
        )

        state['news_data'] = response.get('results', [])

        return state

    def summarize_news(self, state: dict) -> dict:

        news_items = state['news_data']

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """Summarize AI news articles into markdown format. For each item include:
            - Date in **YYYY-MM-DD** format in IST timezone
            - Concise sentences summary from latest news
            - Sort news by date wise (latest first)
            - Source URL as link

            Use format:
            ### [Date]
            - [Summary](URL)"""),

            ("user", "Articles:\n{articles}")
        ])

        articles_str = "\n\n".join([
            f"Content: {item.get('content', '')}\n"
            f"URL: {item.get('url', '')}\n"
            f"Date: {item.get('published_date', '')}"
            for item in news_items
        ])

        response = self.llm.invoke(
            prompt_template.format(articles=articles_str)
        )

        state['summary'] = response.content

        return state

    def save_result(self, state):

        frequency = state['frequency']
        summary = state['summary']

        # Project root: agentic_chatbot
        project_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../../")
        )

        news_folder = os.path.join(project_root, "AINews")

        os.makedirs(news_folder, exist_ok=True)

        filename = os.path.join(
            news_folder,
            f"{frequency}_summary.md"
        )

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# {frequency.capitalize()} AI News Summary\n\n")
            f.write(summary)

        state['filename'] = filename

        return state